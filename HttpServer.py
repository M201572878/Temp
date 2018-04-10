import sys
import os
import locale
import platform
import socketserver
import http.server
import socket
import time
import threading
addr = len(sys.argv) < 2 and "0.0.0.0" or sys.argv[1]
port = len(sys.argv) < 3 and 8001 or locale.atoi(sys.argv[2])

dst_ip = "10.187.45.133"
dst_port = 22

BUFSIZE=10240
LOCK = threading.Lock()

class Client():
    __id = 0
    __to_dst_socket = None
    __message_queue = []
    def __init__(self, id, sock):
        self.__id = id
        self.__to_dst_socket = sock

    def get_sock(self):
        return self.__to_dst_socket

    def get_messages(self):
        return self.__message_queue

class TestHTTPHandle(http.server.BaseHTTPRequestHandler):
    __client_dict = {}
    def deal_connect(self, client_id, con_to_dst):
        buf = con_to_dst.recv(BUFSIZE)
        print('recv from server:', buf)
        while len(buf) > 0:
            LOCK.acquire()
            self.__client_dict[client_id].get_messages().append(buf)
            LOCK.release()
            buf = con_to_dst.recv(BUFSIZE)
        con_to_dst.close()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        data_to_src = b"<!DOCTYPE html> <html><body> hello </body> </html>"
        if self.path == '/connect':
            # try:
            socket_to_dst = socket.socket()
            socket_to_dst.connect((dst_ip, dst_port))
            data_from_dst = socket_to_dst.recv(BUFSIZE)
            data_to_src = data_from_dst
            print('recv from server:', data_from_dst)

            client_id = int(self.headers.get("ClientId"))
            LOCK.acquire()
            self.__client_dict[client_id] = Client(client_id, socket_to_dst)
            LOCK.release()

            threading.Thread(target=self.deal_connect, args=(client_id, socket_to_dst)).start()
            # except():
            #     data_to_src += b'connect error'
        self.wfile.write(data_to_src)

    def do_POST(self):
        client_id_str = self.headers.get("ClientId")
        client_id = int(client_id_str)
        self.send_response(200)
        serialize_bytes = b''
        if(client_id > 0):
            length = int(self.headers.get("Content-Length"))
            data = self.rfile.read(length)
            print("post:", data)
            self.__client_dict[client_id].get_sock().sendall(data)
            time.sleep(0.3)
            self.send_header("ClientId", client_id_str)

            LOCK.acquire()
            messages_list = self.__client_dict[client_id].get_messages()
            for message in messages_list:
                serialize_bytes += len(message).to_bytes(2, "big")
                serialize_bytes += message
            messages_list.clear()
            LOCK.release()
        self.end_headers()
        print("post rsp")
        self.wfile.write(serialize_bytes)

if __name__ == "__main__":
    # Linux下需要以root用户运行
    if platform.system() == "Linux" and os.getuid() != 0:
        print("This program must be run as root. Aborting.")
        sys,exit(1)
    httpd = socketserver.TCPServer((addr, port), TestHTTPHandle)
    print ("HTTP server is at: http://%s:%d/" % (addr, port))
    httpd.serve_forever()