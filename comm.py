import struct, serial, time, ctypes, keyboard
 #start, steer, speed, chcs


def checksm(*args):
    x = 0
    for i in args:
        x ^= ctypes.c_uint16(i).value
    return x
class SerialCommand():
    def __init__(self, **kwargs):
        self.f = "HhhH"
        self.data = (kwargs)
    def __call__(self):
        return struct.pack(self.f, self.data.get("start", 0),
                   self.data.get("steer", 0),
                   self.data.get("speed", 0),
                   self.data.get("checksum", 0))
#start cmd1 cmd2 speedR_meas speedL_meas batVoltage boardTemp cmdLed checksum

class SerialFeedback():
    def __init__(self, **kwargs):
        self.f = "IiiiiiiII"
        self.data = (kwargs)
    def __call__(self):
        return struct.pack(self.f,
            self.data.get("start", 0),
            self.data.get(" cmd1", 0),
            self.data.get(" cmd2", 0),
            self.data.get(" speedR_meas", 0),
            self.data.get(" speedL_meas", 0),
            self.data.get(" batVoltage", 0),
            self.data.get(" boardTemp", 0),
            self.data.get("cmdLed", 0),
            self.data.get("checksum", 0))


def Send(uSteer, uSpeed, ser: serial.Serial):
  # Create command
  cmd = SerialCommand(start = 0xABCD, steer = uSteer,
                    speed = uSpeed, checksum = checksm(0xABCD, uSteer, uSpeed))

  # Write to Serial
  ser.write(cmd())

if __name__ == '__main__':
    ser = serial.Serial('COM7', baudrate=115200)
    print(ser)
    speed, steer = 0, 0
    while True:
        if keyboard.is_pressed('W'):
            speed += 100
        if keyboard.is_pressed('S'):
            speed  -= 100
        if keyboard.is_pressed('D'):
            steer  += 100
        if keyboard.is_pressed('A'):
            steer  -= 100
        if keyboard.is_pressed('X'):
            speed, steer = 0, 0
        print(speed, steer)
        Send(steer, speed, ser)
        time.sleep(0.100)