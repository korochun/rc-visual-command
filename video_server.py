from flask import Flask, render_template, Response, request, stream_with_context
import cv2
from detection import process_frame

app = Flask(__name__)
#cam = VideoCamera()
cam = cv2.VideoCapture(0)
while not cam.read()[0]:
    pass
sample = cam.read()[1]
@app.route('/')
async def index():
    return {'resolution':sample.shape}

def gen(camera):
    while True:
        try:
            #frame = camera.get_frame()
            #yield (b'--frame\r\n'
            #    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            res, frame = camera.read()
            if res:
                frame = process_frame(frame) 
                yield(frame.tobytes())
        except:
            ...

@app.route('/video_feed')
async def video_feed():
    return Response(gen(cam))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    cam.release()