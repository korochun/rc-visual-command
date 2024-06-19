from math import degrees, atan2, pi
import cv2, torch
from ultralytics import YOLO
from ultralytics.engine.results import Results
from ultralytics.utils.plotting import Annotator

model = YOLO('yolov8n.pt')
model.classes = [0]

def process_frame(frame, id):
    results = model.track(frame, persist=True)[0]
    return results.plot(), calc_dir(results, id)

def calc_dir(results, id):
    boxes = results.boxes[results.boxes.id == id]
    if not len(boxes):
        return
    xyxy = boxes[0].xyxy[0]
    pos = (int((xyxy[0] + xyxy[2])//2), int(xyxy[3]))
    return pos


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        frame = cap.read()[1]
        
        annotated_frame, dir = process_frame(frame, 1)
        if dir is not None:
            annotated_frame = cv2.circle(annotated_frame, dir, 10, (255,255,255), 2)
        cv2.imshow("YOLOv8 Tracking", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()