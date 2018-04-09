import _thread
import socket
import getpass

def get_dst_ip_port(buf):
    result = True
    try:
        str = buf.decode().split('\n')[0]
        http_info = str.split(' ')
        ip_port = http_info[1].split(':')
        ip = ip_port[0]
        port = int(ip_port[1])
    except:
        result = False
    finally:
        return result, ip, port

# 为线程定义一个函数
def print_time(name, socketRecv, socketSend, ip_port):
    print(name)
    try:
        while True:
            buf = socketRecv.recv(10240)
            if(len(buf)):
                print(name.encode() + b":" + buf)
            if( name == 'listenClient'):
                buf = replace_buf(buf, ip_port)
            socketSend.send(buf)
    except:
        socketSend.close()
        print('close')

def replace_buf(buf, ip_port):
    str = buf.decode()
    str.replace("127.0.0.1:10010", ip_port)
    return str.encode()

if __name__ == '__main__':
    proxy_ip = '10.187.45.133'
    proxy_port = 3128

    user = getpass.getuser()
    print(user)

    socketListenClient = socket.socket()  # 创建socket对象
    socketListenClient.bind(("0.0.0.0", 10010))  # 绑定端口,“127.0.0.1”代表本机地址，8888为设置链接的端口地址
    socketListenClient.listen(5)  # 设置监听，最多可有5个客户端进行排队
    # 创建两个线程
    socketToClient = None
    socketToServer = None
    while(True):
        socketToClient, addr = socketListenClient.accept()  # 阻塞状态，被动等待客户端的连接
        buf = socketToClient.recv(10240)
        result, dst_ip, dst_port = get_dst_ip_port(buf)
        if(result):
            con_ip = dst_ip if user == 'hyhyx' else proxy_ip
            con_port = dst_port if user == 'hyhyx' else proxy_port
            socketToServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('connect to: ', con_ip, con_port)
            socketToServer.connect((con_ip, con_port))
            ip_port = con_ip + str(con_port)
            buf = replace_buf(buf, ip_port)
            print(buf)
            socketToServer.send(buf)
            try:
               _thread.start_new_thread( print_time, ("listenServer", socketToServer, socketToClient, ip_port) )
               _thread.start_new_thread( print_time, ("listenClient", socketToClient, socketToServer, ip_port) )
            except:
               print ("Error: 无法启动线程")

    while 1:
       pass

