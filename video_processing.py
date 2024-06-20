import cv2, numpy as np

GRAYSCALE = 35

def add_text(frame, text, x, y, size = 1, color = (255, 255, 255), thick = 1):
    if x < 0: x += frame.shape[1]
    if y< 0: y += frame.shape[0]
    return cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                       size, color, thick, cv2.LINE_AA)

def add_speed(frame, speed, steer):
    frame = add_text(frame, f'Speed: {speed}', 20, 40)
    frame = add_text(frame, f'Steer: {steer}', 20, 80)
    return frame

def insert_img(frame, img, x, y):
    frame[y:img.shape[0]+y, x:img.shape[1]+x] = img
    return frame

def gr(img):
    grsk = img.mean(axis = 2).astype(np.uint8)
    return grsk.reshape(grsk.shape+ (1,)).repeat(3, axis = 2)


CR_LOGO = cv2.imread('cruise.bmp')
CR_LOGO[CR_LOGO == 0] = GRAYSCALE
CR_LOGO_DISABED = gr(CR_LOGO)
def add_cruise(frame, flag):
    frame = insert_img(frame, CR_LOGO if flag else CR_LOGO_DISABED, 16, 100)
    return frame
CO_LOGO = cv2.imread('target.bmp')
CO_LOGO[CO_LOGO == 0] = GRAYSCALE
CO_LOGO_DISABED = gr(CO_LOGO)
CO_LOGO_DISABED[CO_LOGO_DISABED != 35] = 170
def add_coco(frame, flag):
    frame = insert_img(frame, CO_LOGO if flag else CO_LOGO_DISABED, 133, 100)
    return frame

PO_LOGO = cv2.imread('human.bmp')
PO_LOGO[PO_LOGO == 0] = GRAYSCALE
PO_LOGO_DISABED = gr(PO_LOGO)
PO_LOGO_DISABED[PO_LOGO_DISABED != 35] = 170
def add_pose(frame, flag):
    frame = insert_img(frame, PO_LOGO if flag else PO_LOGO_DISABED, 94, 200)
    return frame

def gen_placeholder(frame, height = None, width = None):
    #frame[-frame.shape[0]//8:, :200] //=3
    shape = [*frame.shape]
    if height is not None: shape[1] = height
    elif width is not None: shape[0] = width
    holder = np.ones(shape, dtype=np.uint8)*GRAYSCALE
    return holder



if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    frame = cap.read()[1]
    frame = cv2.resize(frame, (1600, 900), interpolation = cv2.INTER_AREA)
    cap.release()
#    add_speed(image, 100, 10)
    cv2.imshow('frame', frame)
    cv2.waitKey(0)