rknn = RKNN(verbose=True)
ret = rknn.config(reorder_channel = '0 1 2',
                  mean_values = [[0, 0, 0]],
                  std_values = [[255, 255, 255]],
                  optimization_level = 3,
                  target_platform = 'rk3399pro',
                  output_optimize = 1,
                  quantize_input_node = True)
print(ret)

##############################################################
ret = rknn.build(do_quantization=True, dataset='./yolov5/rknn/dataset.txt')
if ret!=0:
     print("构建rknn模型失败")
else:
    print("构建rknn模型成功")
ret = rknn.export_rknn('./yolov5/rknn/models/best.rknn')
if ret!=0:
    print("导出rknn模型失败")
else:
    print("导出rknn模型成功")

####################################################################
import cv2
ret = rknn.load_rknn('./yolov5/rknn/models/best.rknn')
if ret ==0:
    ret = rknn.init_runtime(perf_debug=True, eval_mem=True)
    if ret ==0:
        img = cv2.imread("./yolov5/data/images/bus.jpg")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (640, 640))
        results = rknn.inference(inputs=[img])
        print(results)
#################################################################
# 图像采集
class CameraThread(threading.Thread):
    def __init__(self, camera_id, camera_width, camera_height):
        threading.Thread.__init__(self)
        self.working = True
        self.running = False
        self.cap = cv2.VideoCapture(camera_id)  # 打开摄像头
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)  # 设置摄像头分辨率宽度
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)  # 设置摄像头分辨率高度
        
    def run(self):
        self.running = True
        global camera_img     # 定义一个全局变量，用于存储获取的图片，以便于算法可以直接调用
        camera_img = None
        while self.working:
            ret, camera_img = self.cap.read()  # 获取新的一帧图片
        self.running = False

    def stop(self):
        self.working = False
        while self.running:
            pass
        self.cap.release()

###########################################################################

imgbox = widgets.Image()  # 定义一个图像盒子，用于装载图像数据
imgbox.value = cv2.imencode('.jpg', camera_img)[1].tobytes() # 把图像值转成byte类型的值
display(imgbox) 
#######################################################################
class DetectThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.working = True
        self.running = False       
        # Create RKNN object
        self.rknn = RKNN(verbose=True)
        # Load RKNN model
        ret = self.rknn.load_rknn(RKNN_MODEL)
        # init runtime environment
        ret = self.rknn.init_runtime(async_mode=True)

        # 创建图像盒子
        self.imgbox = widgets.Image()
        display(self.imgbox)

    def run(self):
        global flash_light
        flash_light = False
        self.running = True
        while self.working:
            try:
                if camera_img is not None:
                    img_1 = camera_img
                    img, ratio, (dw, dh) = letterbox(img_1, new_shape=(IMG_SIZE, IMG_SIZE))
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    outputs = self.rknn.inference(inputs=[img])
                    input_data = post_process(outputs)
                    boxes, classes, scores = yolov5_post_process(input_data)
                    if boxes is not None:
                        if 0 in classes:
                            flash_light = True
                            draw(img_1, boxes, scores, classes, dw, dh, ratio)
                    # 更新图像盒子的值
                    img_bytes = cv2.imencode('.jpg', img_1)[1].tobytes()
                    self.imgbox.value = img_bytes
                    flash_light = False
            except Exception as e:
                pass
        self.running = False

    def stop(self):
        self.working = False
        while self.running:
            pass
        self.rknn.release()

#######################################################################

class LightThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.working = True
        self.running = False
        self.port = "/dev/ttyS0"
        self.ser = serial.Serial(self.port, 9600, timeout=0.2)
        self.ser.flushInput()
        self.ser.flushOutput()
    
    def exec_cmd(self, command):
        """
        执行led控制
        :param command: 16进制值
        :return:
        """
        try:
            cmd = bytes.fromhex(command)
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.write(cmd)
        except Exception as e:
            print('NewQuerySerial error: ' + str(e))
    
    def turn_on_red(self):
        """
        打开红灯 
        :return:
        """
        command = '01 05 00 10 FF 00 8D FF' # 打开红灯
        self.exec_cmd(command)

    def turn_off_red(self):
        """
        关闭红灯
        :return:
        """
        command = '01 05 00 10 00 00 CC 0F' # 关闭红灯
        self.exec_cmd(command)

    def close_serial(self):
        """
        关闭串口
        :return:
        """
        try:
            self.ser.close()
        except Exception as e:
            print(e)
                   
    def run(self):
        self.running =False
        while self.working:
            try:
                if flash_light:
                    self.turn_on_red()
                    time.sleep(0.5)
                    self.turn_off_red()
                    time.sleep(0.5)
            except Exception as e:
                print('light error: ' + str(e))
                pass
        self.running = True
                
    def stop(self):
        self.working = False
        while self.running:
            pass
        self.turn_off_red()
        time.sleep(0.5)
        self.close_serial() # 温度检测出关闭串口
        print('LightThread quit!')

###################################################
light_th = LightThread()
light_th.start()
############################
detect_th.stop()
camera_th.stop()
light_th.stop()