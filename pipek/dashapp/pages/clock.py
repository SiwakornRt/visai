import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/clock")

current_date_interval = dcc.Interval(
    id="current-date-interval",
    interval=1000,  # in milliseconds
    n_intervals=0,
)

layout = html.Div(
    children=[
        current_date_interval,
        html.H1(children="Service"),
        html.Div(id="current-date"),
        # health_check_bar,
        # html.Div(id="problem_services", style={"padding-top": "1em"}),
    ]
)
