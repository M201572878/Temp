import _thread
import socket
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime

# 为线程定义一个函数
def print_time(name, socketRecv, socketSend):
    print(name)
    buf = socketRecv.recv(10240)
    while len(buf):
        print(name.encode() + b":" + buf)
        if name == "listenServer":
            now = datetime.now()
            stamp = mktime(now.timetuple())
            dataStr = format_date_time(stamp)

            head = b'''HTTP/1.1 200 OK
Proxy-Connection: Keep-Alive
Connection: keep-alive
Server: BaseHTTP/0.3 Python/2.7.10
Date ''' + dataStr.encode() + b'''
Content-Length: ''' + str(len(buf)).encode() + b'''

''' + buf;
            print(head.decode())
        socketSend.send(head + buf)
        buf = socketRecv.recv(10240)
    socketSend.close()

socketListenClient = socket.socket()  # 创建socket对象
socketListenClient.bind(("0.0.0.0", 10010))  # 绑定端口,“127.0.0.1”代表本机地址，8888为设置链接的端口地址
socketListenClient.listen(5)  # 设置监听，最多可有5个客户端进行排队
# 创建两个线程
socketToClient = None
socketToServer = None
while(True):
    socketToClient, addr = socketListenClient.accept()  # 阻塞状态，被动等待客户端的连接
    socketToServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketToServer.connect(('127.0.0.1', 10086))
    try:
       _thread.start_new_thread( print_time, ("listenServer", socketToServer, socketToClient) )
       _thread.start_new_thread( print_time, ("listenClient", socketToClient, socketToServer) )
    except:
       print ("Error: 无法启动线程")

while 1:
   pass

