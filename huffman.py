
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
                    if not left.isTreenode and right.isTreenode: 
                        leftHuff,rightHuff = rightHuff,leftHuff
    
                    left.huffmanStr = point.huffmanStr+leftHuff
                    stack.append(left)
                    
    
                    right.huffmanStr = point.huffmanStr+rightHuff
                    stack.append(right)
