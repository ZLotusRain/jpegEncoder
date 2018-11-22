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

#存储结构：底层单位为8*8的np.array，上一层是MCU，即[YYYYCbCr]，再上一层为MCU数
# 因此存储结构为一个MCU列表，每个表项为[Y,Y,Y,Y,Cb,Cr]这样的形式存储，每个元素是一个8*8的np.array

#模块1，读取图片，并进行二次采样
def generateMCU():
    global mcuList
    in_file = sys.argv[1]
    im = Image.open(in_file)
    width,height = im.size
    im = im.convert("YCbCr")
    x,y = 0,0
    outerWidth,outerHeight = width,height
    if width%16 !=0:
        outerWidth = outerWidth + 16 - outerWidth%16
    if height%16!=0:
        outerHeight = outerHeight + 16 - outerHeight%16
    outerWidth-=1
    outerHeight-=1
    mcuList = [] #用来存放mcu的列表
    while x<outerWidth and y<outerHeight:
        y00,y01,y10,y11 = np.zeros((8,8),int),np.zeros((8,8),int),np.zeros((8,8),int),np.zeros((8,8),int)
        cb,cr = np.zeros((8,8),int),np.zeros((8,8),int)
        for i in range(x,x+16):
            for j in range(y,y+16):
                if i>=width or j>=height:#填充
                    element = (0,0,0)
                else:
                    element = im.getpixel((i,j))
                inline_x,inline_y = i-x,j-y #内部坐标转换
                #按照位置写入4个Y中
                if inline_x<8:
                    if inline_y<8:
                        y00[inline_y,inline_x] = element[0]
                    else:
                        y10[inline_y-8,inline_x] = element[0]
                else:
                    if inline_y<8:
                        y01[inline_y,inline_x-8] = element[0]
                    else:
                        y11[inline_y-8,inline_x-8] = element[0]
                #检查当前元素是否能够写入Cb或Cr
                if inline_x % 2 == 0:
                    if inline_y % 2 == 0:
                        cb[inline_y//2,inline_x//2] = element[1]
                    else:
                        cr[inline_y//2,inline_x//2] = element[2]
        mcuList.append([y00,y01,y10,y11,cb,cr])
        x+=16
        if x >= outerWidth:
            x = 0
            y += 16

generateMCU()

#模块2， 进行DCT变化
cFunc = lambda x: math.sqrt(2)/2 if x==0 else 1
def implementDCT():
    global mcuList
    for mcu in mcuList:
        for (n,block) in enumerate(mcu):
            f = np.zeros((8,8))
            for u in range(8):
                for v in range(8):
                    sum = 0
                    for i in range(8):
                        for j in range(8):
                            sum+=math.cos(math.pi*(2*i+1)*u/16)*math.cos(math.pi*v*(2*j+1)/16)*(block[j][i]-128)
                    f[v][u] = round(sum *cFunc(u)*cFunc(v)/4)
            mcu[n] = f

implementDCT()

#模块3，进行量化
def implement_quantize():
    global mcuList
    for mcu in mcuList:
        for (n,block) in enumerate(mcu):
            if n<4:
                mcu[n] = np.divide(block,lightQ)
                for i in range(8):
                    for j in range(8):
                        mcu[n][i][j] = round(mcu[n][i][j])
            else:
                mcu[n] = np.divide(block,colorQ)
                for i in range(8):
                    for j in range(8):
                        mcu[n][i][j] = round(mcu[n][i][j])

implement_quantize()
#模块4，进行DPCM编码的函数
def encoding_dpcm(value):
    value = int(value)
    if value >= 0:
        return (len(bin(value))-2,bin(value)[2:])
    else:
        oppose = (1<<(len(bin(value))-3)) + value -1
        oppose = bin(oppose)[2:]
        oppose = oppose.zfill(len(bin(value))-3)
        return (len(oppose),oppose)

# 模块5，按照MCU顺序提取DC分量并插入到列表中
dcCodingList = []
baseline = 0
for mcu in mcuList:
    mcuDcList = []
    for block in mcu:
        mcuDcList.append(block[0][0]-baseline)
        baseline = block[0][0]
    dcCodingList.append(mcuDcList)

# 模块6，对DC分量进行DPCM编码
for dclist in dcCodingList:
    for (n,dcvalue) in enumerate(dclist):
        dclist[n] = encoding_dpcm(dcvalue)

#模块7，对DC分量进行熵编码
dc_size_lu,dc_size_co = [],[]
for dclist in dcCodingList:
    for (num,(size,amplitude)) in enumerate(dclist):
        if num<4:
            dc_size_lu.append(size)
        else:
            dc_size_co.append(size)

huffman_dc_lu = H.HuffmanTree(dc_size_lu)
huffman_dc_co = H.HuffmanTree(dc_size_co)

#模块8，取得8*8块的游长编码用的函数（注：RLC中不包含EOB）
def ac_getRLC(F):
    step = 1
    x = 0
    y = 0
    el = []
    el.append(F[y][x])
    while x!=7 or y!=7:
        if step==1:
            x+=1
            el.append(F[y][x])
            while x>0 and y<7:
                x,y = x-1,y+1
                el.append(F[y][x])
            
            y+=1
            el.append(F[y][x])
            while x<7 and y>0:
                x,y = x+1,y-1
                el.append(F[y][x])
            
            if x==6:
                step+=1
        elif step == 2:
            x+=1
            el.append(F[y][x])
            while x>0 and y<7:
                x,y = x-1,y+1
                el.append(F[y][x])
            
            x+=1
            el.append(F[y][x])
            while x<7 and y>0:
                x,y = x+1,y-1
                el.append(F[y][x])
            
            step +=1
        else:
            y+=1
            el.append(F[y][x])
            while x>0 and y<7:
                x,y = x-1,y+1
                el.append(F[y][x])
            
            x+=1
            el.append(F[y][x])
            while x<7 and y>0:
                x,y = x+1,y-1
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
    #RLC
    rlc = []
    num = 0
    for i in range(1,encodingsize):
        if el[i]!=0:
            while num > 15: #因为后面哈夫曼编码的问题，runlength最大只能为4位，不能表示长度大于15的零串
                rlc.append((15,0))
                num -= 15
            rlc.append((num,el[i]))
            num = 0
        else:
            num+=1

    return rlc

# 模块9，取得RLC
acCodingList = []
for mcu in mcuList:
    mcuAcList = []
    for block in mcu:
        rlc = ac_getRLC(block)
        mcuAcList.append(rlc)
    acCodingList.append(mcuAcList)
# 模块10，对RLC的runlength进行游长编码
for acMcu in acCodingList:
    for (m,acRLC) in enumerate(acMcu):
        dpcm = []
        for runlength,value in acRLC: #对得到的size进行DPCM编
            dpcm_code = encoding_dpcm(value)
            symbol1 = bin(runlength)[2:].zfill(4)+bin(dpcm_code[0])[2:].zfill(4)
            dpcm.append((symbol1,dpcm_code[1])) #(Symbol1,Symbol2)
        dpcm.append(('00000000',''))#在结尾插入EOB
        acMcu[m] = dpcm

# 模块11，对AC分量的RLC进行熵编码
ac_size_lu,ac_size_co = [],[]
for acMcu in acCodingList:
    for (num,acDpcmCode) in enumerate(acMcu):
        for symbol1,symbol2 in acDpcmCode:
            if num<4:
                ac_size_lu.append(symbol1)
            else:
                ac_size_co.append(symbol1)
                
huffman_ac_lu = H.HuffmanTree(ac_size_lu)
huffman_ac_co = H.HuffmanTree(ac_size_co)

#模块12，二进制读写用辅助函数
#接受值和长度，返回指定长度的二进制字符串
def int2Bit(value,length):
    return bin(value)[2:].zfill(length)

#接受十六进制字符串，转换成长度*4的二进制字符串
def Hex2Bit(heximal):
    bit = ''
    for hex in heximal:
        bit += int2Bit(int(hex,16),4)
    return bit
#返回结构化的define quantize table
def writeDQT():
    dqt_stream = ''
    #亮度量化表
    #write head
    dqt_stream += Hex2Bit('FFDB')#开始符号
    dqt_stream += Hex2Bit('0043')#长度为67字节
    dqt_stream += Hex2Bit('00')#QT号=0，QT精度=8bits
    for i in range(8):
        for j in range(8):
            dqt_stream += int2Bit(lightQ[i][j],8)
    #颜色量化表
    #write head
    dqt_stream += Hex2Bit('FFDB')#开始符号
    dqt_stream += Hex2Bit('0043')#长度为67字节
    dqt_stream += Hex2Bit('01')#QT号=1，QT精度=8bits
    for i in range(8):
        for j in range(8):
            dqt_stream += int2Bit(colorQ[i][j],8)
    return dqt_stream

#DC产生哈夫曼表的函数，接受一个哈夫曼树，返回0/1字符串流
def DC_DHT_writer(huffmantree,id):
    # 生成流
    outputHuffman = huffmantree.outputHuffman
    reverseList = huffmantree.reverseHuffman

    flow = ''
    #冒泡排序得到正常的outputHuffman
    output_len = len(outputHuffman)
    for i in range(output_len):
        for j in range(output_len-i-1):
            if(len(outputHuffman[j])>len(outputHuffman[j+1])):
                outputHuffman[j],outputHuffman[j+1] = outputHuffman[j+1],outputHuffman[j]
            elif(len(outputHuffman[j])==len(outputHuffman[j+1]) and outputHuffman[j]>outputHuffman[j+1]):
                outputHuffman[j],outputHuffman[j+1] = outputHuffman[j+1],outputHuffman[j]
    #对各个长度进行统计
    countDict = {}
    totalLength = 0
    for i in range(16):
        countDict[i] = 0
    for huff in outputHuffman:
        countDict[len(huff)-1] +=1 #长度减1表示，第一个8位编号为0，存放长度为1，
        totalLength +=1

    totalLength += 2+1+16 #2字节的长度，1字节的表ID和表类型，16字节的不同码字数量
    #write head
    flow += Hex2Bit('FFC4')
    flow += int2Bit(totalLength,16)
    flow += Hex2Bit(id)#DC亮度表
    for k,v in countDict.items():
        flow += int2Bit(v,8)
    
    #DC的哈夫曼表是对DPCM的size进行编码，得到的key是int
    for huffmanStr in outputHuffman:
        huffmanValue = reverseList[huffmanStr]
        flow += int2Bit(huffmanValue,8)
    return flow

#AC，同上
def AC_DHT_writer(huffmantree,id):
    # 生成流
    outputHuffman = huffmantree.outputHuffman
    reverseList = huffmantree.reverseHuffman

    flow = ''
    #冒泡排序得到正常的outputHuffman
    output_len = len(outputHuffman)
    for i in range(output_len):
        for j in range(output_len-i-1):
            if(len(outputHuffman[j])>len(outputHuffman[j+1])):
                outputHuffman[j],outputHuffman[j+1] = outputHuffman[j+1],outputHuffman[j]
            elif(len(outputHuffman[j])==len(outputHuffman[j+1]) and outputHuffman[j]>outputHuffman[j+1]):
                outputHuffman[j],outputHuffman[j+1] = outputHuffman[j+1],outputHuffman[j]

    #对各个长度进行统计
    countDict = {}
    totalLength = 0
    for i in range(16):
        countDict[i] = 0
    for huff in outputHuffman:
        countDict[len(huff)-1] +=1
        totalLength +=1

    totalLength += 2+1+16 #2字节的长度，1字节的表ID和表类型，16字节的不同码字数量

    #write head
    flow += Hex2Bit('FFC4')
    flow += int2Bit(totalLength,16)
    flow += Hex2Bit(id)#AC表
    for k,v in countDict.items():
        flow += int2Bit(v,8)
    
    #AC的哈夫曼表是对symbol1进行编码，得到的key是8位的0/1字符串
    for huffmanStr in outputHuffman:
        huffmanValue = reverseList[huffmanStr]
        if huffmanValue == 0:
            huffmanValue = '00000000'
        flow += huffmanValue
    return flow


#返回结构化的define huffman table
def writeDHT():
    dht_stream = ''
    #4个哈夫曼表
    # 第一个，DC亮度表
    dht_stream += DC_DHT_writer(huffman_dc_lu,'00')
    # 第二个，DC颜色表
    dht_stream += DC_DHT_writer(huffman_dc_co,'01')
    # 第三个，AC亮度表
    dht_stream += AC_DHT_writer(huffman_ac_lu,'10')
    # 第四个，AC颜色表
    dht_stream += AC_DHT_writer(huffman_ac_co,'11')
    return dht_stream

#返回二进制位流
def write_file(dcCodingList,acCodingList):
    bitstream = ''
    # write SOI
    bitstream += Hex2Bit('FFD8')
    # write APP0
    bitstream += Hex2Bit('FFE0')
    bitstream += Hex2Bit('00104A46494600010101006000600000')
    # write DQT
    bitstream += writeDQT()
    # write SOF0
    bitstream += Hex2Bit('FFC0')
    bitstream += Hex2Bit('0011') #17字节长
    bitstream += Hex2Bit('08') #精度8bit
    bitstream += int2Bit(height,16)
    bitstream += int2Bit(width,16)
    bitstream += Hex2Bit('03012200021101031101')
    # write DHT
    bitstream += writeDHT()
    # write SOS
    bitstream += Hex2Bit('FFDA')
    bitstream += Hex2Bit('000C03010002110311003F00')
    # write data
    codedStream = ''
    for (mcuID,dcmcu) in enumerate(dcCodingList):
        acmcu = acCodingList[mcuID]
        for (blockID,dcValue) in enumerate(dcmcu):
            acValue = acmcu[blockID]
            #DC编码
            if blockID<4:
                dc_dict = huffman_dc_lu.huffman
            else:
                dc_dict = huffman_dc_co.huffman
            codedStream += dc_dict[dcValue[0]]+dcValue[1]

            #AC编码
            if blockID<4:
                ac_dict = huffman_ac_lu.huffman
            else:
                ac_dict = huffman_ac_co.huffman
            
            for (sym1,sym2) in acValue:
                codedStream += ac_dict[sym1]+sym2
    while len(codedStream) % 8 != 0: #压缩数据末尾补0
        codedStream += '0'
    
    # 对于FF插入00
    point = 0
    while point<len(codedStream):
        if codedStream[point:point+8] == '11111111':
            if point+8<len(codedStream):
                codedStream = codedStream[:point+8]+'00000000'+codedStream[point+8:]
                point +=8
            else:
                codedStream+='00000000'
        point+=8

    bitstream+=codedStream+Hex2Bit('FFD9')
    return bitstream

# 模块13 导出文件用
#对于一串二进制字符串，将其转换为十六进制（二进制形式）字符串
def originBin2Hex(bStr):
    point = 0
    result = b''
    while point < len(bStr):
        hex1,hex2 = '',''
        if point+8 >= len(bStr):
            if point+4 >= len(bStr):
                hex1 = bStr[point:]
                while len(hex1) < 4:
                    hex1 +='0'
                hex2 = '0000'
            else:
                hex1 = bStr[point:point+4]
                hex2 = bStr[point+4:]
                while len(hex2) < 4:
                    hex2+='0'
        else:
            hex1 = bStr[point:point+4]
            hex2 = bStr[point+4:point+8]
        hex1 = hex(int(hex1,2))[2:]
        hex2 = hex(int(hex2,2))[2:]
        cache = bytes.fromhex(hex1+hex2)
        result += cache
        point += 8
    return result