# jpeg格式说明与解码学习

本文更加注重JPEG格式的具体解码实现，并不涉及编码实现（比如DCT、熵编码之类的，这些在很多书中都有详细的介绍，我就不赘述了）

## 参考资料

### 中文资料

* [JPEG文件格式JFIF&Exif](https://blog.csdn.net/kickxxx/article/details/8173332)：很好的对JPEG格式的整体解释，表格很清晰
* [jpg格式举例详解](https://blog.csdn.net/yangysng07/article/details/9025443)：同样有对JPEG各个marker的解释，十分全面，甚至还有例子。
* [JPEG文件编/解码详解](http://www.cnblogs.com/leaven/archive/2010/04/06/1705846.html)：同样有着很详尽的说明，理论上十分深刻。
* [jpeg图像密写研究](https://www.cnblogs.com/gungnir2011/tag/JPEG/)：四篇文章，似乎不错的样子
* [csdn下载:Jpeg官方文档下载](https://download.csdn.net/download/wxzking/1497052)：JPEG官方文档，虽然我没看

### 英文资料
* [StackOverflow: How to write jpeg file decoder](https://stackoverflow.com/questions/6871028/how-to-write-a-jpeg-file-decoder-from-scratch)：StackOverflow上的问题，帮助很大。
* [jpeg deocder written in python](https://github.com/enmasse/jpeg_read)：上面题目中一位答主用python写的jpeg解码器
* [JPEG decoder written in C](http://www.ctralie.com/PrincetonUGRAD/Projects/JPEG/jpeg.pdf)：普林斯顿大佬的JPEG解码器
* [JPEGsnoop](https://github.com/ImpulseAdventure/JPEGsnoop)：github上的开源软件，可以探测分析JPEG上各个分量的具体数值。
* [JPEG Huffman Coding Tutorial](https://www.impulseadventure.com/photo/jpeg-huffman-coding.html)：上面那款软件作者的文章，很详细的介绍了哈夫曼编码的过程与手动解码的例子。
* [JPEG encoder in Python](https://github.com/ghallak/jpeg-python)：python写的JPEG编码器与解码器

## 格式介绍

以下内容翻译自英文维基百科，我觉得挺不错的。

JPEG由segment组成，segment的开头是marker；marker由0xFF开头，后一个决定了marker的类型。marker后会跟两个字节的的长度，表示其后的数据量，有时会用连续的FF进行填充。

### 概念释义

不保证正确，只是个人的理解
1. JPG与JPEG：一样的意思，都是表示Joint Photographic Experts Group开发的这套JPEG标准所描述的图片，只是早期DOS系统只支持3位扩展名，而Apple支持多位扩展名才有所区别。后面即使Windows同样支持多位扩展名也没有改变这个习惯。因为Windows用户更多，所以主流为jpg，但是像是.jpeg、.JPG和.JPEG都是可以的。
2. JPG与JFIF：早期的JPEG格式只说明了图片如何压缩为字节流以及重新解码为图片的过程，但是没有说明这些字节是如何在任何特定的存储媒体上封存起来的。因此建立了相关的额外标准JFIF(JPEG File Interchange Format)。后来这个标准变为主流，现在所使用的JPEG文件基本都是符合JFIF标准的。

### 关于0xFF

从上面这句话可以看出，0xFF在JPEG文件中是十分重要。如果读取中出现了0xFF，根据后面的值有多种可能。
1. 后面的值为0xFF，这时候视为一个0xFF看待，继续读取。
2. 后面的值为0x00，这时候表示这个FF在数据流中，跳过。
3. 其他能够表示marker的值，将其视为marker开头处理。
4. 其他值，跳过。

### 整体格式

JPEG格式的大致顺序为：
* SOI
* APP0
* \[APPn\]可选
* DQT
* SOF0
* DHT
* SOS
* 压缩数据
* EOI

JPEG中SOI和EOI中间为Frame

Frame的头包含了像素的位数，图像的宽和高等信息。Frame下有Scan

Scan的头包含每个扫描的分量数，分量ID，哈夫曼表等。Scan下有Segment和Restart，即压缩数据的基本单位。


注：在JPEG文件格式中使用Motorola格式而不是Intel格式，也就是说大端模式，高字节低地址，低字节高地址。

### 标签表

总表

|缩写|字节码|名称|注释|
| :-: | :-: | :-: | :-|
|SOI|0xFFD8|Start of image|文件开头|
|SOF0|0xFFC0|Start of Frame0|Baseline DCT-based JPEG所用的开头|
|SOF2|0xFFC2|Start of Frame2|Progressive DCT-based JPEG|
|DHT|0xFFC4|Define Huffman Tables|指定一个或多个哈夫曼表|
|DQT|0xFFDB|Define Quantization Table| 指定量化表|
|DRI|0xFFDD|Define Restart Interval|RST中的marker|
|SOS|0xFFDA|Start of Scan|Scan的开头|
|RSTn|0xFFDn|Restart|DRImarker中插入r个块|
|APPn|0xFFEn|Application-specific|Exif JPEG使用APP1，JFIF JPEG使用APP0|
|COM|0xFFFE|Comment|注释内容|
|EOI|0xFFD9|End of Image|图像的结束|

表2 JPEG Start of Frame结构
|字段名称|长度|注释|
|:-:|:-:|:-|
|标记代码|2 bytes|固定值0xFFC0|
|数据长度|2 bytes|SOF marker的长度，包含自身但不包含标记代码|
|精度|1 byte|每个样本数据的位数，通常是8位|
|图像高度|2 bytes|图像高度，单位是像素|
|图像宽度|2 bytes|图像宽度，单位是像素|
|颜色分量数|1 bytes|灰度级1，YCbCr或YIQ是3，CMYK是4|
|颜色分量信息|颜色分量数*3|每个颜色分量：1 byte分量ID； 1byte水平垂直采样因子（前4位为水平采样因子，后4位为垂直采样因子）； 1byte当前分量使用的量化表ID|

表3 JPEG Start of Scan结构
|字段名称|长度|注释|
|:-:|:-:|:-|
|标记代码|2 bytes|固定值0xFFDA|
|数据长度|2 bytes|SOS marker的长度，包含自身但不包含标记代码|
|颜色分量数|1 bytes|灰度级1，YCbCr或YIQ是3，CMYK是4|
|颜色分量信息|颜色分量数*3|1byte的颜色分量id，1byte的直流/交流系数表号（高4位：直流分量所使用的哈夫曼树编号，低4位：交流分量使用的哈夫曼树的编号）|
|压缩图像信息|3 bytes||
||1 byte|谱选择开始 固定为0x00|
||1 byte|谱选择结束 固定为0x3f|
||1 byte|谱选择 在basic JPEG中固定为00|

注：SOS紧跟着就是压缩图像信息

表4 JPEG APP0 应用保留标记0
|字段名称|长度|注释|
|:-:|:-:|:-|
|标记代码|2 bytes|固定值0xFFE0|
|数据长度|2 bytes|APP0的长度，包含自身但不包含标记代码|
|标识符 identifier|5 bytes|固定的字符串"JFIF\0"|
|版本号|2 bytes|一般为0x0101或0x0102，表示1.1或1.2|
|像素单位 unit|1 byte|坐标单位，0为没有单位； 1 pixel/inch； 2pixel/inch|
|水平像素数目|2 bytes||
|垂直像素数目|2 bytes||
|缩略图水平像素数目|1 byte|如果为0则没有缩略图|
|缩略图垂直像素数目|1 byte|同上|
|缩略图RGB位图|3n bytes|n = 缩略图水平像素数目*缩略图垂直像素数目，这是一个24bits/pixel的RGB位图|

表5 APPn应用程序保留标记
|字段名称|长度|注释|
|:-:|:-:|:-|
|标记代码|2 bytes|固定值0xFFE1-0xFFEF，n=1~15|
|数据长度|2 bytes|APPn的长度，包含自身但不包含标记代码|
|详细信息|(length-2) bytes|内容是应用特定的，比如Exif使用APP1来存放图片的metadata，Adobe Photoshop用APP1和APP13两个标记段分别存储了一副图像的副本。|

表6 DQT 定义量化表
|字段名称|长度|注释|
|:-:|:-:|:-|
|标记代码|2 bytes|固定值0xFFDB|
|数据长度|2 bytes|DQT的长度，包含自身但不包含标记代码|
|量化表|(length-2)bytes|下面为子字段|
|精度及量化表ID| 1 byte| 高4位为精度，只有两个可选值：0表示8bits，1表示16bits；低4位为量化表ID，取值范围为0~3|
|表项|64*(精度+1)bytes||

表7 DHT 定义哈夫曼表
|字段名称|长度|注释|
|:-:|:-:|:-|
|标记代码|2 bytes|固定值0xFFC4|
|数据长度|2 bytes|DHT的长度，包含自身但不包含标记代码|
|哈夫曼表|(length-2)bytes|以下为哈夫曼表子字段|
|表ID和表类型|1 byte|高4位：类型，只有两个值可选，0为DC直流，1为AC交流；低4位：哈夫曼表ID，注意DC表和AC表是分开编码的|
|不同位数的码字数量|16字节||
|编码内容|上述16个不同位数的码字的数量和||

注：哈夫曼表可以重复出现（一般出现4次）



其他详细内容可以看[这篇文章](http://www.cnblogs.com/leaven/archive/2010/04/06/1705846.html)，这是我在这一部分看到的比较全面的中文资料。

## 解码
因为时间原因，后面写的不是很好，建议阅读其他参考文献。
### 哈夫曼表解码

学习自这篇[文章](http://www.cnblogs.com/leaven/archive/2010/04/06/1705846.html)，里面的例子写的很好。
还有这篇[英文文章](https://www.impulseadventure.com/photo/jpeg-huffman-coding.html)，作者居然自己还写了个分析器，十分厉害。

如上文表7所述，对于单一的哈夫曼表应该有三个部分：
1. 哈夫曼表ID和类型：长度为1byte。这个自己的值一般只有四个，0x00、0x01、0x10、0x11。其中高4位表示直流/交流，低4位表示id。
2. 不同位数的码字数量，JPEG文件的哈夫曼编码只能是1~16位。这个字段的16个字节分别表示1~16位的编码码字在哈夫曼树中的个数
3. 编码内容：这个字段记录了哈夫曼树上各个叶子结点的权重。因此，上一字段的16个数值之和就应该是本字段的长度，也就是哈夫曼树中叶子节点的个数。

4个哈夫曼表中分别代表光学的DC编码和AC编码（Y）以及色彩的DC编码和AC编码（Cb&Cr）

哈夫曼表2条目中的16个数表示对应位数的编码个数，比如第一个数表示哈夫曼编码长度为1的编码个数，以此类推。

然后可以根据哈夫曼编码中的编码进行解码：
1）第一个码字必定为0。
如果第一个码字位数为1，则码字为0；
如果第一个码字位数为2，则码字为00；
如此类推。

2）从第二个码字开始，
如果它和它前面的码字位数相同，则当前码字为它前面的码字加1；
如果它的位数比它前面的码字位数大，则当前码字是前面的码字加1后再在后边添若干个0，直至满足位数长度为止。

## 编码

### DC编码

根据DCT变换，每个块都会得到一个DC分量。对于每个颜色空间的DC分量，计算差值，使得过去的值可以用现在的值加上之前的累加和来表示。

对于得到的这么一个差分序列，将它变为(size,amplitude)形式，其中amplitude的计算方式是：正数直接转换为二进制数，负数直接取反码。size表示amplitude的位数。再对每个size进行哈夫曼编码来压缩，就得到了最后的二进制流。

### AC编码

每个块有63个AC分量。对这些AC分量按照zigzag顺序进行游长编码(runlength,value)，意义为跨越多少个0串之后到达怎样的值。因为后面编码的原因，runlength不能大于15。对于得到的游长编码，对其value进行DPCM编码，然后将runlength作为4位二进制数与DPCM的size一同合并为8位二进制数进行编码，amplitude单独编码，合并成一个二进制流。

### 哈夫曼编码

对于得到的4个哈夫曼树进行编码。编码时按照哈夫曼编码字典序排列，位数短的在前，统计位数，然后写下前16位数字。
接着写下所有的哈夫曼编码对应的值，编码结束。

这里有几个问题：
1. 生成的Huffman编码如果大于16位的话就不在范围之内了，这个是有可能的，[这个问题](https://stackoverflow.com/questions/9115155/jpeg-huffman-coding-procedure)提到了这种情况。里面的答主提到实际中后面会留有一定的空间，同时大多数JPEG编码器使用的是基于统计学制作的标准的哈夫曼编码表。(注：普通的jpeg不会遇到这种情况，因为它们编码的对象为size，一般不会超过16位，更多情况下不会多于10个点)
2. 从解码的角度考虑，存储的时候哈夫曼编码条目不一定能够还原回去。这意味着应该要对生成的哈夫曼树进行处理，保证三个特点：a.下一长度的哈夫曼树必须能够为上一长度的哈夫曼树加1补0后得到。

### 编码数据

编码数据的安排是这样的，每个8*8的块按照顺序存放，每个块内三个颜色空间按顺序存放，每个颜色空间内先存DC分量编码，再存AC分量编码

对于AC部分的编码。
如果没有AC分量没有出现的话，其size置为0后，后面可以不用跟任何东西。

因为scan的数据必须为8的整数位，如果有不足的地方需要填1
