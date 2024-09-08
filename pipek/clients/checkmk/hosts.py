import datetime
from werkzeug.exceptions import Unauthorized, Forbidden

import httpx
import json

from . import base


from enum import Enum


class HostState(Enum):
    UP = 0
    DOWN = 1
    UNREACH = 3


class Host(base.BasedAPI):
    def get_host_configs(self):
        endpoint = "/domain-types/host_config/collections/all"
        params = {
            #           "query": json.dumps(query),
            "columns": [
                #    "name",
                #     "total_services",
                #     "groups",
                #     "state",
                #     "last_check",
                #     "services_with_state",
            ],
        }

        return self.get(endpoint, params=params)

    def get_hosts(self):
        endpoint = "/domain-types/host/collections/all"
        query = {
            "op": "and",
            "expr": [
                # {"op": "=", "left": "name", "right": host_name},
                # {"op": "!=", "left": "state", "right": "1"},
            ],
        }

        params = {
            # "query": json.dumps(query),
            "columns": [
                "name",
                "total_services",
                "state",
                "last_check",
                "last_time_up",
                "last_time_down",
                "last_state_change",
                "downtimes_with_info",
                "address",
                "groups",
                "tags",
                "labels",
                "check_interval",
                "services_with_fullstate",
            ],
        }

        return self.get(endpoint, params=params)

    def get_host_status(self, host_name: str):
        endpoint = "/domain-types/host/collections/all"
        url = f"{self.based_api_url}{endpoint}"
        query = {
            "op": "and",
            "expr": [
                {"op": "=", "left": "name", "right": host_name},
                # {"op": "!=", "left": "state", "right": "1"},
            ],
        }

        params = {
            "query": json.dumps(query),
            "columns": [
                "name",
                "total_services",
                "groups",
                "state",
                "last_check",
                "services_with_state",
            ],
        }
        print("params", params)

        response = self.get(url, params=params)
        if response.status_code == 200:
            return response.json()

        return {}
