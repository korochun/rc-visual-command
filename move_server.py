import socket

sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.bind(('0.0.0.0', 2976))
sk.listen(1) 
conn = sk.accept()[0]

while True:
    try:
        data = conn.recv(1024)
        speed, steer = map(int, data.decode('ascii').split('|'))
        print(speed, steer)
    except Exception as e:
        print(e)
        conn = sk.accept()[0]
