import dash
import json
import pathlib
import io
import time
import requests
from dash import html, dcc
from PIL import Image
import base64

from flask import current_app
from visai import models
from visai.web import redis_rq
from visai.jobs import face_detections


# Function to load an image from a URL
def load_image_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image
        else:
            print(
                f"Failed to retrieve image from {url}, status code: {response.status_code}"
            )
            return None
    except Exception as e:
        print(f"Error occurred while loading image from URL: {e}")
        return None


# Function to save the image and create a database entry
def parse_image(image, filename):
    image_dir_path = pathlib.Path(current_app.config.get("VISAI_DATA")) / "images"
    image_dir_path.mkdir(
        parents=True, exist_ok=True
    )  # Create the directory if it doesn't exist

    stored_filename = image_dir_path / filename
    while stored_filename.exists():
        stored_filename = image_dir_path / f"{round(time.time() * 1000)}-{filename}"

    image.save(stored_filename)

    # Create a new Image entry in the database
    db_image = models.Image(
        path=str(stored_filename),  # Store the path as a string
        filename=filename,
    )

    models.db.session.add(db_image)
    models.db.session.commit()
    models.db.session.refresh(db_image)

    # Enqueue a job for face detection
    job = redis_rq.redis_queue.queue.enqueue(
        face_detections.detect,
        args=(db_image.id,),
        timeout=600,
        job_timeout=600,
    )

    return db_image.id, f"{db_image.id} Upload Completed"


# Define Dash layout
layout = html.Div(
    [
        dcc.Input(id="image-url-input", type="text", placeholder="Enter image URL"),
        html.Button("Request Image", id="request-image-button", n_clicks=0),
        html.Div(id="upload-status"),
        html.Div(id="upload-image-ids"),
        dcc.Store(id="image-ids"),
        dcc.Interval(id="image-result-interval", interval=1000, n_intervals=0),
        html.Div(id="image-results"),
    ]
)


@dash.callback(
    dash.Output("upload-status", "children"),
    dash.Output("upload-image-ids", "children"),
    dash.Output("image-ids", "data"),
    dash.Input("request-image-button", "n_clicks"),
    dash.State("image-url-input", "value"),
)
def request_image(n_clicks, image_url):
    if (
        n_clicks > 0 and image_url
    ):  # Check if the button was clicked and the URL is provided
        image = load_image_from_url(image_url)  # Load the image from the provided URL
        if image:
            image_id, result = parse_image(
                image, image_url.split("/")[-1]
            )  # Save image and return ID
            return result, html.Div(f"Image ID: {image_id}"), json.dumps([image_id])
        else:
            return "Failed to load image from URL.", "", ""
    return "", "", ""


@dash.callback(
    dash.Output("image-results", "children"),
    dash.Input("image-result-interval", "n_intervals"),
    dash.Input("image-ids", "data"),
)
def get_image_results(n_intervals, image_ids):
    if not image_ids:
        return "Not Uploaded"

    datas = json.loads(image_ids)
    results = []

    for image_id in datas:
        image = models.db.session.get(models.Image, image_id)
        if image:
            # Convert the image to base64 for display
            with open(image.path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
                image_tag = html.Img(
                    src=f"data:image/jpeg;base64,{encoded_string}",
                    style={"width": "300px"},
                )
                results.append(
                    html.Div(
                        [
                            image_tag,
                            html.Div(
                                f"Image ID: {image.id}, Status: {image.status}, Results: {image.results}, Updated: {image.updated_date}"
                            ),
                        ]
                    )
                )

    return html.Div(results)
