import datetime
import cv2
import json
import pathlib
import time

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

# Setup Detectron2 configuration
cfg = get_cfg()   # get a fresh new config
cfg.MODEL.DEVICE = "cpu"
cfg.merge_from_file(model_zoo.get_config_file("COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7  # set threshold for this model
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml")

def detect(img_path):
    print("detect", img_path)
    
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: Unable to read image at {img_path}")
        return 0  # Return 0 if image is not readable
    
    # Initialize the predictor
    predictor = DefaultPredictor(cfg)
    outputs = predictor(img)
    
    # Get the number of bounding boxes
    bboxes = outputs["instances"].pred_boxes.tensor.cpu().numpy()
    print(f"Number of bounding boxes in {img_path}: {len(bboxes)}")

    # Visualize the output
    v = Visualizer(img[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=0.5)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    img = out.get_image()[:, :, ::-1]  # Convert back to BGR for OpenCV
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return len(bboxes)

def process_images_in_folder(folder_path, output_file):
    folder = pathlib.Path(folder_path)
    i = 1
    with open(output_file, 'w') as f:
        for img_file in folder.glob("*.jpg"): 
            print(f"{i} Processing {img_file.name}...")
            i += 1
            num_bboxes = detect(str(img_file))
            f.write(f"{img_file.name},{num_bboxes}\n")

# process_images_in_folder("airflow-redis-postgres/src/spark/assets/cam01", "bounding_boxes_count.txt")
detect("airflow-redis-postgres/src/spark/assets/cam01/cam_120241005_005457.jpg")