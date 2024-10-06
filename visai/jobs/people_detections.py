import datetime
import cv2
import json
import pathlib
from flask import current_app
import time

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

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

    filename = image.filename
    img = cv2.imread(image.path)

    cfg = get_cfg()   # get a fresh new config
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7  # set threshold for this model
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml")
    predictor = DefaultPredictor(cfg)
    outputs = predictor(img)
    v = Visualizer(img[:,:,::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    img = out.get_image()[:, :, ::-1]

    image_dir_path = pathlib.Path(current_app.config.get("VISAI_DATA")) / "processed_images"
    image_dir_path.mkdir(
        parents=True, exist_ok=True
    )  # Create the directory if it doesn't exist

    # stored_filename = image_dir_path / filename
    # while stored_filename.exists():
    stored_filename = image_dir_path / f"{round(time.time() * 1000)}-{filename}-processed"

    image.save(stored_filename)

    db_image = models.Image(
        path=str(stored_filename),  # Store the path as a string
        filename=filename,
    )

    models.db.session.add(db_image)
    models.db.session.commit()
    models.db.session.refresh(db_image)

    image.status = "completed"
    image.updated_date = datetime.datetime.now()
    session.add(image)
    session.commit()