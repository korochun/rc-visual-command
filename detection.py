from math import degrees, atan2, pi
import cv2, torch
from ultralytics import YOLO
from ultralytics.engine.results import Results
from ultralytics.utils.plotting import Annotator
from webcam import Webcam

COLORS = {
    "left": (70, 230, 30),
    "right": (30, 230, 70),
    "left_up": (70, 230, 30),
    "right_up": (30, 230, 70),
    "circle": (200, 200, 60),
    "test_up": (30, 70, 230),
    "test_stop": (230, 70, 30)
}

THRESHOLD = 30


def around(angle, other, wrap=360, threshold=THRESHOLD):
    diff = angle - other
    clamp = diff - (diff + wrap / 2) // wrap * wrap
    return abs(clamp) < threshold


def detect_poses(result: Results):
    if result.keypoints is None or result.keypoints.xy is None or result.keypoints.conf is None or result.boxes is None:
        return []
    for kpts, box, conf in reversed([*zip(result.keypoints.xy, result.boxes.data, result.keypoints.conf)]):
        if kpts.numel() == 0: continue
        
        quality = conf[5:11].min()
        if quality < 0.25: continue

        left_shoulder = kpts[7] - kpts[5]
        left_elbow = kpts[9] - kpts[7]
        right_shoulder = kpts[8] - kpts[6]
        right_elbow = kpts[10] - kpts[8]
        
        left_shoulder = left_shoulder / left_shoulder.norm()
        left_elbow = left_elbow / left_elbow.norm()
        right_shoulder = right_shoulder / right_shoulder.norm()
        right_elbow = right_elbow / right_elbow.norm()
        
        ls_angle = degrees(atan2(*left_shoulder))
        le_angle = degrees(atan2(*left_elbow))
        rs_angle = degrees(atan2(*right_shoulder))
        re_angle = degrees(atan2(*right_elbow))

        left_is_straight = around(ls_angle, le_angle, threshold=THRESHOLD * 2)
        right_is_straight = around(rs_angle, re_angle, threshold=THRESHOLD * 2)
        left_horiz = around(ls_angle, 90) and left_is_straight
        right_horiz = around(rs_angle, 270) and right_is_straight
        left_up = around(ls_angle, 180)
        right_up = around(rs_angle, 180)
        left_sup = around(ls_angle, 180) and left_is_straight
        right_sup = around(rs_angle, 180) and right_is_straight
        
        if left_up and right_up and (kpts[10] - kpts[9]).norm() < 100:
            yield box, "circle", kpts[5:11]
        elif left_sup and right_sup:
            yield box, "test_up", kpts[5:11]
        else:
            if left_sup:
                yield box, "left_up", kpts[5:11:2]
            if right_sup:
                yield box, "right_up", kpts[6:11:2]
        if right_horiz and left_horiz:
            yield box, "test_stop", kpts[5:11]
        else:
            if left_horiz:
                yield box, "left", kpts[5:11:2]
            if right_horiz:
                yield box, "right", kpts[6:11:2]


def plot_stuff(annotator: Annotator, result: Results, pose):
    for kpts, box in reversed([*zip(result.keypoints.data, result.boxes.data)]):
        # add keypoints/skeletons
        annotator.kpts(kpts, result.orig_shape, radius=5, kpt_line=True)

        annotator.box_label(box[:4], str(float(box[4])), color=(5, 71, 175))
    
    for box, name, points in pose:
        # box
        xs = points[:, 0]
        ys = points[:, 1]
        annotator.box_label((xs.min(), ys.min(), xs.max(), ys.max()), label=f'{name}, {box[4]}', color=COLORS[name])



# load the pose detection model
model = YOLO('yolov8n-pose.pt')

# connect webcam
webcam = Webcam(0)
for frame in webcam:
    # apply model and plot keypoints to image
    result = model.track(frame)[0]

    pose = [*detect_poses(result)]

    plot_stuff(Annotator(frame), result, pose)

    # Show the frames in a cv2 window
    cv2.imshow('Webcam Frame', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    # Break the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
