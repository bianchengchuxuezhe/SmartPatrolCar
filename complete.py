# -*- coding: utf-8 -*-

#人体检测及人脸识别所需库
import RPi.GPIO as GPIO
import time
import picamera
from aip import AipFace
import requests
import base64

#GPS所需库
#添加第三方库路径
import sys
#pip的库所在位置
sys.path.append('/home/pi/.local/lib/python2.7/site-packages') 
import serial
import pynmea2 

#上传图片所需库
import paramiko

#写文件所需库
import codecs

#转换坐标所需库
import json


#人体检测及人脸识别 变量
APP_ID ="16699062"
URL="https://aip.baidubce.com/rest/2.0/face/v2/verify"
API_KEY="rzeWi36tz4zp22Hn0AkwK9vA"
API_SECRET="dVxWMCVGUUMOBabGIgPaailda38q4t2h"
imageType="BASE64"
groupIdList = "try1"
client = AipFace(APP_ID, API_KEY, API_SECRET)

#上传 变量
global s
s=0
host_ip='182.92.86.34' #不需要带端口
username='omada'
password='bupt2018qa'

global curtime

def init():    #设置不显示警告    
   GPIO.setwarnings(False)    
#设置读取面板针脚模式   
   GPIO.setmode(GPIO.BOARD)    
#设置读取针脚标号   
   GPIO.setup(40,GPIO.IN)
   
def detect():    
    while True:        
        if GPIO.input(40) == True:
            camera.start_preview()
            alert()        
        else:           
            continue        
        
def alert():
    #curtime记录拍摄时间
    curtime = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))  
    print (curtime + " Someone is coming!" )   #根据时间获取图像     
    camera.capture('/home/pi/Desktop/pic/1.jpg') #声明摄像头
    time.sleep(0.3)
    camera.capture('/home/pi/Desktop/pic/2.jpg')
    token_get()
    while True:
        img=transimage('/home/pi/Desktop/pic/1.jpg')
        decide=go_api(img,'/home/pi/Desktop/pic/1.jpg',curtime)
        if decide==1:
            break
        img=transimage('/home/pi/Desktop/pic/2.jpg')
        decide=go_api(img,'/home/pi/Desktop/pic/2.jpg',curtime)
        break
    camera.stop_preview()
    time.sleep(3)
    
def token_get():
    url="https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=rzeWi36tz4zp22Hn0AkwK9vA&client_secret=dVxWMCVGUUMOBabGIgPaailda38q4t2h&"
    data=requests.get(url).json()
    return data['access_token']

def transimage(local_pic):
    f = open(local_pic,'rb')
    img = base64.b64encode(f.read())
    return img

def go_api(image,local_pic,curtime):
    result = client.search(str(image, 'utf-8'), imageType, groupIdList);
    if result['error_msg'] == 'SUCCESS':#如果成功了
        group=result['result']
        name = result['result']['user_list'][0]['user_id']#获取名字
        score = result['result']['user_list'][0]['score']#获取相似度
        if score > 65:#如果相似度大于70
            print("黑名单人员，请立刻驱逐",name) 
            global s                
            #上传图片
            remote_pic_dir='/mnt/omada/presentation/static/carpos/'
            remote_pic_name = '%d.jpg'%(s+1)
            remote_pic=remote_pic_dir+remote_pic_name
            sftp_put(host_ip, username, password, local_pic, remote_pic)               
            #上传位置信息
            (lon,lat) = GPS()
            local_posTXT='/home/pi/Desktop/pos/'+'%d.txt'%s
            remote_posTXT='/home/www/root/static/carpos/pos/'+'%d.txt'%s
            remote_posTXT='/mnt/omada/presentation/static/carpos/pos.txt'
            posDoc(lon,lat,local_posTXT)                
            sftp_put(host_ip, username, password, local_posTXT, remote_posTXT)
            #上传时间信息
            local_timeTXT='/home/pi/Desktop/time/'+'%d.txt'%s
            remote_timeTXT='/home/www/root/static/carpos/time/'+'%d.txt'%s
            remote_timeTXT='/mnt/omada/presentation/static/carpos/time.txt'
            timeDoc(curtime,local_timeTXT)
            sftp_put(host_ip, username, password, local_timeTXT, remote_timeTXT)
            #修改s对应下一组
            s=(s+1)%3#仅存在3组数据名称分别为0 1 2.jpg/txt
            return 1
                            
        else:
            print("认证失败",score)
            return 0

def GPS():
    ser = serial.Serial("/dev/ttyUSB0",9600,timeout=5)#timeout=5s
    while True:
        line = str(ser.readline())[2:-5]
        if line.startswith('$GPRMC'):
            #print("i'm in if")
            rmc = pynmea2.parse(line)
            lon_du = rmc.lon[:-7]
            lat_du = rmc.lat[:-7]
            lon_fen = rmc.lon[-7:]
            lat_fen = rmc.lat[-7:]
            lon = float(lon_du) + float(lon_fen)/60 
            lat = float(lat_du) + float(lat_fen)/60 
            (lon_change,lat_change) = positionChange(lon,lat)#转为百度坐标
            lon_dir = rmc.lon_dir
            lat_dir = rmc.lat_dir
            position = "Latitude: %f°%s Longitude: %f°%s" %(lat_change,lat_dir,lon_change,lon_dir)
            print(position)
            return (lon_change,lat_change)
    
# put单个文件
def sftp_put(host_ip, username, password, local_pic, remote_pic):
    t = paramiko.Transport(sock=(host_ip, 22))
    t.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.put(local_pic, remote_pic)
    t.close()       

#坐标转换    
def positionChange(XX,YY):  #输出为tuple of float(经度，纬度)
    url1='http://api.map.baidu.com/geoconv/v1/?coords='+str(XX)+','+str(YY)+'&from=1&to=5&ak=zvEOHBNPi6zMDwYF3nx1CDGS1s14tiaf'
    req=requests.get(url1)
    content= req.content
    data=json.loads(content)
    result=data['result']
    str_temp=result[0]         
    longitude=str_temp['x']
    latitude=str_temp['y']
    return (longitude,latitude)

#创建本地位置文档
def posDoc(lon,lat,local_posTXT):
    fh = codecs.open(local_posTXT,"r+","utf-16")
    fh.write(str(lon)+'\n') #第一行经度
    fh.write(str(lat)+'\n') #第二行纬度
    fh.close()

#创建本地时间文档
def timeDoc(curtime,local_timeTXT):
    fh = codecs.open(local_timeTXT,"r+","utf-16")
    fh.write(curtime+'\n')
    fh.close()
    
    
if __name__ == '__main__':
    camera = picamera.PiCamera()
    init()
    detect()
    GPIO.cleanup()
    

    
