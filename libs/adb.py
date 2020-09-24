# coding=UTF-8
'''
Created on 2020年9月24日
@author: lishang
'''
import win32gui, win32con, win32api
import time
import os, sys
import re
import getopt
import subprocess
from PIL import ImageGrab, Image
from threading import Timer, Thread
import _thread
import pytesseract
import cv2
import numpy as np
from skimage.measure import compare_ssim
import logging
LOG = logging.getLogger(__name__)

class ADB:
    def __init__(self,device_Name,screen_Size):
        #self.adb_Path = "C:/Program Files (x86)/Nox/bin/nox_adb.exe"  #夜神
        self.adb_Path = "C:/XuanZhi/LDPlayer/adb.exe"   #雷電
        self.screen_Size = screen_Size
        self.device_Name = device_Name
        self.Nox_Path = r"C:/Program Files (x86)/Nox/bin/"
        self.LD_Path = r'C:/XuanZhi/LDPlayer/'
        self.hwnd = 0
        self.screen_Hot = None

    def Start_Game(self, Game_Activity_Name, device_Name=None):
        if not device_Name:
            device_Name = self.device_Name
        self.adb_call(device_Name, ['shell', 'am', 'start', '-n', Game_Activity_Name])

    def Shut_Down_Game(self, Game_Activity_Name, device_Name=None):
        if not device_Name:
            device_Name = self.device_Name
        self.adb_call(device_Name, ['shell', 'am', 'force-stop', Game_Activity_Name])

    def Keep_Game_ScreenHot(self,Emu_Index,file_Name):
        th = Thread(self.Keep_Game_ScreenHot_fn,args=[Emu_Index,file_Name])
        th.start()

    def Keep_Game_ScreenHot_fn(self,Emu_Index,file_Name):
        self.hwrd = self.Get_Self_Hwnd(Emu_Index)
        while 1:
            self.window_capture(hwnd=self.hwnd,fileName=file_Name)
            time.sleep(1)

    def Get_Self_Hwnd(self,index_Num):
        device_List = self.LD_Call()  #雷電
        for k, device_Data in enumerate(device_List):
            if k != index_Num:
                continue
            hwnd = device_Data[3]
            return hwnd

    def Game_ScreenHot_By_Adb(self, device_Name=None, save_path=None):
        if not device_Name:
            device_Name=self.device_Name
        if not save_path:
            LOG.error('Error: 請輸入保存圖片的路徑')
            print('wrong!請輸入保存圖片的路徑')
        else:
            local_path = 'C:/Users/username/python_workspace/GitHub/worldFlipperATS/'+save_path
            self.adb_call(device_Name, ['exec-out', 'screencap', '-p', '>', local_path])
            time.sleep(0.2)

    def Get_Rect_Img(self,x1,y1,x2,y2):
        pass

    def Nox_Call(self):
        file_Path = self.Nox_Path + "NoxConsole.exe"
        output = subprocess.Popen([file_Path,"list2"], shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE)
        end = []
        for line in output.stdout.readlines():
            output = line.decode("BIG5")
            output = output.strip()
            if output != "":
                output = output.split(",")
                end.append(output)
        return end

    def LD_Call(self):
        file_Path = self.LD_Path + "LDConsole.exe"  
        output = subprocess.Popen([file_Path,"list2"], shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE)
        end = []
        for line in output.stdout.readlines():
            output = line.decode("BIG5")
            output = output.strip()
            print('output is : ',output)
            if output != "":
                output = output.split(",")
                end.append(output)
        return end

    def window_capture(self,hwnd,fileName):
        game_Rect = win32gui.GetWindowRect(int(hwnd))
        src_Image = ImageGrab.grab(game_Rect)
        src_Image = src_Image.resize(self,screen_Size,Image.ANTIALIAS)
        src_Image.save(fileName)
        self.screen_Hot = src_Image

    def Touch(self,x,y,device_Name=None):
        if not device_Name:
            device_Name = self.device_Name
        x = str(x)
        y = str(y)
        self.adb_call(device_Name,["shell","input","tap",x,y])
    
    def Press(self,keypoint,device_Name=None):
        if not device_Name:
            device_Name = self.device_Name
        keypoint = str(keypoint)
        self.adb_call(device_Name,["shell","input","keyevent",keypoint])

    def Text_Input(self,text,device_Name=None):
        if not device_Name:
            device_Name = self.device_Name
        self.adb_call(device_Name,["shell","input","text",text])

    def Swipe(self,x1,y1,x2,y2,device_Name=None):
        if not device_Name:
            device_Name = self.device_Name
        x1 = str(x1)
        y1 = str(y1)
        x2 = str(x2)
        y2 = str(y2)
        self.adb_call(device_Name, ["shell", "input", "swipe",x1,y1,x2,y2])

    def adb_call(self,adb_Path,device_List):
        command = [self.adb_Path,"-s",self.device_Name]
        for order in device_List:
            command.append(order)
        try:
            subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
        except subprocess.CalledProcessError as error:
            output = error.output
            code = error.returncode
            if output == b'error: device not found\r\n':
                LOG.INFO('執行adb kill-server, 並等待 5 秒重啟時間')
                subprocess.Popen([self.adb_Path,"kill-server"])
                time.sleep(5)
                subprocess.Popen(command,shell=True)
                LOG.INFO('重新呼叫成功')

    def Drag(self,x1,y1,x2,y2,x3,y3,deley_Time=1):
        x1 = x1 * 19199 / self.screen_Size[0]
        y1 = y1 * 10799 / self.screen_Size[1]
        x2 = x2 * 19199 / self.screen_Size[0]
        y2 = y2 * 10799 / self.screen_Size[1]
        x3 = x3 * 19199 / self.screen_Size[0]
        y3 = y3 * 10799 / self.screen_Size[1]

        
if __name__ == '_main__':
    #obj = ADB(device_Name='127.0.0.1:62001',screen_Size=[720,1280])  #夜神
    obj = ADB(device_Name=os.environ.get('DEVICE_NAME'),screen_Size=[540,960])
    hawd = obj.Get_Self_Hwnd(0)
    obj.Drag(467,1164,400,1164,370,1164)