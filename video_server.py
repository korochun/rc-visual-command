from flask import Flask, render_template, Response, request, stream_with_context
import cv2
from detection import process_frame
from video_processing import add_text
from threading import Thread
import socket, serial, time

app = Flask(__name__)
#camera = VideoCamera()
camera = cv2.VideoCapture(0)

cnt = 0
while not camera.read()[0]:
    time.sleep(0.2)
    print('webcam err')
    cnt+=1
    if cnt %10 == 0: 
        camera.release()
        camera = cv2.VideoCapture(0)

sample = camera.read()[1]
@app.route('/')
async def index():
    return {'resolution':sample.shape}

def pipeline(frame):
    frame = process_frame(frame)
    return frame


def gen():
    global camera
    cnt = 0
    while True:
        try:
            #frame = camera.get_frame()
            #yield (b'--frame\r\n'
            #    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            res, frame = camera.read()
            if res:
                frame = pipeline(frame) 
                yield(frame.tobytes())
        except:
            print('camera error')
            cnt += 1
            if cnt == 10:
                camera.release()
                camera = cv2.VideoCapture(0)
                cnt = 0


@app.route('/video_feed')
async def video_feed():
    return Response(gen())


sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.bind(('0.0.0.0', 2976))
sk.listen(1) 

def move(speed, steer):
    ...

def socket_poll():
    print('Ожидание порта запущено')
    conn = sk.accept()[0]
    print('Есть подключение!')
    while True:
        try:
            data = conn.recv(1024)
            speed, steer = map(int, data.decode('ascii').split('|'))
            print(speed, steer)
            move(speed, steer)
        except Exception as e:
            print(e)
            move(0, 0)
            conn = sk.accept()[0]
            print('Есть подключение!')
        time.sleep(0.05)



if __name__ == '__main__':
    Thread(target=socket_poll, daemon=True).start()
    app.run(host='0.0.0.0')