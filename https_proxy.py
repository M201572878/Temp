import socket

import time

import threading

BUFSIZE = 1024

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

class Access_to_Host(object):
    def handler(self, conn, addr):
        self.conn = conn
        self.addr = addr
        all_src_data, hostname, port, ssl_flag = self.get_dst_host_from_header(self.conn, self.addr)
        if (hostname != '119.29.188.55'):
            return
        all_dst_data = self.get_data_from_host(hostname, port, all_src_data, ssl_flag)
        print(all_dst_data, ssl_flag)
        if all_dst_data and not ssl_flag:
            # self.send_data_to_client(self.conn,all_dst_data)
            self.ssl_client_server_client(self.conn, self.conn_dst, all_dst_data)
        elif ssl_flag:
            sample_data_to_client = b"HTTP/1.0 200 Connection Established\r\n\r\n"
            # print("\nSSL_Flag-1")
            # self.send_data_to_client(self.conn,all_dst_data)
            # print("SSL_Flag-2")
            self.ssl_client_server_client(self.conn, self.conn_dst, sample_data_to_client)
            # print("\nSSL_Flag-3")
        else:
            print('pls check network. cannot get hostname:' + hostname)
            # self.conn.close()

    def ssl_client_server(self, src_conn, dst_conn):
        self.src_conn = src_conn
        self.dst_conn = dst_conn
        while True:
            ###get data from client
            try:
                ssl_client_data = self.src_conn.recv(BUFSIZE)
            except Exception as e:
                print("client disconnct ")
                print(e)
                self.src_conn.close()
                # self.dst_conn.close()
                return False

            if ssl_client_data:
                #####send data to server
                try:
                    self.dst_conn.sendall(ssl_client_data)
                except Exception as e:
                    print("server disconnct Err")
                    self.dst_conn.close()
                    return False
            else:
                self.src_conn.close()
                return False

    def ssl_server_client(self, src_conn, dst_conn):
        self.src_conn = src_conn
        self.dst_conn = dst_conn

        while True:
            ###get data from server
            try:
                ssl_server_data = self.dst_conn.recv(BUFSIZE)
            except Exception as e:
                print("server disconnct ")
                self.dst_conn.close()
                return False

            if ssl_server_data:
                #####send data to client
                try:
                    self.src_conn.sendall(ssl_server_data)
                except Exception as e:
                    print("Client disconnct Err")
                    self.src_conn.close()
                    return False
            else:
                self.dst_conn.close()
                return False

    def ssl_client_server_client(self, src_conn, dst_conn, all_dst_data):
        self.src_conn = src_conn
        self.dst_conn = dst_conn
        try:
            # print(all_dst_data)
            self.src_conn.sendall(all_dst_data)
            print(all_dst_data)
        except Exception as e:
            print(e)
            print("cannot sent data(HTTP/1.0 200) to SSL client")
            return False
        threadlist = []

        t1 = threading.Thread(target=self.ssl_client_server, args=(self.src_conn, self.dst_conn))
        t2 = threading.Thread(target=self.ssl_server_client, args=(self.src_conn, self.dst_conn))
        threadlist.append(t1)
        threadlist.append(t2)
        for t in threadlist:
            t.start()
            # t.join()
            ######线程控制,等待线程结束后,远程主机关闭socket后，客户端到主机的socket也不需要再做任何操作了。
        while not self.dst_conn._closed:
            time.sleep(1)
        self.src_conn.close()

    def get_src_client(self):
        self.src_ip = self.s_src.getpeername()
        return self.src_ip

    def send_data_to_client(self, conn_src, data):
        self.conn_src = conn_src
        try:
            self.conn_src.sendall(data)
        except Exception as e:
            print(e)
            print("cannot sent data to client")
            return False
            # self.conn_dst.close()

    def get_dst_host_from_header(self, conn_sock, addr):

        self.s_src = conn_sock
        self.addr = addr
        header = ""
        ssl_flag = False
        while True:
            # print("Loop Loop Loop")
            header = self.s_src.recv(BUFSIZE)

            if header:
                #####header的一行含有CONNECT，即为SSL（HTTPS）
                indexssl = header.split(b"\n")[0].find(b"CONNECT")
                # print("indexsll:"+str(indexssl))
                if indexssl > -1:
                    #####CONNECT===7  +8 前面一个空格
                    # hostname = str(header.split(b"\n")[0].split(b":")[0].decode())
                    # hostname = hostname[indexssl + 8:]
                    # port = 443
                    result11, hostname, port = get_dst_ip_port(header)
                    if (hostname == '119.29.188.55'):
                        print(header)
                    ssl_flag = True
                    return header, hostname, port, ssl_flag
                index1 = header.find(b"Host:")
                index2 = header.find(b"GET http")
                index3 = header.find(b"POST http")
                if index1 > -1:
                    indexofn = header.find(b"\n", index1)
                    ##host:===5
                    host = header[index1 + 5:indexofn]
                elif index2 > -1 or index3 > -1:
                    ###no host sample :'GET http://saxn.sina.com.cn/mfp/view?......
                    host = header.split(b"/")[2]
                else:
                    print("src socket host:")
                    print(self.s_src.getpeername())
                    print("cannot find out host!!:" + repr(header))
                    return
                break
        host = str(host.decode().strip("\r").lstrip())
        if len(host.split(":")) == 2:
            port = host.split(":")[1]
            hostname = host.split(":")[0].strip("")
        else:
            port = 80
            hostname = host.split(":")[0].strip("")
        ssl_flag = False
        return header, hostname, int(port), ssl_flag

    def get_data_from_host(self, host, port, sdata, ssl_flag):
        self.conn_dst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        all_dst_data = ""
        try:
            self.conn_dst.connect((str(host), port))
        except Exception as e:
            print(e)
            print("get_data_from_host: cannot get host:" + host)
            self.conn_dst.close()
            return False
        # con_string="("+server+","+port+")"
        ############https只建立链接
        try:
            if ssl_flag:
                return all_dst_data
            else:
                print(sdata)
                self.conn_dst.sendall(sdata)
        except Exception as e:
            print(e)
            print("cannot send data to host:" + host)
            self.conn_dst.close()
            return False
            # buffer=[]
        rc_data = self.conn_dst.recv(BUFSIZE)
        print(rc_data)
        #####剩下的data交给线程去获取
        return rc_data


class Server(object):
    def Handle_Rec(conn_socket, addr):
        print("This is Handler Fun")
        pass

    def __init__(self, host, port):
        print("Server starting......")
        self.host = host
        self.port = port
        self.s_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s_s.bind((host, port))
        self.s_s.listen(20)

    def start(self):
        while True:
            try:
                conn, addr = self.s_s.accept()
                threading.Thread(target=Access_to_Host().handler, args=(conn, addr)).start()
            except Exception  as e:
                print(str(e))
                print("\nExcept happend")


if __name__ == "__main__":
    svr = Server("127.0.0.1", 10010)
    svr.start()