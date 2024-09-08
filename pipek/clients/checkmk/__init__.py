import datetime

import httpx

from . import hosts
from . import host_groups
from . import services
from . import events


class CheckmkClient:
    def __init__(
        self,
        username: str = "",
        password: str = "",
        base_api_url: str = "",
        verify_ssl=False,
    ):
        self.base_api_url = base_api_url
        self.verify_ssl = verify_ssl
        self.username = username
        self.password = password
        self.timeout = 30
        self.tokens = {}
        self.app = None
        self.http_client = httpx.Client()

        self.update_headers()

        self.hosts = hosts.Host(self.http_client, self.base_api_url)
        self.host_groups = host_groups.HostGroup(self.http_client, self.base_api_url)
        self.events = events.Event(self.http_client, self.base_api_url)
        self.services = services.Service(self.http_client, self.base_api_url)

    def init_app(self, app):
        self.base_api_url = app.config.get("CHECKMK_BASE_API_URL")
        self.verify_ssl = app.config.get("CHECKMK_API_VERIFY_SSL", False)
        self.username = app.config.get("CHECKMK_USERNAME")
        self.password = app.config.get("CHECKMK_PASSWORD")

        self.update_headers()

        self.hosts.update_based_api_url(self.base_api_url)
        self.events.update_based_api_url(self.base_api_url)
        self.host_groups.update_based_api_url(self.base_api_url)
        self.services.update_based_api_url(self.base_api_url)

    def update_headers(self):
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Accept": "application/json",
        }
        self.http_client.headers.update(headers)

    def get_access_token(self):
        return f"{self.username} {self.password}"


client = CheckmkClient()
