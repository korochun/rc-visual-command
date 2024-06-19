import requests, cv2, socket
import numpy as np
import keyboard, threading
import time
from PIL import Image, ImageDraw
import pygame
from video_processing import *

client = requests.Session()
host = '192.168.100.37'
#host = 'localhost'

resol_resp = client.get(f'http://{host}:5000/').json()
resolution = resol_resp['resolution']
print(resolution)
size = resolution[0] * resolution[1] * resolution[2]

accK = 10

speed, steer, mode = 0, 0, 0
key_up = True
#mode: 0 - normal, 1 - cruise


def keyboard_poll():
    global steer, speed, mode, key_up
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
        l, r, u, d = (keyboard.is_pressed(b) for b in ('left', 'right', 'up', 'down'))
        if not key_up: key_up = not(u or d)
        if mode == 0:
            if l:
                steer = max(steer - (abs(steer) + 1)**0.6, -50)
            if r:
                steer = min(steer + (abs(steer) + 1)**0.6, 50)

            if u:
                speed = min(speed + (abs(speed) + 1)**0.4, 100)
            if d:
                speed = max(speed - (abs(speed) + 1)**0.4, -100)
            if not (l or r):
                steer *= 0.7
            if not (u or d):
                speed *= 0.7
        elif mode == 1 and key_up:
            if l:
                steer = max(steer - 5, -50)
            if r:
                steer = min(steer + 5, 50)
            if not (l or r):
                steer = 0
            if u:
                speed = min(speed + 10, 100)
            if d:
                speed = max(speed - 10, -100)
        steer, speed = int(steer), int(speed)
        try:
            sock.send((f'{steer}|{speed}|{mode}|7').encode('ascii'))
        except Exception as e:
            print(e)
            connect() 

        time.sleep(0.15)

threading.Thread(target=keyboard_poll).start()

def toggle_cruise():
    global mode, key_up
    key_up = False
    mode = 1*(mode != 1)

def enable_coco(id):
    global mode, steer
    mode = 2
    steer = id
    
def disable_coco():
    global mode
    mode = 0

def cv2_to_pygame(image):
    pygame_image = pygame.image.frombuffer(image.tobytes(), image.shape[:2][::-1], "BGR")
    return pygame_image

def pipeline(frame):
    global steer, speed, mode
    frame =  cv2.resize(frame, (960, 720), interpolation = cv2.INTER_AREA)
    holder = gen_placeholder(frame, height=200)
    sspd, sstr = (speed, steer) if mode < 2 else (-1, -1)
    holder = add_speed(holder, sspd, sstr)
    holder = add_cruise(holder, mode == 1)
    holder = add_coco(holder, mode == 2)
    frame = np.hstack((frame, holder))
    return frame

pygame.init()
screen = None

try:
    resp = client.get(f'http://{host}:5000/video_feed', stream=True)
    for line in resp.iter_content(size):
        if line:
            frame = np.frombuffer(line, dtype=np.uint8).reshape(resolution)
            frame = pipeline(frame)

            if screen is None:
                screen = pygame.display.set_mode(frame.shape[1::-1])
                pygame.display.set_caption("Robot remote control")

            screen.blit(cv2_to_pygame(frame),(0,0))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        toggle_cruise()
                    elif 49 <= event.key <= 57:
                        enable_coco(event.key - 48)
                    elif event.key == 48:
                        disable_coco()

except KeyboardInterrupt or pygame.error:
    client.close()
    pygame.quit()
    exit(0)
    
    