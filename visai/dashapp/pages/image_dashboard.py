import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/image-dashboard")

image_result_interval = dcc.Interval(
    id="image-result-interval",
    interval=1000,  # in milliseconds
    n_intervals=0,
)


layout = html.Div(
    style={"textAlign": "center"},  # Center text in the whole div
    children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("Image URL"),
                        dcc.Input(
                            id="image-url-input",
                            type="text",
                            placeholder="Enter image URL",
                            style={"width": "300px"},  # Decrease input bar size
                        ),
                        html.Button(
                            "Request Image", id="request-image-button", n_clicks=0
                        ),
                        html.Div(id="upload-status"),
                        html.Div(id="upload-image-ids"),
                    ],
                    width={"size": 6, "offset": 3}  # Center column
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("Image Results"),
                        html.Div(id="image-results"),
                    ],
                    width={"size": 6, "offset": 3}  # Center column
                )
            ]
        ),
        image_result_interval,
        dcc.Store(id="image-ids"),
    ]
)
