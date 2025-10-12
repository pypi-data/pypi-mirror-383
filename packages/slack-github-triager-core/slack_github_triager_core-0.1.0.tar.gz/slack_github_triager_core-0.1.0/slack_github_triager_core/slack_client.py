import functools
import logging
import re
import time

import requests

logger = logging.getLogger(__name__)


################################################################################
# Helpers
################################################################################
@functools.lru_cache()
def get_slack_tokens(subdomain: str, d_cookie: str) -> tuple[str, str]:
    """
    Get session token and enterprise session tokenbased on the d cookie.
    https://papermtn.co.uk/retrieving-and-using-slack-cookies-for-authentication
    """
    response = requests.get(
        f"https://{subdomain}.slack.com",
        cookies={"d": d_cookie},
    )
    response.raise_for_status()

    match = re.search(r'"api_token":"([^"]+)"', response.text)
    if not match:
        raise ValueError("No api_token found in response")

    api_token = match.group(1)

    match = re.search(r'"enterprise_api_token":"([^"]+)"', response.text)
    if not match:
        raise ValueError("No enterprise_api_token found in response")

    enterprise_api_token = match.group(1)

    return api_token, enterprise_api_token




################################################################################
# Slack API Client
################################################################################


class SlackRequestError(Exception):
    pass


def _slack_raise_for_status(response: requests.Response):
    response.raise_for_status()
    if not response.json()["ok"]:
        logger.error(f"Slack request failed - Path: {response.request.path_url}, Body: {response.request.body}, Response: {response.text}")

        raise SlackRequestError("non-OK slack response")


class SlackRequestClient:
    def __init__(
        self,
        subdomain: str,
        token: str,
        cookie: str,
        use_bot: bool = False,
        enterprise_token: str | None = None,
    ):
        self.use_bot = use_bot
        self.subdomain = subdomain

        if not self.use_bot and not enterprise_token:
            raise ValueError("enterprise_token is required when user auth is used")

        self.enterprise_token = enterprise_token

        self.session = requests.session()

        if self.use_bot:
            self.session.headers["Authorization"] = f"Bearer {token}"
        else:
            self.session.cookies["d"] = cookie
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _make_slack_request(
        self, method: str, path: str, **kwargs
    ) -> requests.Response:
        assert path and path[0] == "/"

        if self.use_bot:
            url = f"https://slack.com{path}"
        else:
            url = f"https://{self.subdomain}.slack.com{path}"

        while True:
            response = self.session.request(method, url, **kwargs)
            try:
                _slack_raise_for_status(response)
                return response
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    retry_after = int(e.response.headers.get("Retry-After", 1))
                    logger.warning(
                        f"Rate limit hit. Retrying after {retry_after} seconds..."
                    )
                    time.sleep(retry_after)
                else:
                    raise

    def get(self, path: str, **kwargs) -> dict:
        return self._make_slack_request("GET", path, **kwargs).json()

    def paginated_get(self, path: str, **kwargs) -> dict:
        assert path and "?" in path

        response = self._make_slack_request("GET", path, **kwargs)

        while cursor := response.json().get("response_metadata", {}).get("next_cursor"):
            yield response.json()

            response = self._make_slack_request(
                "GET", f"{path}&cursor={cursor}", **kwargs
            )

        return response.json()

    def post(self, path: str, data: list[tuple], **kwargs) -> dict:
        if not self.use_bot:
            data.append(("token", self.enterprise_token))
        return self._make_slack_request("POST", path, data=data, **kwargs).json()
