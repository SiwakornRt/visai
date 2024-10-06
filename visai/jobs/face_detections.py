import datetime
import cv2
import json
from sqlalchemy import select

from visai import models


def detect(image_id):
    print("detect", image_id)
    session = models.get_session()
    image = session.get(models.Image, image_id)

    print("process", image.id)
    image.status = "processing"
    image.updated_date = datetime.datetime.now()
    session.add(image)
    session.commit()

    img = cv2.imread(image.path)

    image.status = "completed"
    image.updated_date = datetime.datetime.now()
    session.add(image)
    session.commit()
