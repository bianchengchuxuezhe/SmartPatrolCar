本项目需要预装miniconda3 来配置对应的虚拟环境


请注意，操控小车的树莓派和人脸识别并报警的树莓派是2个不同的树莓派

以下为人脸识别部分的说明：

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



在树莓派本地创建存放图片的路径/home/pi/Desktop/pic/
在树莓派本地创建存放位置信息的路径/home/pi/Desktop/pos/
在树莓派本地创建存放时间信息的路径/home/pi/Desktop/time/

之后在树莓派内运行该代码即可实现功能

