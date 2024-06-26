from flask import Flask, render_template, Response, request, stream_with_context
import cv2, numpy as np
from pose_detection import process_frame as pose_processor
from coco_detection import process_frame as human_processor
from video_processing import add_text
from threading import Thread
import socket, serial, time
from comm import Send
from video_processing import add_text

app = Flask(__name__)
#camera = VideoCamera()

def get_cam():
    cap = cv2.VideoCapture(0)
    return cap
camera = get_cam()

cnt = 0
while not camera.read()[0]:
    time.sleep(0.2)
    print('webcam err')
    cnt+=1
    if cnt %10 == 0: 
        camera.release()
        camera = get_cam()

sample = camera.read()[1]
@app.route('/')
async def index():
    return {'resolution':sample.shape}

mode, target_id = 0, 0

def process_pose(frame):
    global mode
    if mode == 3:
        frame = pose_processor(frame)
    return frame

def process_coco(frame):
    global mode, target_id
    if mode == 2:
        frame, dir = human_processor(frame, target_id)
        frame = add_text(frame, f'Human detection is enabled', 20, -70)
        frame = add_text(frame, f'Current id: {target_id}', 20, -45)
        if dir is not None:
            frame = cv2.circle(frame, dir, 5, (0, 0, 255), 2)
            height = frame.shape[0] - dir[1]
            hl = frame.shape[1]//2
            angle = ((hl - dir[0])/hl)*60
            angle = (-1 if angle < 0 else 1) * min(abs(angle), 50)**1.1
            speed, steer = int(min((max(10, height)-15)*1.5, 70)), -int(angle)
        else:
            speed, steer = 0, 0
        frame = add_text(frame, f'Speed: {speed} Steering: {steer}', 20, -20)
        move(speed, steer)
    return frame
    


def pipeline(frame):
    frame = process_pose(frame)
    frame = process_coco(frame)
    return frame


def gen():
    global camera, mode
    cnt = 0
    while True:
        try:
            #frame = camera.get_frame()
            #yield (b'--frame\r\n'
            #    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            res, frame = camera.read()
            if res:
                frame = pipeline(frame) 
                enc = cv2.imencode('.jpeg', frame)[1]
                yield(enc.tobytes())
        except GeneratorExit:
            return
        except Exception as e:
            print(f'camera error: {e}')
            cnt += 1
            if cnt == 10:
                camera.release()
                camera = cv2.VideoCapture(0)
                cnt = 0


@app.route('/video_feed')
async def video_feed():
    try:
        return Response(gen())
    except:
        pass


sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.bind(('0.0.0.0', 2976))
sk.listen(1) 

import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
if len(ports) == 0:
    print('serial unavailable')
    #exit(0)
for p in ports:
    try:
        ser = serial.Serial(p.device, baudrate=115200)
        print(f'Serial {p.name} opened')
    except:
        print(f'Serial {p.name} unavailable')


def move(speed, steer):
    global ser
    print(f'to device: {speed} {steer}')
    Send(uSpeed=speed, uSteer=steer, ser=ser)

def socket_poll():
    global mode, target_id
    print('Ожидание порта запущено')
    conn = sk.accept()[0]
    print('Есть подключение!')
    while True:
        try:
            data = b''
            while not b'!' in data:
                data += conn.recv(1024)
            s = data.decode('ascii')
            s = s[:s.find('!')]
            steer, speed, mode, check, *shit = map(int, s.split('|'))
            if check != 7: continue
            print(speed, steer, mode)
            if mode < 2:
                move(speed, steer)
            elif mode in {2, 3}:
                target_id = steer
        except Exception as e:
            print(e)
            move(0, 0)
            conn = sk.accept()[0]
            print('Есть подключение!')



if __name__ == '__main__':
    Thread(target=socket_poll, daemon=True).start()
    app.run(host='0.0.0.0')