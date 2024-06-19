import cv2, numpy as np
from PIL import Image, ImageFont, ImageDraw

monospace = ImageFont.truetype("Nunito.ttf",32)


def add_text(frame, text, x, y, size = 1, color = (255, 255, 255), thick = 1):
    if x < 0: x += frame.shape[1]
    if y< 0: y += frame.shape[0]
    return cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                       size, color, thick, cv2.LINE_AA)

def add_speed(frame, speed, steer):
    frame = add_text(frame, f'Speed: {speed}', 20, 40)
    frame = add_text(frame, f'Steer: {steer}', 20, 80)
    return frame

def add_cruise(frame, flag):
    frame = add_text(frame, f'Cruise: {"on" if flag else "off"}', 20, 120)
    return frame

def gen_placeholder(frame, height = None, width = None):
    #frame[-frame.shape[0]//8:, :200] //=3
    shape = [*frame.shape]
    if height is not None: shape[1] = height
    elif width is not None: shape[0] = width
    holder = np.ones(shape, dtype=np.uint8)*40
    return holder



if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    frame = cap.read()[1]
    frame = cv2.resize(frame, (1600, 900), interpolation = cv2.INTER_AREA)
    cap.release()
    frame = add_placeholder(frame)
#    add_speed(image, 100, 10)
    cv2.imshow('frame', frame)
    cv2.waitKey(0)