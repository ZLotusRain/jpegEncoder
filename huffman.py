
#提供哈夫曼树所使用的节点
#属性包括节点的权重，是否为叶节点，左子树在保存列表的位置，右子树在保存列表的位置
class HuffmanNode:
    def __init__(self,weight,isTreenode,left,right,key,position):
        self.weight = weight
        self.isTreenode = isTreenode
        self.rightChild = right
        self.leftChild = left
        self.key = key
        self.position = position #自己存放的位置
        self.huffmanStr = ''
    
#要求1：能够输出符合格式的哈夫曼表
#要求2：能够根据给定的键来输出哈夫曼数据
class HuffmanTree:
    def __init__(self,arr):
        times = {}
        for ele in arr:
            if ele in times:
                times[ele] +=1
            else:
                times[ele] = 1
        if len(times)==1:
            self.huffman = {arr[0]:'0'}
            self.reverseHuffman = {'0':arr[0]}
            self.outputHuffman = ['0']
        else:
            self.store = []
            counting = 0
            for k,v in times.items():
                self.store.append(HuffmanNode(v,True,0,0,k,counting))
                counting +=1 
            doing = self.store.copy()
            list.sort(doing,key = lambda ele: ele.weight,reverse = True) #按照频率降序排序
            while len(doing)>=2:
                left = doing.pop() #左边是最小的
                right = doing.pop() #右边更大一点
                pos = len(self.store)
                huff = HuffmanNode(left.weight+right.weight,False,left.position,right.position,0,pos)
                doing.append(huff)
                self.store.append(huff)
                #更新优先队列
                point = len(doing)-1
                while point > 0:
                    if doing[point].weight>doing[point-1].weight:
                        doing[point],doing[point-1] = doing[point-1],doing[point]
                    else:
                        break
            self.root = doing[0]
            #根据建立好的树生成哈夫曼映射表
            stack = [self.root]
            self.huffman = {}#哈夫曼映射表，根据给定的键映射值
            self.reverseHuffman = {}
            self.outputHuffman = []
            while len(stack)>0:
                point = stack.pop()
                if point.isTreenode:
                    self.huffman[point.key] = point.huffmanStr
                    self.reverseHuffman[point.huffmanStr] = point.key
                    self.outputHuffman.append(point.huffmanStr)
                else:
                    leftHuff = '0'
                    rightHuff = '1'
                    left = self.store[point.leftChild]
                    right = self.store[point.rightChild]
                    # 考虑到如果哈夫曼编码长度不一致，后一个哈夫曼编码将由前一个哈夫曼编码+1后补零产生
                    #如果孩子有一个为叶节点，一个不是，则叶节点必须在左边，不然解码的时候会出错。
                    '''
                    if not left.isTreenode and right.isTreenode: 
                        leftHuff,rightHuff = rightHuff,leftHuff
                    '''
                    left.huffmanStr = point.huffmanStr+leftHuff
                    stack.append(left)
                    
    
                    right.huffmanStr = point.huffmanStr+rightHuff
                    stack.append(right)

#接受值和长度
def int2Bit(value,length):
    return bin(value)[2:].zfill(length)

#接受十六进制字符串，转换成长度*4的二进制字符串
def Hex2Bit(heximal):
    bit = ''
    for hex in heximal:
        bit += int2Bit(int(hex,16),4)
    return bit

def getStd(std_dict):
    outputHuffman = []
    huffman = {}
    reverseHuffman = {}
    baseline = 0
    for (length,huffman_list) in std_dict.items():
        for hexNum in huffman_list:
            #基准对齐
            huffmanStr = bin(baseline)[2:].zfill(length)
            #填充
            key = Hex2Bit(hexNum)
            outputHuffman.append(huffmanStr)
            huffman[key] = huffmanStr
            reverseHuffman[huffmanStr] = key
            #进入下一个
            baseline += 1
        baseline <<=1
    return (outputHuffman,huffman,reverseHuffman)

def std_DC_LU():
    std_dc_lu = {}
    std_dc_lu[2] = ['00']
    std_dc_lu[3] = ['01','02','03','04','05']
    std_dc_lu[4] = ['06']
    std_dc_lu[5] = ['07']
    std_dc_lu[6] = ['08']
    std_dc_lu[7] = ['09']
    std_dc_lu[8] = ['0A']
    std_dc_lu[9] = ['0B']
    return getStd(std_dc_lu)

def get_dc_lu_dict():
    std_dc_lu = {}
    std_dc_lu[2] = ['00']
    std_dc_lu[3] = ['01','02','03','04','05']
    std_dc_lu[4] = ['06']
    std_dc_lu[5] = ['07']
    std_dc_lu[6] = ['08']
    std_dc_lu[7] = ['09']
    std_dc_lu[8] = ['0A']
    std_dc_lu[9] = ['0B']
    return std_dc_lu

def std_DC_CO():
    std_dc_co = {}
    std_dc_co[2] = ['00','01','02']
    std_dc_co[3] = ['03']
    std_dc_co[4] = ['04']
    std_dc_co[5] = ['05']
    std_dc_co[6] = ['06']
    std_dc_co[7] = ['07']
    std_dc_co[8] = ['08']
    std_dc_co[9] = ['09']
    std_dc_co[10] = ['0A']
    std_dc_co[11] = ['0B']
    return getStd(std_dc_co)

def get_dc_co_dict():
    std_dc_co = {}
    std_dc_co[2] = ['00','01','02']
    std_dc_co[3] = ['03']
    std_dc_co[4] = ['04']
    std_dc_co[5] = ['05']
    std_dc_co[6] = ['06']
    std_dc_co[7] = ['07']
    std_dc_co[8] = ['08']
    std_dc_co[9] = ['09']
    std_dc_co[10] = ['0A']
    std_dc_co[11] = ['0B']
    return std_dc_co

def std_AC_LU():
    std_ac_lu = {}
    std_ac_lu[2] = ['01','02']
    std_ac_lu[3] = ['03']
    std_ac_lu[4] = ['00','04','11']
    std_ac_lu[5] = ['05','12','21']
    std_ac_lu[6] = ['31','41']
    std_ac_lu[7] = ['06','13','51','61']
    std_ac_lu[8] = ['07','22','71']
    std_ac_lu[9] = ['14','32','81','91','A1']
    std_ac_lu[10] = ['08','23','42','B1','C1']
    std_ac_lu[11] = ['15','52','D1','F0']
    std_ac_lu[12] = ['24','33','62','72']
    std_ac_lu[15] = ['82']
    std_ac_lu[16] = ['09','0A',
    '16','17','18','19','1A',
    '25','26','27','28','29','2A',
    '34','35','36','37','38','39','3A',
    '43','44','45','46','47','48','49','4A',
    '53','54','55','56','57','58','59','5A',
    '63','64','65','66','67','68','69','6A',
    '73','74','75','76','77','78','79','7A',
    '83','84','85','86','87','88','89','8A',
    '92','93','94','95','96','97','98','99','9A',
    'A2','A3','A4','A5','A6','A7','A8','A9','AA',
    'B2','B3','B4','B5','B6','B7','B8','B9','BA',
    'C2','C3','C4','C5','C6','C7','C8','C9','CA',
    'D2','D3','D4','D5','D6','D7','D8','D9','DA',
    'E1','E2','E3','E4','E5','E6','E7','E8','E9','EA',
    'F1','F2','F3','F4','F5','F6','F7','F8','F9','FA',
    ]

    return getStd(std_ac_lu)

def get_ac_lu_dict():
    std_ac_lu = {}
    std_ac_lu[2] = ['01','02']
    std_ac_lu[3] = ['03']
    std_ac_lu[4] = ['00','04','11']
    std_ac_lu[5] = ['05','12','21']
    std_ac_lu[6] = ['31','41']
    std_ac_lu[7] = ['06','13','51','61']
    std_ac_lu[8] = ['07','22','71']
    std_ac_lu[9] = ['14','32','81','91','A1']
    std_ac_lu[10] = ['08','23','42','B1','C1']
    std_ac_lu[11] = ['15','52','D1','F0']
    std_ac_lu[12] = ['24','33','62','72']
    std_ac_lu[15] = ['82']
    std_ac_lu[16] = ['09','0A',
    '16','17','18','19','1A',
    '25','26','27','28','29','2A',
    '34','35','36','37','38','39','3A',
    '43','44','45','46','47','48','49','4A',
    '53','54','55','56','57','58','59','5A',
    '63','64','65','66','67','68','69','6A',
    '73','74','75','76','77','78','79','7A',
    '83','84','85','86','87','88','89','8A',
    '92','93','94','95','96','97','98','99','9A',
    'A2','A3','A4','A5','A6','A7','A8','A9','AA',
    'B2','B3','B4','B5','B6','B7','B8','B9','BA',
    'C2','C3','C4','C5','C6','C7','C8','C9','CA',
    'D2','D3','D4','D5','D6','D7','D8','D9','DA',
    'E1','E2','E3','E4','E5','E6','E7','E8','E9','EA',
    'F1','F2','F3','F4','F5','F6','F7','F8','F9','FA',
    ]

    return std_ac_lu

def std_AC_CO():
    std_ac_co = {}
    std_ac_co[2] = ['00','01']
    std_ac_co[3] = ['02']
    std_ac_co[4] = ['03','11']
    std_ac_co[5] = ['04','05','21','31']
    std_ac_co[6] = ['06','12','41','51']
    std_ac_co[7] = ['07','61','71']
    std_ac_co[8] = ['13','22','32','81']
    std_ac_co[9] = ['08','14','42','91','A1','B1','C1']
    std_ac_co[10] = ['09','23','33','52','F0']
    std_ac_co[11] = ['15','62','72','D1']
    std_ac_co[12] = ['0A','16','24','34']
    std_ac_co[14] = ['E1']
    std_ac_co[15] = ['25','F1']
    std_ac_co[16] = ['17','18','19','1A',
    '26','27','28','29','2A',
    '35','36','37','38','39','3A',
    '43','44','45','46','47','48','49','4A',
    '53','54','55','56','57','58','59','5A',
    '63','64','65','66','67','68','69','6A',
    '73','74','75','76','77','78','79','7A',
    '82','83','84','85','86','87','88','89','8A',
    '92','93','94','95','96','97','98','99','9A',
    'A2','A3','A4','A5','A6','A7','A8','A9','AA',
    'B2','B3','B4','B5','B6','B7','B8','B9','BA',
    'C2','C3','C4','C5','C6','C7','C8','C9','CA',
    'D2','D3','D4','D5','D6','D7','D8','D9','DA',
    'E2','E3','E4','E5','E6','E7','E8','E9','EA',
    'F2','F3','F4','F5','F6','F7','F8','F9','FA',
    ]
    return getStd(std_ac_co)

def get_ac_co_dict():
    std_ac_co = {}
    std_ac_co[2] = ['00','01']
    std_ac_co[3] = ['02']
    std_ac_co[4] = ['03','11']
    std_ac_co[5] = ['04','05','21','31']
    std_ac_co[6] = ['06','12','41','51']
    std_ac_co[7] = ['07','61','71']
    std_ac_co[8] = ['13','22','32','81']
    std_ac_co[9] = ['08','14','42','91','A1','B1','C1']
    std_ac_co[10] = ['09','23','33','52','F0']
    std_ac_co[11] = ['15','62','72','D1']
    std_ac_co[12] = ['0A','16','24','34']
    std_ac_co[14] = ['E1']
    std_ac_co[15] = ['25','F1']
    std_ac_co[16] = ['17','18','19','1A',
    '26','27','28','29','2A',
    '35','36','37','38','39','3A',
    '43','44','45','46','47','48','49','4A',
    '53','54','55','56','57','58','59','5A',
    '63','64','65','66','67','68','69','6A',
    '73','74','75','76','77','78','79','7A',
    '82','83','84','85','86','87','88','89','8A',
    '92','93','94','95','96','97','98','99','9A',
    'A2','A3','A4','A5','A6','A7','A8','A9','AA',
    'B2','B3','B4','B5','B6','B7','B8','B9','BA',
    'C2','C3','C4','C5','C6','C7','C8','C9','CA',
    'D2','D3','D4','D5','D6','D7','D8','D9','DA',
    'E2','E3','E4','E5','E6','E7','E8','E9','EA',
    'F2','F3','F4','F5','F6','F7','F8','F9','FA',
    ]
    return std_ac_co