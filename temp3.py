import _thread
import socket

# 为线程定义一个函数
def print_time(name, socketRecv, socketSend):
    print(name)
    buf = socketRecv.recv(10240)
    while len(buf):
        #print(buf)
        if name == "listenServer":
            buf = b'''HTTP/1.1 200 OK
            Proxy-Connection: Keep-Alive
            ''' + buf;
        socketSend.send(buf)
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

