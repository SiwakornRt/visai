import datetime

from influxdb_client import InfluxDBClient, Point, Dialect
from influxdb_client.client.write_api import SYNCHRONOUS

from . import hosts


class InfluxDBClientProxy:
    def __init__(self, url: str = "", token: str = "", org: str = "", bucket=""):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.app = None

        if url and token and org:
            self.initial()

    def init_app(self, app):
        self.app = app
        self.url = app.config.get("INFLUXDB_V2_URL", "http://localhost:8086")
        self.org = app.config.get("INFLUXDB_V2_ORG", "")
        self.token = app.config.get("INFLUXDB_V2_TOKEN", "")
        self.bucket = app.config.get("INFLUXDB_V2_BUCKET", "DIIS")
        self.initial()

    def initial(self):
        self.influx_client = InfluxDBClient(
            url=self.url, token=self.token, org=self.org
        )

        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.influx_client.query_api()

        self.init_entities()

    def init_entities(self):
        self.hosts = hosts.HostManager(
            self.influx_client, self.write_api, self.query_api, self.bucket
        )


client = InfluxDBClientProxy()
