import enum


HOST_STATES = ["up", "down", "unreach"]
SERVICE_STATES = ["up", "unreach", "down", "unknown"]


class HostManager:
    def __init__(self, influx_client, write_api, query_api, bucket):
        self.influx_client = influx_client
        self.bucket = bucket
        self.write_api = write_api
        self.query_api = query_api

        self.metric_states = dict(
            host=HOST_STATES,
            AP=SERVICE_STATES,
            AD=SERVICE_STATES,
            HTTP=SERVICE_STATES,
        )
        self.fluxs = dict(
            host="""
            from(bucket: "{bucket}")
            |> range({range_time})
            |> filter(fn: (r) => (r._measurement == "host"))
            |> filter(fn: (r) => r["_field"] == "state")
            {addition}
        """,
            AP="""
            from(bucket: "{bucket}")
            |> range({range_time})
            |> filter(fn: (r) => (r._measurement == "AP"))
            |> filter(fn: (r) => r["_field"] == "state")
            {addition}
        """,
            AD="""
            from(bucket: "{bucket}")
            |> range({range_time})
            |> filter(fn: (r) => (r._measurement == "service"))
            |> filter(fn: (r) => (r.name == "LDAP"))
            |> filter(fn: (r) => r["_field"] == "state")
            {addition}
        """,
            HTTP="""
            from(bucket: "{bucket}")
            |> range({range_time})
            |> filter(fn: (r) => (r._measurement == "service"))
            |> filter(fn: (r) => (r.name == "HTTP"))
            |> filter(fn: (r) => r["_field"] == "state")
            {addition}
        """,
        )

    def process_state(self, tables, data, state):
        for table in tables:
            for record in table.records:
                # print("record", record)
                groups = [
                    group.strip()
                    for group in record.values.get("groups", "").split(",")
                ]

                for group in groups:
                    if group not in data:
                        data[group] = dict(
                            up=0, down=0, unreach=0, downtime=0, unknow=0, total=0
                        )

                    is_downtime = (
                        record.values.get("downtime", "flase").lower() == "true"
                    )
                    if is_downtime:
                        data[group]["downtime"] += record.get_value()
                    else:
                        if state in data[group]:
                            data[group][state] += record.get_value()
                        else:
                            data[group]["unknow"] += record.get_value()
                            print(record)

                    data[group]["total"] += record.get_value()

    def get_current_state(self):
        data = dict()

        for metric in self.fluxs:
            result = self.get_metric_state(metric=metric, aggregate="last")
            for k, v in result.items():
                if k not in data:
                    data[k] = v
                else:
                    for sk, sv in v.items():
                        data[k][sk] += sv
        return data

    def get_state(self, started_date, ended_date):
        data = dict()

        for metric in self.fluxs:
            result = self.get_metric_state(
                metric=metric,
                started_date=started_date,
                ended_date=ended_date,
                # aggregate="count",
            )

            for k, v in result.items():
                if k not in data:
                    data[k] = v
                else:
                    for sk, sv in v.items():
                        data[k][sk] += sv

        return data

    def get_metric_state(
        self, metric, start="-5m", started_date=None, ended_date=None, aggregate=""
    ):
        range_time = f"start: {start}"
        aggregate_method = ""

        if started_date and ended_date:
            range_time = f"start: {started_date}, stop: {ended_date}"

        if aggregate:
            aggregate_method = f"|> {aggregate}()"

        data = dict()
        for state in range(0, len(self.metric_states[metric])):
            additions = []
            additions.append(f'|> filter(fn: (r) => r["_value"] == {state})')
            if aggregate_method:
                additions.append(aggregate_method)
            additions.append(f"|> count()")

            flux = self.fluxs[metric]
            flux = flux.format(
                bucket=self.bucket, range_time=range_time, addition="\n".join(additions)
            )

            # print("flux", flux)

            tables = self.query_api.query(flux)
            # print("->", tables)
            self.process_state(
                tables,
                data,
                self.metric_states[metric][state],
            )

        return data

    def get_sla_by_group(self, groups, started_date, ended_date):

        range_time = (
            f"start: {started_date.date().isoformat()}, stop: {ended_date.isoformat()}"
        )
        # range_time = f"start: -30d"
        addition = ""
        aggregate = "count"

        aggregate_method = f"|> {aggregate}()"
        additions = []
        additions.append(aggregate_method)
        addition = "\n".join(additions)

        groups_str = ",".join(groups)
        filters = ""

        flux_host_template = """
            from(bucket: "{bucket}")
            |> range({range_time})
            |> filter(fn: (r) => (r._measurement == "host"))
            |> filter(fn: (r) => r["_field"] == "state")
            |> filter(fn: (r) => r["groups"] == "{groups_str}")
            {filters}
            |> group(columns: ["id"])
            {addition}
        """

        down_record_counters = dict()
        record_counters = dict()

        flux_host = flux_host_template.format(
            bucket=self.bucket,
            range_time=range_time,
            groups=groups,
            addition=addition,
            groups_str=groups_str,
            filters=filters,
        )

        # print("flux>", flux_host)

        tables = self.query_api.query(flux_host)
        for table in tables:
            for record in table.records:
                # print(record)
                record_counters[record.values["id"]] = record.get_value()

        # print("all >>>", record_counters)

        filters = '|> filter(fn: (r) => r["_value"] == 1)'
        flux_host = flux_host_template.format(
            bucket=self.bucket,
            range_time=range_time,
            groups=groups,
            addition=addition,
            groups_str=groups_str,
            filters=filters,
        )
        tables = self.query_api.query(flux_host)
        for table in tables:
            for record in table.records:
                # print(record)
                down_record_counters[record.values["id"]] = record.get_value()

        # print("down >>>", down_record_counters)
        slas = dict()
        for key in record_counters.keys():
            if key in record_counters:
                slas[key] = 100 - (
                    down_record_counters.get(key, 0) / record_counters[key] * 100
                )

        return slas

    def get_current_state_by_group(self, groups, time_ago="-3m"):

        range_time = f"start: {time_ago}"
        addition = ""

        flux_host_template = """
            from(bucket: "{bucket}")
            |> range({range_time})
            |> filter(fn: (r) => (r._measurement == "host"))
            |> filter(fn: (r) => r["_field"] == "state")
            |> filter(fn: (r) => r["groups"] == "{groups}")
            {addition}
            |> count()
        """

        addition = '|> filter(fn: (r) => r["_value"] == 0 or r["_value"] == 2)'

        record_counters = dict()

        flux_host = flux_host_template.format(
            bucket=self.bucket,
            range_time=range_time,
            groups=",".join(groups),
            addition=addition,
        )
        tables = self.query_api.query(flux_host)
        for table in tables:
            for record in table.records:
                record_counters[record.values["id"]] = record.get_value()

        # print(">>>", record_counters)

        data = dict()
        for key, value in record_counters.items():
            if value:
                data[key] = True
            else:
                data[key] = False

        return data
