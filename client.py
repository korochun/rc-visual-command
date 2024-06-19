import requests, cv2, socket
import numpy as np
import keyboard, threading
import time
from PIL import Image, ImageDraw
from video_processing import *

client = requests.Session()
host = '192.168.100.37'
#host = 'localhost'

resol_resp = client.get(f'http://{host}:5000/').json()
resolution = resol_resp['resolution']
print(resolution)
size = resolution[0] * resolution[1] * resolution[2]


speed, steer = 0, 0


def keyboard_poll():
    global steer, speed
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    def connect():
        while True:
            try:
                sock.connect((host, 2976)) 
                break
            except:
                time.sleep(1)
                print('Error opening socket')
    connect()
    while True:
        steer, speed = 0, 0
        if keyboard.is_pressed("left"):
            steer -= 50
        if keyboard.is_pressed("right"):
            steer += 50
        if keyboard.is_pressed("up"):
            speed += 50
        elif keyboard.is_pressed("down"):
            speed -= 50
        try:
            sock.send((f'{steer}|{speed}').encode('ascii'))
        except Exception as e:
            print(e)
            connect() 

        time.sleep(0.1)

threading.Thread(target=keyboard_poll).start()

def pipeline(frame):
    global steer, speed
    frame =  cv2.resize(frame, (960, 720), interpolation = cv2.INTER_AREA)
    holder = gen_placeholder(frame, height=200)
    holder = add_speed(holder, speed, steer)
    frame = np.hstack((frame, holder))
    return frame


resp = client.get(f'http://{host}:5000/video_feed', stream=True)
for line in resp.iter_content(size):
    if line:
        frame = np.frombuffer(line, dtype=np.uint8).reshape(resolution)
        frame = pipeline(frame)
        cv2.imshow('stream', frame)
        cv2.waitKey(1)