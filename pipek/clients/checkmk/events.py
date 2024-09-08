from enum import Enum
import json

from . import base


class EventState(Enum):
    UP = 0
    DOWN = 1
    UNREACH = 3


class Event(base.BasedAPI):
    def get_event_configs(self):
        endpoint = "/domain-types/event_config/collections/all"
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

    def get_events(self):
        endpoint = "/domain-types/event_console/collections/all"
        # endpoint = "/objects/event_console/100"
        query = {
            "op": "and",
            "expr": [
                {"op": "=", "left": "name", "right": "dss.psu.ac.th"},
                {"op": "!=", "left": "state", "right": "0"},
            ],
        }

        params = {
            # "query": json.dumps(query),
            # "host": "dss.psu.ac.th",
            # "state": "ok",
            # "phase": "open",
            # "application": "app_1",
            # "columns":  [
            # "name",
            # "total_services",
            # "groups",
            # "state",
            # "last_check",
            # "services_with_state",
            # ],
        }

        return self.get(endpoint, params)

    def get_event_status(self, event_name: str):
        endpoint = "/domain-types/event/collections/all"
        url = f"{self.based_api_url}{endpoint}"
        query = {
            "op": "and",
            "expr": [
                {"op": "=", "left": "name", "right": event_name},
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

        return self.get(endpoint, params)
