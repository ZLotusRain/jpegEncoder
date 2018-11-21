from PIL import Image
import numpy as np
import math
import huffman as H
blockList = []
originBlockList = []
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
# 规定横向为x轴正方向，纵向向下为y轴正方向
width,height = 0,0
#将PIL.Image转化为YCbCr空间，并切片
def generateBlocks(im):
# 输入图像的长宽必须为8的整数倍
# 后面将会进行二次采样，对于超出的部分进行0值填充，然后统一进行切分
    global width,height
    global blockList,originBlockList
    width,height = im.size
    blocksNumber = height//8*width//8   #calculating total block number
    im = im.convert("YCbCr")
    x,y = 0,0
    for i in range(blocksNumber):
        block = np.zeros((3,8,8))
        for j in range(x,x+8):
            for k in range(y,y+8):
                for color in range(3):
                    block[color][k-y][j-x] = im.getpixel((j,k))[color]
        blockList.append(block)
        originBlockList.append(block.copy())
        x+=8
        if x>=width:
            x = 0
            y += 8

# DCT变换的辅助函数
def cFunc(x):
    if x == 0:
        return math.sqrt(2)/2
    else:
        return 1

#进行DCT变化
def implement_dct():
    global blockList
    M = 8
    N = 8
    f = np.zeros((8,8))
    for block in blockList:
        for color in range(3):
            for u in range(8):
                for v in range(8):
                    sum = 0
                    for i in range(8):
                        for j in range(8):
                            sum+=math.cos(math.pi*(2*i+1)*u/(2*M))*math.cos(math.pi*v*(2*j+1)/(2*N))*(block[color][j][i]-128)
                    f[v][u] = round(2 * sum *cFunc(u)*cFunc(v)/math.sqrt(M*N))
            
            for u in range(8):
                for v in range(8):
                    block[color][v][u] = f[v][u] #是否可以用block[color]=f?

#量化
def implement_quantize():
    for block in blockList:
        for color in range(3):
            if color == 0:
                #Y
                block[color] = np.divide(block[color],lightQ)
                for i in range(8):
                    for j in range(8):
                        block[color][i][j] = round(block[color][i][j])
            else:
                #CbCr
                block[color] = np.divide(block[color],colorQ)
                for i in range(8):
                    for j in range(8):
                        block[color][i][j] = round(block[color][i][j])

#逆量化和IDCT后
def counting_distortion():
    distortion = blockList.copy()
    #逆量化
    for block in distortion:
        for color in range(3):
            if color == 0:
                #Y
                block[color] = np.multiply(block[color],lightQ)
            else:
                #CbCr
                block[color] = np.multiply(block[color],colorQ)
    M = 8
    N = 8
    f = np.zeros((8,8))
    for block in distortion:
        for color in range(3):
            for i in range(8):
                for j in range(8):
                    sum = 0
                    for u in range(8):
                        for v in range(8):
                            sum+=cFunc(u)*cFunc(v)/4*math.cos(math.pi*(2*i+1)*u/(2*M))*math.cos(math.pi*v*(2*j+1)/(2*N))*block[color][v][u]
                    f[j][i] = round(sum+128)
            
            for u in range(8):
                for v in range(8):
                    block[color][v][u] = f[v][u] #是否可以用block[color]=f?

    total_distortion = 0
    for (k,block) in enumerate(distortion):
        for color in range(3):
            for i in range(8):
                for j in range(8):
                    total_distortion += abs(distortion[k][color][j][i] - originBlockList[k][color][j][i])
    print(total_distortion/(width*height*3))

# 接受一个value，返回一个二元组(size,amplitude)
def encoding_dpcm(value):
    value = int(value)
    if value >= 0:
        return (len(bin(value))-2,bin(value)[2:])
    else:
        oppose = (1<<(len(bin(value))-3)) + value -1
        oppose = bin(oppose)[2:]
        oppose = oppose.zfill(len(bin(value))-3)
        return (len(oppose),oppose)

# 接受一个block，进行DC部分的处理，获得三个DC的列表，计算差值，编码并计算哈夫曼树，返回DPCM后的dc编码
def dc_encoding():
    global huffman_dc_lu,huffman_dc_co #全局保存哈夫曼树

    dc = [[],[],[]]
    for block in blockList:
        for color in range(3):
            dc[color].append(block[color][0][0]) #将每个DC分量压入列表中

    base = [dc[0][0],dc[1][0],dc[2][0]]
    for i in range(1,len(dc[0])):
        for color in range(3):
            dc[color][i] = dc[color][i] - base[color] #计算差值
            base[color] += dc[color][i] #更新base

    # 对DC分量进行熵编码
    for i in range(3): #计算DPCM编码
        dc[i] = list(map(lambda x:encoding_dpcm(x),dc[i])) 
    # 提取所有的size进行哈夫曼编码，将生成的哈夫曼树保存
    dc_size = [[],[],[]]
    for color in range(3):
        for size,amplitudue in dc[color]:
            dc_size[color].append(size)

    huffman_dc_lu = H.HuffmanTree(dc_size[0])
    huffman_dc_co = H.HuffmanTree(dc_size[1]+dc_size[2])
    return dc
    
# AC用的辅助函数，从8*8块中按顺序提取出数据并编码，然后去除DC分量
# F为一个颜色的8*8块，返回一个二元组列表，二元组为AC的游长编码形式（runlength,value）
def ac_getCode(F):
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


# AC从每个block中提取出剩余的63个AC分量，用全局的AC分量生成哈夫曼树
# 两个哈夫曼树在全局情况下保存，得到一个((runlength,size),amplitude)列表，列表以blockNum*color的两重列表保存
def ac_encoding():
    global huffman_ac_lu,huffman_ac_co #全局保存哈夫曼树

    ac_coding = [] #全局编码存放
    ac_size_lu = [] #AC的(size,amplitude)二元组的size的存放，用于哈夫曼编码
    ac_size_co = [] #同上，Cb和Cr的size的存放

    for block in blockList:
        ac_block_coding = []
        for color in range(3):
            RLC = ac_getCode(block[color]) #将会拿到游长编码形式(runlength,size)

            # 对AC分量进行熵编码
            dpcm = []
            for runlength,value in RLC: #对得到的size进行DPCM编码，将得到的size作为哈夫曼编码的一项使用
                dpcm_code = encoding_dpcm(value)
                symbol1 = bin(runlength)[2:].zfill(4)+bin(dpcm_code[0])[2:].zfill(4)
                if color == 0:
                    ac_size_lu.append(symbol1)
                else:
                    ac_size_co.append(symbol1)
                dpcm.append((symbol1,dpcm_code[1])) #(Symbol1,Symbol2)
            #在末尾插入EOB
            dpcm.append(('00000000','')) 
            if color == 0:
                ac_size_lu.append('00000000')
            else:
                ac_size_co.append('00000000')
            #向block单位中加入，得到blockList
            ac_block_coding.append(dpcm)
        ac_coding.append(ac_block_coding)
    
    huffman_ac_lu = H.HuffmanTree(ac_size_lu)
    huffman_ac_co = H.HuffmanTree(ac_size_co)
    return ac_coding

#接受值和长度
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

#排序算法，对outputHuffman进行排序，长度优先，同一长度字典序优先

#返回二进制位流
def write_file(dc_code,ac_code):
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
    for (blockNum,block) in enumerate(blockList):
        for color in range(3):
            #DC编码
            if color == 0:
                dc_dict = huffman_dc_lu.huffman
            else:
                dc_dict = huffman_dc_co.huffman
            
            codedStream += dc_dict[dc_code[color][blockNum][0]] + dc_code[color][blockNum][1]
            #AC编码
            ac_codeList = ac_code[blockNum][color]
            if color == 0:
                ac_dict = huffman_ac_lu.huffman
            else:
                ac_dict = huffman_ac_co.huffman
            
            for (sym1,sym2) in ac_codeList:
                codedStream += ac_dict[sym1] + sym2
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

#对于一串二进制字符串，将其转换为十六进制
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

import os
os.chdir('C:\\Users\\wtysos11\\Desktop')

im = Image.open("test.jpg")
generateBlocks(im)

implement_dct()
implement_quantize()

# 复制后进行逆量化和IDCT，计算失真率
counting_distortion()

dc_code = dc_encoding()
ac_code = ac_encoding()
bitStream = write_file(dc_code,ac_code)
print('计算压缩率:')
print(len(bitStream)/(24*width*height)) #JPEG位流相对于每个像素24位的RGB图像的压缩率
'''
with open('test2.jpg','wb') as f:
    length = f.write(originBin2Hex(bitStream))
'''