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

    def forwardRequest(self,parsed_data):
        server_socket = socket(AF_INET,SOCK_STREAM)
        server_socket.connect((parsed_data["server_host"],parsed_data["server_port"]))
        print("connected to ",parsed_data["server_port"])
        if(parsed_data["server_port"] == 443):
            context =ssl.create_default_context()
            server_socket = context.wrap_socket(server_socket,server_hostname=parsed_data["server_host"])

        url = 'GET {} HTTP/1.0\r\nHOST: {}\r\n\r\n'.format(parsed_data["server_path"],parsed_data["server_host"])
        server_socket.sendall(url.encode())
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

            header = response.split(b"\r\n\r\n")[0]
            decoded_header = header.decode()
            status_code = decoded_header.split("\r\n")[0].split(" ")[1]
            if(status_code == "404"):
                pass
            elif(status_code == "304"):
                pass
            elif(300 >=  int(status_code) and int(status_code) < 400):
               pass 
            body = response[len(header)+4:]
            decoded_header = decoded_header+ "\r\nproxy_ip_addr: {}\r\nproxy_port: {}\r\n\r\n".format(SERVER_IP,SERVER_PORT)
            modified_response = decoded_header.encode() +body 
        except Exception as e:
            print("Exception {}".format(e))
            server_socket.settimeout(0)
            modified_response = b"HTTP/1.0 404 File not found\r\n" 
        return modified_response

    def handleClientThead(self,connection,client_req_data):
        parsed_data = self.parseRequest(client_req_data)
        server_response = self.forwardRequest(parsed_data)
        print("server resp :",server_response)
        connection.sendall(server_response)
        connection.close()

# CONNECT www.cse.iith.ac.in:443 HTTP/1.1
# 'GET http://example.com/ HTTP/1.1'

    def parseRequest(self, request):
        urlDetails = {"server_host":"", "server_port":0, "server_path":"/", "is_valid":0}
        url_arr = request.split('\r\n')
        server_url_str = url_arr[0].split(" ")
        url = server_url_str[1][1:]
        if url.split(":")[-1] == "443" and url[:4] != "http":
            url = url[:4] + "s" + url[4:]
        parsedURL = urlparse(url)
        if parsedURL.scheme and parsedURL.netloc:
            urlDetails["server_host"] = parsedURL.hostname
            urlDetails["server_port"] = 80
            if parsedURL.scheme == "https":
                urlDetails["server_port"] = 443
            if parsedURL.path:
                urlDetails["server_path"] =  parsedURL.path
            urlDetails["is_valid"] = 1
            get_port_regex =re.findall(r':\d+', url)
            if(get_port_regex):
                if(get_port_regex[0][0]==":" and get_port_regex[0][1:].isdigit()):
                    urlDetails["server_port"] = int(get_port_regex[0][1:])
        return urlDetails

    def listenClient(self):
        while True:
            connection,address = self.poxyServerObj.accept()
            request = connection.recv(4096).decode('latin-1')
            start_new_thread(self.handleClientThead,(connection,request))
            
httpProxy = ProxySever()
httpProxy.listenClient()

