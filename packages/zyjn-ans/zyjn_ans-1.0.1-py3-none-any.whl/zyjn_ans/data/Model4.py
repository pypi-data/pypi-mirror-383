import cv2
import serial
import time
import threading


class SmartHomeSystem:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            '/home/nle/pt/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml')
        self.ser = serial.Serial('/dev/ttyS0', 9600, timeout=1.0)
        self.human_detected = False # 红外传感器
        self.light_low = False  # 光照传感器
        self.face_detected = False  # 检测到人脸
        self.running = True
        self.serial_lock = threading.Lock() # 进程锁

    '''发送命令'''
    def send_command(self, command, description=""):
        with self.serial_lock:
            try:
                self.ser.flushInput()
                self.ser.flushOutput()
                cmd = bytes.fromhex(command)
                self.ser.write(cmd)
                time.sleep(0.5)
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    return data.hex()
                return None
            except Exception as e:
                return None

    '''人脸检测开锁'''
    def face_detection_thread(self):
        cap = cv2.VideoCapture(0)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

            if len(faces) > 0:
                if not self.face_detected:
                    print("检测到人脸，开门！")
                    self.send_command('01 05 00 13 FF 00 7D FF', "开门")
                    self.face_detected = True
                    threading.Timer(5, self.close_door).start()

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imshow('Face Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False

        cap.release()
        cv2.destroyAllWindows()

    '''关锁'''
    def close_door(self):
        print("5秒后关门")
        self.send_command('01 05 00 13 00 00 3C 0F', "关门")
        self.face_detected = False

    '''人体传感器检测房间是否有人'''
    def human_sensor_thread(self):
        while self.running:
            data_hex = self.send_command('01 01 00 00 00 07 7D C8', "读取人体传感器")

            if data_hex:
                if len(data_hex) >= 8:
                    if data_hex[0:6] == '010101':
                        status = int('0x' + data_hex[6:8], 16)
                        self.human_detected = (status == 0)

            time.sleep(2)

    '''光照传感器获取房间光照强度'''
    def light_sensor_thread(self):
        while self.running:
            data_hex = self.send_command('0C 03 00 00 00 02 C5 16', "读取光照传感器")

            if data_hex:
                if len(data_hex) >= 14:
                    if data_hex[0:2] == '0c':
                        light_value = int('0x' + data_hex[6:14], 16)
                        self.light_low = (light_value < 200)

            time.sleep(2)

    '''双传感器决策是否开灯'''
    def light_control_thread(self):
        light_on = False

        while self.running:
            if self.human_detected and self.light_low:
                if not light_on:
                    print("开灯")
                    self.send_command('01 05 00 11 FF 00 DC 3F', "开灯")
                    light_on = True
            else:
                if light_on:
                    print("关灯")
                    self.send_command('01 05 00 11 00 00 9D CF', "关灯")
                    light_on = False

            time.sleep(2)

    def run(self):
        print("启动智能家居系统...")
        print("按 'q' 退出")

        threads = [
            threading.Thread(target=self.face_detection_thread),
            threading.Thread(target=self.human_sensor_thread),
            threading.Thread(target=self.light_sensor_thread),
            threading.Thread(target=self.light_control_thread)
        ]

        for t in threads:
            t.daemon = True # 进程守护
            t.start()

        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:   # Ctrl+C终止
            self.running = False

        print("关闭所有设备...")
        self.send_command('01 05 00 13 00 00 3C 0F', "关门")
        self.send_command('01 05 00 11 00 00 9D CF', "关灯")
        if self.ser.is_open:
            self.ser.close()
        print("系统已关闭")


if __name__ == "__main__":
    system = SmartHomeSystem()
    system.run()