import datetime
from werkzeug.exceptions import Unauthorized, Forbidden

import httpx
import json

from . import base


from enum import Enum


class ServiceState(Enum):
    UP = 0
    DOWN = 1
    UNREACH = 3


class Service(base.BasedAPI):
    def get_service_configs(self):
        endpoint = "/domain-types/service_config/collections/all"
        url = f"{self.based_api_url}{endpoint}"
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

        response = self.http_client.get(url, params=params)
        if response.status_code == 200:
            return response.json()

        return {}

    def get(self, service_name, host_name):
        endpoint = "/domain-types/service/collections/all"
        query = {
            "op": "and",
            "expr": [
                {"op": "=", "left": "host_name", "right": host_name},
                {"op": "=", "left": "description", "right": service_name},
            ],
        }

        params = {
            "host_name": host_name,
            "query": json.dumps(query),
            "columns": [
                "groups",
                "state",
                "last_check",
                "host_address",
                "last_time_critical",
                "last_state_change",
                "host_address",
            ],
        }
        return super().get(endpoint, params)

    def get_services(self):
        endpoint = "/domain-types/service/collections/all"
        query = {
            "op": "and",
            "expr": [
                # {"op": "=", "left": "host_name", "right": "lms.psu.ac.th"},
                # {"op": "!=", "left": "state", "right": "1"},
            ],
        }

        params = {
            # "query": json.dumps(query),
            "columns": [
                # "name",
                "groups",
                "state",
                "last_check",
                "host_address",
                "last_time_critical",
                "last_state_change",
                "host_address",
            ],
        }
        return self.get(endpoint, params)

    def get_service_status(self, service_name: str):
        endpoint = "/domain-types/service/collections/all"
        url = f"{self.based_api_url}{endpoint}"
        query = {
            "op": "and",
            "expr": [
                {"op": "=", "left": "name", "right": service_name},
                # {"op": "!=", "left": "state", "right": "1"},
            ],
        }

        params = {
            "query": json.dumps(query),
            "columns": [
                "name",
                # "total_services",
                # "groups",
                # "state",
                # "last_check",
                # "services_with_state",
            ],
        }
        print("params", params)

        response = self.http_client.get(url, params=params)
        if response.status_code == 200:
            return response.json()

        return {}
