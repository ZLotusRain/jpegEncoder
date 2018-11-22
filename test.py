import matplotlib.pyplot as plt
import os
from PIL import Image

os.chdir('C:\\Users\\wtysos11\\Desktop\\test')
im = Image.open("source1.jpg")
xx = [i for i in range(256)]
yy = [0 for i in range(256)]
for i in range(im.size[0]):
    for j in range(im.size[1]):
        yy[im.getpixel((i,j))[2]] += 1



plt.bar(xx,yy)
plt.xlabel("gray number")
plt.ylabel("times")
plt.title("hist of gray")
plt.show()

originStr = "IMG_20181106_{0}.jpg"
num = [155314,155047,154846,155356,155659,155906,155940,183006,204622,204801,205047,205353,205708,205446,205918]
imList = [originStr.format(i) for i in num]
for n,imPath in enumerate(imList):
    im = Image.open(imPath)     
    im = im.resize((640,480))
    im.save("originGraph{}.bmp".format(n))

import os
import math

import numpy as np
os.chdir("C:\\Users\\wtysos11\\Desktop")
import calculate
height = 8
width = 8

# 颜色转换（RGB转YIQ或YUV空间）和色彩二度采样（按书中说法，JPEG进行二次采样采用4:2:0的方案）
# pic[j][i] 为pic中第j行第i列（横向为x轴，纵向为y轴）
pic = np.array([[200,202,189,188,189,175,175,175],
[200,203,198,188,189,182,178,175],
[203,200,200,195,200,187,185,175],
[200,200,200,200,197,187,187,187],
[200,205,200,200,195,188,187,175],
[200,200,200,200,200,190,187,175],
[205,200,199,200,191,187,187,175],
[210,200,200,200,188,185,187,186]])

# 二维DCT变换
M = 8
N = 8
f = np.array(calculate.makeEmptyList(8,8))
for u in range(8):
    for v in range(8):
        sum = 0
        for i in range(8):
            for j in range(8):
                sum+=math.cos(math.pi*(2*i+1)*u/(2*M))*math.cos(math.pi*v*(2*j+1)/(2*N))*(pic[j][i]-128)
        f[v][u] = round(2 * sum *calculate.calculate(u)*calculate.calculate(v)/math.sqrt(M*N))

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
# 量化
F = np.divide(f,lightQ)
for i in range(M):
    for j in range(N):
        F[i][j] = round(F[i][j])

# 逆量化 
F = np.multiply(F,lightQ)
M = 8
N = 8
f = np.array(calculate.makeEmptyList(8,8))
for i in range(8):
    for j in range(8):
        sum = 0
        for u in range(8):
            for v in range(8):
                sum+=calculate.calculate(u)*calculate.calculate(v)/4*math.cos(math.pi*(2*i+1)*u/16)*math.cos(math.pi*v*(2*j+1)/16)*F[v][u]
        f[v][u] = round(sum+128)

i,j = 0,0
sum = 0
for u in range(8):
    for v in range(8):
        sum += calculate.calculate(u)*calculate.calculate(v)/4*math.cos(math.pi*(2*i+1)*u/16)*math.cos(math.pi*v*(2*j+1)/16)*F[v][u]

# DPCM和游长编码
## version origin
step = 1
x = 0
y = 0
el = []
print(x,y)
el.append(F[y][x])
while x!=7 or y!=7:
    if step==1:
        print("step1")
        x+=1
        print(x,y)
        el.append(F[y][x])
        while x>0 and y<7:
            x,y = x-1,y+1
            print(x,y)
            el.append(F[y][x])
        
        y+=1
        print(x,y)
        el.append(F[y][x])
        while x<7 and y>0:
            x,y = x+1,y-1
            print(x,y)
            el.append(F[y][x])
        
        if x==6:
            step+=1
    elif step == 2:
        print("step2")
        x+=1
        print(x,y)
        el.append(F[y][x])
        while x>0 and y<7:
            x,y = x-1,y+1
            print(x,y)
            el.append(F[y][x])
        
        x+=1
        print(x,y)
        el.append(F[y][x])
        while x<7 and y>0:
            x,y = x+1,y-1
            print(x,y)
            el.append(F[y][x])
        
        step +=1
    else:
        print("step 3")
        y+=1
        print(x,y)
        el.append(F[y][x])
        while x>0 and y<7:
            x,y = x-1,y+1
            print(x,y)
            el.append(F[y][x])
        
        x+=1
        print(x,y)
        el.append(F[y][x])
        while x<7 and y>0:
            x,y = x+1,y-1
            print(x,y)
            el.append(F[y][x])

encodingsize = len(el)
encodingList = []
num = 1
char = el[0]
for i in range(1,encodingsize):
    if el[i]!=char:
        encodingList.append((char,num))
        char = el[i]
        num = 1
    else:
        num +=1

encodingList.append((char,num))

ac = el[0]
#RLC
rlc = []
num = 0
for i in range(1,encodingsize):
    if el[i]!=0:
        rlc.append((num,el[i]))
        num = 0
    else:
        num+=1

rlc.append((0,0))
## DC系数的哈夫曼编码前篇，将DC系数转为(SIZE,AMPLITUDE)表示
dpcmReady = [150,5,-6,3,-8]
dpcm = []
for ele in dpcmReady:
    if ele>0:
        dpcm.append(bin(ele)[2:])
    else:
        oppose = (1<<(len(bin(ele))-3)) + ele -1
        oppose = bin(oppose)[2:]
        originLength = len(bin(ele))-3
        while len(oppose)<originLength:
            oppose = '0'+oppose
        dpcm.append(oppose)

# 熵编码
import os
os.chdir('C:\\Users\\wtysos11\\Desktop')
from myJpeg import *
im = Image.open("test.jpg")
generateBlocks(im)
implement_dct()
implement_quantize()
dc_code = dc_encoding()
ac_code = ac_encoding()
bitStream = write_file(dc_code,ac_code)
with open('test2.jpg','wb') as f:
    length = f.write(originBin2Hex(bitStream))

# 对EOB的实现问题
# 目前的处理：删除RLC后的(0,0)编码，在最后的时候加上
# 问题：对于EOB的处理是由哈夫曼解码得到的，这样子需要手动在哈夫曼树上加上EOB相关项目，不是特别好
# 其他想法：使用特殊常量表示EOB，通过将EOB插入来实现
# 此时哈夫曼树中有该条目，在最后的时候运用该条目即可