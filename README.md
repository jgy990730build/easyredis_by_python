# easyredis_by_python
简单使用python实现redis

# 设计思路
1	使用python的socket模块写一个服务端和一个客户端的tcp通信程序，可以在服务端收到客户端发送的信息，并可以对其进行分割<br>
2	对于客户端：把发送前的信息进行自定义格式化，表明信息的长度（有利于区分命令），表明输入的值，对于服务端：把信息获取并放入字典当中，方便以后取出。然后引入selectors实现高效的 I/O multiplexing ,  常用于非阻塞的 socket  的编程中。<br>
3	把数据存在一个字典里，通过封装成database模块，提高代码可重用性并作为父类，写对应的类继承它。不同的类操作不同的数据。Set数据以python的Set类型存储到字典里，List类型以python的list类型存储，set，get命令计入到string类型存储。<br>
4	在database类加入两个抽象方法load和dump分别用于数据持久化和读取出来，使用序列化技术（OS,pickle）把数据存入到db文件里。在每次打开服务端是把db文件反序列化到字典里。<br>
5	加入只定义log模块，使用操作时的信息。<br>

# 采用的语言，框架
Python，添加模块：socket，selectors，Lock，Pool，os，pickle

#使用TCP通信协议：把字符串进行重组，结构如下：
 
py-redis > set kj 'vc'
*3
$3
set
$2
kj
$4
'vc'

