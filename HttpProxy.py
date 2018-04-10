import http
import os
import time
import requests
import threading
import socket
import requests
import time
from requests_ntlm import HttpNtlmAuth

middle_url = "http://127.0.0.1:8001"

BUFSIZE=10240
session = requests.Session()
# session.auth = HttpNtlmAuth('china\\z00427032','hyhyx6125...')
# session.proxies = {"http":"http://proxy.huawei.com:8080","https": "http://proxy.huawei.com:8080",}
# rsp = session.get("http://www.baidu.com", verify=False)
# print(rsp.content)

def recv_client(client_id, con_to_client):
    data_from_client = con_to_client.recv(BUFSIZE)
    while (len(data_from_client) > 0):
        print("from client:", data_from_client)
        rsp = session.post(middle_url, data=data_from_client, headers = {'ClientId': str(client_id)},verify=False)
        data = rsp.content
        index = 0
        while( index < len(data)):
            length = int.from_bytes(data[index : index + 2], "big")
            part_data = data[index + 2: index + 2 +length]
            print("send to client:", part_data)
            con_to_client.sendall(part_data)
            index += (2 + length)
        data_from_client = con_to_client.recv(BUFSIZE)
    con_to_client.close()

if __name__ == "__main__":
    socketListenClient = socket.socket()  # 创建socket对象
    socketListenClient.bind(("0.0.0.0", 10010))  # 绑定端口,“127.0.0.1”代表本机地址，8888为设置链接的端口地址
    socketListenClient.listen(5)  # 设置监听，最多可有5个客户端进行排队
    while (True):
        socketToClient, addr = socketListenClient.accept()  # 阻塞状态，被动等待客户端的连接
        client_id = int(time.time())
        #session.headers["ClientID"] = str(client_id)
        rsp = session.get(middle_url + "/connect", verify=False,headers = {'ClientId': str(client_id)})
        data = rsp.content
        print(data)
        socketToClient.sendall(data)
        threading.Thread(target=recv_client, args=(client_id, socketToClient)).start()