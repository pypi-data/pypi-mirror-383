import threading
from Algorithm.rtspCamera import NLRtspApi
import os
import time
import faulthandler
import cv2      
import concurrent.futures
from lib.ft2 import ft   # 中文描绘库
import ipywidgets as widgets    # jupyter画图库
from IPython.display import display  # jupyter显示库
from ctypes import *
from concurrent.futures import ThreadPoolExecutor
from lib.HiKang1 import HiKangThread1
import matplotlib.pyplot as plt
import sys
import platform


executor = ThreadPoolExecutor()
faulthandler.enable()
rtsp_img = None
rtsp_img_2 = None
rtsp_img_3 = None
limg = None
plate_number = None
result = None
cut_img = None

BASE_PATH = os.path.abspath('.')
#################################################################

class HiKangThread(threading.Thread):
    """
    枪型摄像头
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.working = True
        self.CapIsbasy = False
        self.thread_state = False
        self.s_u8nMediaIndex = (c_uint * 16)()
        self.camera_img = None
        global rtsp_img
        
    def rtsp_config(self):
        lib_path = '/usr/lib/newland/libmedia.so'
        self.nl_rtsp_api = NLRtspApi(libNamePath=lib_path)
        try:
            config_path = bytes(BASE_PATH, 'utf-8') + b'/Config/rtsp_config.ini'
            self.nl_rtsp_api.read_ini(config_path)
            num = self.nl_rtsp_api.get_url_num_from_ini()  # 获取url数量
            urls = []
            for i in range(num):
                rtsp_url = self.nl_rtsp_api.get_url_from_ini(i)  # 获取每一个url，放到列表里面
                urls.append(rtsp_url)
                self.s_u8nMediaIndex[i] = c_uint(i)
            rtsp_dict = {
                'url_num': num,
                'urls': urls
            }
            ret = self.nl_rtsp_api.nl_media_init()  # 初始化
            if ret != 0:
                self.nl_rtsp_api.nl_media_stop()
                return
            ret2 = self.nl_rtsp_api.nl_media_resource_config(self.s_u8nMediaIndex, num,
                                                             rtsp_dict)  # 配置，0表示h264，1表示h265
            if ret2 != 0:
                self.nl_rtsp_api.nl_media_stop()
                return
            ret3 = self.nl_rtsp_api.nl_media_start(self.s_u8nMediaIndex, num)  # 启动
            if ret3 != 0:
                self.nl_rtsp_api.nl_media_stop()
                return
            while self.working:
                if not self.thread_state:
                    self.thread_state = True
                    self.hikang_thread1 = HiKangThread1(self.nl_rtsp_api)
                    self.hikang_thread1.start()
                time.sleep(1)
        except KeyboardInterrupt as e:
            self.nl_rtsp_api.nl_media_stop()
        except Exception as e:
            print('rtsp系统错误，' + str(e))
            self.nl_rtsp_api.nl_media_stop()

    def run(self):
        self.rtsp_config()
        
    def get_counter(self):
        return self.hikang_thread1.get_counter()
                

    def stop(self):
        if self.working:
            self.working = False
            self.hikang_thread1.stop()
            self.nl_rtsp_api.nl_media_stop()
            print('The CameraThread is quit!')

###############################################################################
hikang_thread = HiKangThread()
hikang_thread.start()
time.sleep(5)

###################################################################

image_bgr = hikang_thread.get_counter()  
imgbox = widgets.Image()
imgbox.value = cv2.imencode('.jpg', image_bgr)[1].tobytes() # 把图像值转成byte类型的值
display(imgbox)

#########################
folder_name = 'image'  
if not os.path.exists(folder_name):  
    os.makedirs(folder_name)  
filename = os.path.join(folder_name, 'basketball.jpg')  
  
# 使用OpenCV将图像保存到文件  
cv2.imwrite(filename, image_bgr)  
