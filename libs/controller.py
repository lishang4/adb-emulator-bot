# coding=UTF-8
'''
Created on 2020年9月24日
@author: lishang
'''
from adb import ADB
import time, datetime
import os
import logging
import cv2
import numpy as np
import pytesseract
import re
from skimage.measure import compare_ssim
LOG = logging.getLogger(__name__)

class Controller:
    def __init__(self):
        self.ADB = ADB(device_Name=os.environ.get('DEVICE_NAME'),screen_Size=(560,960))
        self.package = os.environ.get('PACKAGE_NAME')
        self.activity = os.environ.get('ACTIVITY_NAME')

    def Game_Start(self):
        LOG.info(f'啟動遊戲({self.game_package}),等待 5 秒')
        self.ADB.Start_Game(Game_Activity_Name=f'{self.package}/{self.activity}')
        time.sleep(5)

    def Game_Stop(self):
        LOG.info(f'關閉遊戲({self.game_package}),等待 5 秒')
        self.ADB.Shut_Down_Game(Game_Activity_Name=f'{self.package}')
        time.sleep(5)

    def Login_Game(self):
        pass

    def Get_Account_ID(self):
        logging.info('判斷是否已回到首頁')
        print('開始判斷是否已回到首頁')
        self.ADB.Image_Grab(mode='grabed_summon-button')
        stat = self.ADB.Recognize_Img(mode='summon-button')
        while stat != True:
            self.ADB.Touch(35,921)  ##上一頁
            self.ADB.Image_Grab(mode='grabed_summon-button')
            stat = self.ADB.Recognize_Img(mode='summon-button')
        logging.info('已回到首頁，進入\'其他\'選單')
        print('已回到首頁，進入\'其他\'選單')
        self.ADB.Touch(492,921)  #進入'其他'選單
        time.sleep(1.5)
        self.ADB.Touch(267,851)  #點擊引繼
        logging.info('判斷是否已進到準備引繼的選單')
        print('開始判斷是否已進到準備引繼的選單')
        self.ADB.Image_Grab(mode='grabed_setaccount-button')
        stat = self.ADB.Recognize_Img(mode='setaccount-button')
        while stat != True:
            self.ADB.Image_Grab(mode='grabed_setaccount-button')
            stat = self.ADB.Recognize_Img(mode='setaccount-button')
        logging.info('已進入，開始引繼')
        print('已進入，開始引繼')
        time.sleep(0.5)
        self.ADB.Touch(265,583)  #點擊開始引繼
        time.sleep(1)
        self.ADB.Touch(388,816)  #ok
        time.sleep(1)
        self.ADB.Touch(266,490)  #點擊使用引繼碼
        time.sleep(1)
        self.ADB.Touch(270,659)  #ok
        time.sleep(1)
        self.ADB.Touch(263,566)  #點擊生成引繼碼
        time.sleep(1)
        self.ADB.Touch(261,354)  #點擊密碼框
        time.sleep(0.5)
        self.ADB.Text_Input('47004700')
        time.sleep(0.5)
        self.ADB.Touch(261,413)  #點擊確認密碼框
        time.sleep(0.5)
        self.ADB.Text_Input('47004700')
        time.sleep(0.5)
        self.ADB.Touch(70,597)  #勾選同意條款
        time.sleep(0.5)
        self.ADB.Touch(268,700)  #下一步
        time.sleep(1)
        #通信中

    def Recognize_Account(self,starNumber=0):
        logging.info('判斷是否已引繼成功得到引繼碼')
        print('開始判斷是否已引繼成功得到引繼碼')
        self.ADB.Image_Grab(mode='get_accountconfirm-button')
        stat = self.ADB.Recognize_Img(mode='accountconfirm-button')
        while stat != True:
            self.ADB.Image_Grab(mode='get_accountconfirm-button')
            stat = self.ADB.Recognize_Img(mode='accountconfirm-button')
        account = self.ADB.Image_Grab(mode='get_account')
        logging.info('成功獲得。將獲得的引繼碼({})存入指定目錄'.format(account))
        print('開始將獲得的引繼碼({})存入指定目錄'.format(account))
        os.rename('./image/account/waitForAnalysis.jpg','./image/account/{}_fiveStar/{}.jpg'.format(starNumber,account))

    def check(self,mode=None):
        time.sleep(3)
        count = 0
        self.ADB.Image_Grab(mode=f'grabed_{mode}')
        stat = self.ADB.Recognize_Img(mode=mode)
        while stat != True:
            if mode == 'delete-button' and count >60:
                logging.error('當機！關閉遊戲並等待 3 秒後重啟')
                self.ADB.Start_Game(Game_Activity_Name=f'{self.package}/{self.activity}')
                time.sleep(3)
            #print('目前狀態: ', stat)
            count = count +1
            self.ADB.Image_Grab(mode=mode)
            stat = self.ADB.Recognize_Img(mode=mode)
        #time.sleep(0.3)

    ##position coordinate---
    ##318,458,443,485 account's
    ##470,78,519,110 team-member's 
    ##370,900,442,951 summon-button's
    ##158,582,386,609 setaccount-button
    ##470,26,512,67  delete-button
    ##340,642,437,668  agree-button
    ##111,606,182,629  canceltutorial-button
    ##239,607,291,628  got4starconfirm-button
    ##245,457,290,478  nameconfirm-button
    ##244,663,287,682  accountconfirm-button
    ##176,394,361,481  gotpriceconfirm-button
    ##248,608,287,629  afterpriceconfirmok-button
    ##460,26,503,44  skip-button
    ##434,803,511,854  backtotop-button
    ##----- star(差距66,16)  每一行間角色間距114
    ##79,452,145,468 [0,0]star  193,452,259,468 [0,1]star  307,452,373,468 [0,2]star  421,452,487,468 [0,3]star   1,2,3,4
    ##135,602,201,618 [1,0]star 249,602,315,618 [1,1]star  363,602,429,618 [1,2]star                              5,6,7
    ##79,752,145,768 [2,0]star  193,752,259,768 [2,1]star  307,752,373,768 [2,2]star  451,752,487,768 [2,3]star   8,9,10,11
    ##135,902,201,918 [3,0]star 249,902,315,902 [3,1]star  363,902,429,902 [3,2]star                              12,13,1

    # TODO: ImageGrabu應該只做一件事, 判斷做什麼應該放在controller內, return img(cv2.imread)即可
    def Image_Grab(self, mode=None, coordinate=[0,5,0,5]):
        tmp_grab_path = r'/image/openCV_Img/'
        path_ = tmp_grab_path+'tmp_grab.jpg'
        self.Game_ScreenHot_By_Adb(save_path=path_)
        img = cv2.imread('.'+path_, cv2.IMREAD_GRAYSCALE)
        if mode == 'check_star':
            self.Grab_Charactor_Star(img=img)
        elif mode:
            self.Grab_Screen_Partition(img=img, mode=mode, coordinate=coordinate)

    def Grab_Screen_Partition(self, img=img, mode=None, coordinate=coordinate):
        tmp_grab_path = r'/image/openCV_Img/'
        if mode == 'account':
            pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
            imgs = img[458:485, 318:443] ##[y1::y2, x1:x2]
            img_np = np.array(imgs)
            frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
            cv2.imwrite('.'+tmp_grab_path+mode+'.jpg', frame)
            result = pytesseract.image_to_string(frame)
            result = re.sub(r'[l\[\]I]','1',result)
            return result
        elif mode =='summon-button':   ## summon-button
            imgs = img[900:951, 370:442]
        elif mode =='member-button':  ## member-button
            imgs = img[78:110, 470:519]
        elif mode =='setaccount-button':  ##158,582,386,609 setaccount-button
            imgs = img[582:609, 158:386]
        elif mode =='delete-button':  ##470,26,512,67  delete-button
            imgs = img[26:67, 470:512]
        elif mode =='agree-button':  ##340,642,437,668  agree-button
            imgs = img[642:668, 340:437]
        img_np = np.array(imgs)
        frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        cv2.imwrite('.'+tmp_grab_path+'checkPoint.jpg', frame)
        if mode is not None and coordinate != [0,5,0,5]:
            imgs = img[coordinate[1]:coordinate[3], coordinate[0]:coordinate[2]]
            img_np = np.array(imgs)
            frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
            cv2.imwrite('.'+tmp_grab_path+mode+'.jpg', frame)

    def Grab_Charactor_Star(self, img):
        coordinate = [[79,452,145,468],[193,452,259,468],[307,452,373,468],[421,452,487,468],
                    [136,602,202,618],[250,602,316,618],[364,602,430,618],
                    [79,752,145,768],[193,752,259,768],[307,752,373,768],[421,752,487,768],
                    [136,902,202,918],[250,902,316,918],[364,902,430,918]
                ]
        tmp_grab_path = r'/image/openCV_Img/'
        for i,star in enumerate(coordinate, 1):
            #print('擷取第{}隻'.format(i))
            imgs = img[star[1]:star[3], star[0]:star[2]]
            img_np = np.array(imgs)
            frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
            cv2.imwrite(f'.{tmp_grab_path}{i}.jpg', frame)
        time.sleep(1)

    # TODO: 此function應該放在controller內, 上下兩段也應該拆開寫
    def Recognize_Img(self,mode='None'):
        img_Path = r'./image/openCV_Img/'
        if mode == 'star':
            LOG.info('判斷五星角色數量')
            print('開始判斷五星角色數量')
            img_Sample = cv2.imread(img_Path+'five_Star11.png',0)
            starNumber = 0
            for i in range(1,15):
                img_Compare = cv2.imread(img_Path+str(i)+'.jpg',0)
                score = compare_ssim(img_Sample,img_Compare)
                #LOG.info('第 {} 隻為五星的相似度為 {}%'.format(i,round(score*100,2)))
                #print('第 {} 隻為五星的相似度為 {}%'.format(i,round(score*100,2)))
                if score > 0.85:
                    starNumber = starNumber +1
            LOG.info('總共抽到 {} 隻五星角色'.format(starNumber))
            print('總共抽到 {} 隻五星角色'.format(starNumber))
            return starNumber
        
        img_Sample = cv2.imread(img_Path+mode+'.png',0)
        if img_Sample is None:
            img_Sample = cv2.imread(img_Path+mode+'.jpg',0)
        img_Compare = cv2.imread(img_Path+'checkPoint'+'.jpg',0)
        #img_Compare=cv2.resize(img_Compare,img_Sample.shape)
        (H, W) = img_Sample.shape
        # to resize and set the new width and height 
        img_Compare = cv2.resize(img_Compare, (W, H))
        score = compare_ssim(img_Sample,img_Compare)
        if score >= 0.95:
            score = round(score*100,2)
            LOG.info('相似度: {}%, 判定成功'.format(score))
            print('相似度: {}%, 判定成功'.format(score))
            return True
        return False