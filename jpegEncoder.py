from PIL import Image
import numpy as np
import math
import huffman as H
import sys

#亮度量化矩阵和色度量化矩阵
lightQ = np.array([[16,11,10,16,24,40,51,61],
[12,12,14,19,26,58,60,55],
[14,13,16,24,40,57,69,56],
[14,17,22,29,51,87,80,62],
[18,22,37,56,68,109,103,77],
[24,35,55,64,81,104,113,92],
[49,64,78,87,103,121,120,101],
[72,92,95,98,112,100,103,99]])
colorQ = np.array([[17,18,24,47,99,99,99,99],
[18,21,26,66,99,99,99,99],
[24,26,56,99,99,99,99,99],
[47,66,99,99,99,99,99,99],
[99,99,99,99,99,99,99,99],
[99,99,99,99,99,99,99,99],
[99,99,99,99,99,99,99,99],
[99,99,99,99,99,99,99,99]])

width,height = 0,0

#存储结构：底层单位为8*8的np.array，上一层是MCU，即[YYYYCbCr]，再上一层为MCU数
# 因此存储结构为一个MCU列表，每个表项为[Y,Y,Y,Y,Cb,Cr]这样的形式存储，每个元素是一个8*8的np.array
in_file = sys.argv[1]

#模块1，读取图片，并进行二次采样
im = Image.open(in_file)
width,height = im.size
im = im.convert("YCbCr")
x,y = 0,0

mcuList = [] #用来存放mcu的列表
while x<=width and y<=height:
    y00,y01,y10,y11 = np.array((8,8)),np.array((8,8)),np.array((8,8)),np.array((8,8))
    cb,cr = np.array((8,8)),np.array((8,8))
    for i in range(x,x+16):
        for j in range(y,y+16):
            #填充
            if x>width or y>height:
                element = 0
            else:
                element = im.getpixel((i,j))
            inline_x,inline_y = i-x,j-y #内部坐标转换
            #按照位置写入4个Y中
            if inline_x<8:
                if inline_y<8:
                    y00[inline_x,inline_y] = element[0]
                else:
                    y10[inline_x,inline_y-8] = element[0]
            else:
                if inline_y<8:
                    y01[inline_x-8,inline_y] = element[0]
                else:
                    y11[inline_x-8,inline_y-8] = element[0]
            #检查当前元素是否能够写入Cb或Cr
            if inline_x % 2 == 0:
                if inline_y % 2 == 0:
                    cb[inline_x//2,inline_y//2] = element[1]
                else:
                    cr[inline_x//2,inline_y//2] = element[2]
    mcuList.append([y00,y01,y10,y11,cb,cr])

#模块2
cFunc = lambda x: math.sqrt(2)/2 if x==0 else 1

