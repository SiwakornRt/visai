from enum import Enum

from . import base


class HostGroup(base.BasedAPI):
    def get_host_groups(self):
        endpoint = "/domain-types/host_group_config/collections/all"
        params = {
            "columns": [
                "name",
                "num_hosts",
                "num_hosts_up",
                "num_services",
                "num_services_ok",
            ],
        }
        return self.get(endpoint, params)

    def get_host_group(self, name: str):
        endpoint = f"/objects/host_group_config/{name}"
        params = {
            "columns": [
                "name",
                "num_hosts",
                "num_hosts_up",
                "num_services",
                "num_services_ok",
            ],
        }
        return self.get(endpoint, params)
