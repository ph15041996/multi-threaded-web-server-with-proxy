# TODO
# Handle 200 and 404,304 request Reasonable handling of Conditional GET requests and 304 (Not Modified) responses is also required
# You should be able to use your proxy from any Web browser (e.g., Internet Explorer, Chrome, and Mozilla Firefox), and from any machine
# Handle Bad requests

# UnicodeDecodeError: 'utf-8' codec can't decode byte 0xcf in position 380: invalid continuation byte socket

from socket import socket,AF_INET,SOCK_STREAM,SOL_SOCKET,SO_REUSEADDR
from _thread import start_new_thread
import ssl
from urllib.parse import urlparse
import re
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8081

class ProxySever():
    def __init__(self):
        self.poxyServerObj = socket(AF_INET,SOCK_STREAM)
        self.poxyServerObj.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.poxyServerObj.bind((SERVER_IP,SERVER_PORT))
        self.poxyServerObj.listen(5)
        print("Proxy server listening on port ... ",SERVER_PORT)

    def makeRequestToFinalServer(self,parsed_data):
        server_socket = socket(AF_INET,SOCK_STREAM)
        server_socket.connect((parsed_data["server_host"],parsed_data["server_port"]))
        print("connected to ",parsed_data["server_port"])
        if(parsed_data["server_port"] == 443):
            context =ssl.create_default_context()
            server_socket = context.wrap_socket(server_socket,server_hostname=parsed_data["server_host"])

        htmlUrl = 'GET {} HTTP/1.0\r\nHOST: {}\r\n\r\n'.format(parsed_data["server_path"],parsed_data["server_host"])
        # print("htmlUrl =>>>",htmlUrl)
        server_socket.sendall(htmlUrl.encode())
        print("final server socket send")
        server_socket.settimeout(5)
        response =b''
        try:
            while True:
                data = server_socket.recv(4096)
                response += data
                if not data:
                    server_socket.close()
                    print("socket close")
                    break
        except Exception as e:
            print("Exception {}".format(e))
            server_socket.settimeout(0)
        # print("response",response)

        # headers = decoded_server_response.split("\r\n\r\n")[0]
        header = response.split(b"\r\n\r\n")[0]
        decoded_header = header.decode()
        status_code = decoded_header.split("\r\n")[0].split(" ")[1]
        print(status_code)
        if(status_code == "404"):
            pass
        elif(status_code == "304"):
            pass
        elif(300 >=  int(status_code) and int(status_code) < 400):
           pass 


        body = response[len(header)+4:]
        decoded_header = decoded_header+ "\r\nproxy_ip_addr: {}\r\nproxy_port: {}\r\n\r\n".format(SERVER_IP,SERVER_PORT)
        modified_response = decoded_header.encode() +body 
        # print(modified_response)
        return modified_response

    def handleClientThead(self,client_conn,client_addr,client_req_data):
        print("Client conncted with address ",client_addr)
        print(client_req_data.encode())
        parsed_data = self.parseHtmlReq(client_req_data)
        print(parsed_data)
        server_response = self.makeRequestToFinalServer(parsed_data)
        print("server resp :",server_response)
        # response = 'HTTP/1.0 200 OK\r\n'
        # client_conn.sendall(response.encode())
        client_conn.sendall(server_response)
        client_conn.close()

# CONNECT www.cse.iith.ac.in:443 HTTP/1.1
# 'GET http://example.com/ HTTP/1.1'

    def parseHtmlReq(self,req_data):
        # url_arr = req_data.split('\r\n\r\n')
        url_details = {"server_host":"","server_port":0,"server_path":"/","is_valid":0}
        url_arr = req_data.split('\r\n')
        # print(url_arr)
        server_url_str = url_arr[0].split(" ")
        # print(server_url_str)
        final_server_url = url_arr[0].split(" ")
        requested_url = server_url_str[1]
        # print(type(requested_url),"requested_url")
        if(requested_url[:1] == "/"):
            requested_url = requested_url[1:]
        # if(requested_url[:4] == "http"):
            # print("hello")

            
        if(requested_url.split(":")[-1] == "443"):
            if(requested_url[:4] != "http"):
                requested_url = "https://"+requested_url


        # for ele in [0]:
        paresed_word = urlparse(requested_url)
        # print("elel ",requested_url)
        # print("query",paresed_word.query)
        # print("hostname",paresed_word.hostname)
        # print("port",paresed_word.port)
        # print("path",paresed_word.path)
        # print("scheme",paresed_word.scheme)
        # print("netloc",paresed_word.netloc)
        if(paresed_word.scheme and paresed_word.netloc):
            final_server_url_path =  paresed_word.hostname
            url_details["server_host"]= paresed_word.hostname
            url_details["server_port"] = 80
            if(paresed_word.scheme == "https"):
                url_details["server_port"] = 443
            if(paresed_word.path):
                url_details["server_path"] =  paresed_word.path
            url_details["is_valid"] = 1

            # get_port_regex =re.findall(r':\d+',requested_url)
            # print("regex",get_port_regex)
            # if(get_port_regex[0][0]==":" and get_port_regex[0][1:].isdigit()):
            #     url_details["server_port"] = int(get_port_regex[0][1:])
        # print(url_details)
        return url_details
    def waitForResponse(self):
        pass

    def listenClient(self):
        while True:
            client_conn,client_addr = self.poxyServerObj.accept()
            print("client connected  ",client_addr)
            client_req_data = client_conn.recv(4096).decode()
            start_new_thread(self.handleClientThead,(client_conn,client_addr,client_req_data))
            
httpProxy = ProxySever()
httpProxy.listenClient()

