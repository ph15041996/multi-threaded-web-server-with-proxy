import json
from socket import socket,AF_INET,SOCK_STREAM,SOL_SOCKET,SO_REUSEADDR
from _thread import start_new_thread
import ssl
from urllib.parse import urlparse
import re
from englisttohindi.englisttohindi import EngtoHindi
from bs4 import BeautifulSoup
import os
from datetime import datetime,date,timedelta
import matplotlib.pyplot as plt

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8081
json_file_path = "data.json"


class ProxySever():
    # create socket and start listing for request
    def __init__(self):
        self.poxyServerObj = socket(AF_INET,SOCK_STREAM)
        self.poxyServerObj.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.poxyServerObj.bind((SERVER_IP,SERVER_PORT))
        self.poxyServerObj.listen(5)
        print("Proxy server listening on port ... ",SERVER_PORT)

    def forwardRequest(self,parsed_data):
        """
        This function makes request to  the final server and return the repons form the server
        """
        # create socket  and connect to the server
        server_socket = socket(AF_INET,SOCK_STREAM)
        server_socket.connect((parsed_data["server_host"],parsed_data["server_port"]))
        print("connected to final server at port  ",parsed_data["server_port"])

        # if port is 443 then we wrap the socket in ssl
        if(parsed_data["server_port"] == 443):
            context =ssl.create_default_context()
            server_socket = context.wrap_socket(server_socket,server_hostname=parsed_data["server_host"])

        url = 'GET {} HTTP/1.0\r\nHOST: {}\r\n\r\n'.format(parsed_data["server_path"],parsed_data["server_host"])

        # we send request to the server
        server_socket.sendall(url.encode())
        print(f"request to {parsed_data['server_host']}{parsed_data['server_path']}")
        server_socket.settimeout(5)
        response =b''

        try:
            #Recive the response from the server
            while True:
                data = server_socket.recv(4096)
                response += data
                if not data:
                    server_socket.close()
                    print("socket close")
                    break

            # Get the status_code from the response
            header = response.split(b"\r\n\r\n")[0]
            decoded_header = header.decode()
            status_code = decoded_header.split("\r\n")[0].split(" ")[1]
            if(status_code == "404"):
                pass
            elif(status_code == "304"):
                pass
            elif(300 >=  int(status_code) and int(status_code) < 400):
               pass 

            # modify the response by adding proxy ip and proxy port 
            body = response[len(header)+4:]
            decoded_header = decoded_header+ "\r\nproxy_ip_addr: {}\r\nproxy_port: {}\r\n\r\n".format(SERVER_IP,SERVER_PORT)
            modified_response = decoded_header.encode() +body 

            # print(modified_response)
        except Exception as e:
            print("Exception {}".format(e))
            server_socket.settimeout(0)
            modified_response = b"HTTP/1.0 404 File not found\r\n" 

        return modified_response

    def saveUserData(self,client_data,requested_data):
        """
        This function save the request made by the client in data.json file.
        Here we save the data for each clent ip that makes request through this proxy
        The format is

        {
            "server_host": "localhost",
            "server_port": 8080,
            "server_path": "/hello.html",
            "is_valid": 1,
            "date_time": "2023-11-04 19:17:45.616163"
        }
        we take two argument 
        1. client_data which is tuple containing ip and port
        2. requested_data which is a dict which holds details as server_host,server_port,server_path
        """
        json_file_path = "data.json"
        isFilePresent = os.path.exists(json_file_path) # check if file exists or not

        client_ip,client_port = client_data # get the ip and port

        date_time = datetime.now()
        requested_data["date_time"] = str(date_time) # add the date and time to the requested_data dict

        json_data = {}
        key =f"{client_ip}"  # use ip  as key

        # key ="1"
        if(isFilePresent):

            # append the data to the previous data that is already present in the json file
            with open(json_file_path, 'r') as json_file:
                new_data = json.load(json_file)

                #get data using ip from the previous data
                get_data = new_data.get(key)
                if(get_data):

                    # append data to the exists ip datas 
                    get_data.append(requested_data)
                else:
                    # create new data when no data is present
                    get_data = requested_data
                new_data[key] = get_data

                # save the new_data to the json file
                with open(json_file_path, 'w') as json_file:
                    json.dump(new_data, json_file, indent=4)
        else:
            # create a new json file and add first data when the file do nor exists.
            json_data = {key:[requested_data]}
            with open(json_file_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=4)

    def plotGraph(self,x_axis,y_axis,name):
        """
        This function create graph and saves the graph
        this function takes 3 argument
        1. x_axis is list that we need to show in x axis of graph
        2. y_axis is list that we need to show in y axis of graph
        3. name is string that will be the name od saved  graph
        """
        plt.bar(x_axis,y_axis)
        plt.xticks( rotation=20, ha='right')
        plt.savefig(name,dpi=400)
        plt.close()

    def createGraphData(self):
        """
        This Function reads the json file and creates the data for the the graph
        """
        # check if json file exists
        isFilePresent = os.path.exists(json_file_path)
        total_no_of_request = 0
        request_made_today = 0
        request_made_this_week= 0
        request_made_this_month= 0
        today = date.today()
        today_day = today.day
        one_week = timedelta(days=7)
        one_month = timedelta(days=30)

        request_by_day = {
            'Sunday': 0,
            'Monday': 0,
            'Tuesday':0,
            'Wednesday':0,
            'Thursday':0,
            'Friday':0,
            'Saturday':0
        }
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        request_by_month = {
            'January': 0,
            'February': 0,
            'March': 0,
            'April': 0,
            'May': 0,
            'June': 0,
            'July': 0,
            'August': 0,
            'September': 0,
            'October': 0,
            'November': 0,
            'December': 0
        }
        if(isFilePresent):
            with open(json_file_path, 'r') as json_file:
                # save  the json data
                data = json.load(json_file)
                for key,values in data.items():
                    # print(key,values)

                    #loop over the requested_data in the json file
                    for req in values:
                        total_no_of_request+=1
                        # print(req["date_time"])

                        # get the date(yyyy-mm-dd) from the requested_data dict
                        get_date = req["date_time"].split(" ")[0]
                        get_day_arr = get_date.split("-")
                        get_day_no = get_day_arr[2]
                        get_month_no = get_day_arr[1]

                        #create datetime object from the date we fetched
                        date_time = datetime.strptime(req['date_time'], '%Y-%m-%d %H:%M:%S.%f')

                        # check if the date in within one week
                        is_within_week = -(date_time.date()-today)<one_week

                        # check if the date in within one month
                        is_within_month = -(date_time.date()-today)<one_month

                        # if date is of today then increment request_made_today
                        if(today_day == int(get_day_no)):
                            request_made_today += 1

                        # if date is of within one week then increment request_by_day
                        if(is_within_week):
                            request_made_this_week += 1
                            day_of_week = date_time.strftime('%A') 
                            request_by_day[day_of_week]+=1

                        current_month_name = month_names[int(get_month_no)] 
                        request_by_month[current_month_name]+=1

                        # if date is of within one week then increment request_made_this_month
                        if(is_within_month):
                            request_made_this_month+= 1
                
                # call plotGraph function to create graph
                my_axis = list(request_by_month.values())
                mx_axis = list(request_by_month.keys())
                self.plotGraph(mx_axis,my_axis,"request_by_month.png")

                dy_axis = list(request_by_day.values())
                dx_axis = list(request_by_day.keys())
                self.plotGraph(dx_axis,dy_axis,"request_by_day.png")

                tx_axis = ["Today"]
                ty_axis = [request_made_today]
                self.plotGraph(tx_axis,ty_axis,"request_made_today.png")


    def handleClientThead(self,client_conn,client_addr,client_req_data):
        """
        This Function handle the client request
        here we parse the html , save the data of the client request 
        make request to the server
        """
        print("Client connected with address ",client_addr)
        # parse the html file
        parsed_data = self.parseRequest(client_req_data)

        # save the data to json file
        self.saveUserData(client_addr,parsed_data)

        # make request to the server and get he response
        server_response = self.forwardRequest(parsed_data)
        print("server resp :",server_response)

        decoded_headers = server_response.split(b"\r\n\r\n")[0].decode()
        headers_arr = decoded_headers.split("\r\n")
        headers_content_type =""
        for element in headers_arr:
            if(element):
                if("content-type:" in element.lower()):
                    headers_content_type = element
        new_response =server_response  

        # if the response is html file then we change the english in html to hindi
        if headers_content_type:
            if("text/html" in headers_content_type):
                body = server_response[len(decoded_headers)+4:].decode()
                body_arr = body.split("\n")
                modified_html = ""
                if(body_arr[0].lower()=="<!doctype html>"):
                    print("in convert")
                    modified_html = self.convertLanguageInHtml(body)
                    print("data =>",modified_html)
                    new_response = (decoded_headers+modified_html).encode()
        client_conn.sendall(new_response)
        client_conn.close()
        self.createGraphData()
        

# CONNECT www.cse.iith.ac.in:443 HTTP/1.1
# 'GET http://example.com/ HTTP/1.1'

    def convertLanguageInHtml(self,html):
        """
        This function converts the english language in the html file to hindi
        this function takes html string as argument
        """
        #ceate BeautifulSoup obj for the html
        soup=BeautifulSoup(html,"html.parser")
        tag = ["h1","h2","h3","h4","h5","h6","p","td","th","span"]

        # get the html element tag
        for headingElemenet in soup.find_all(tag):

            # get the string from the html tag
            string_value = headingElemenet.string 

            # convert the english to hindi
            trans = EngtoHindi(message=string_value)
            
            # replace the english to hindi
            headingElemenet.string = trans.convert

        return str(soup)

    def parseRequest(self,req_data):
        # url_arr = req_data.split('\r\n\r\n')
        """
        This function parse the request url 
        here there is only one argument 
        req_data is string, it is GET request recived
        """
        url_details = {"server_host":"","server_port":0,"server_path":"/","is_valid":0}

        # get the url form the req_data string by string first by \r\n and then by " "
        url_arr = req_data.split('\r\n')
        server_url_str = url_arr[0].split(" ")
        requested_url = server_url_str[1]

        # if requested_url start with / the skip the /
        if(requested_url[:1] == "/"):
            requested_url = requested_url[1:]

        # if requested_url has port 433 then add https://  
        if(requested_url.split(":")[-1] == "443"):
            if(requested_url[:4] != "http"):
                requested_url = "https://"+requested_url

        # call urlparse function form urllib module 
        paresed_word = urlparse(requested_url)

        # if we have http or https and domain or ip name then we update the url_details dict
        if(paresed_word.scheme and paresed_word.netloc):
            url_details["server_host"]= paresed_word.hostname
            url_details["server_port"] = 80
            if(paresed_word.scheme == "https"):
                url_details["server_port"] = 443
            if(paresed_word.path):
                url_details["server_path"] =  paresed_word.path
            url_details["is_valid"] = 1
            
            # extract port number using regex
            get_port_regex =re.findall(r':\d+',requested_url)
            if(get_port_regex):
                if(get_port_regex[0][0]==":" and get_port_regex[0][1:].isdigit()):
                    url_details["server_port"] = int(get_port_regex[0][1:])

        # print(url_details)
        return url_details

    def listenClient(self):
        while True:
            # accept the request from the client and create a thread to handle the client request
            client_conn,client_addr = self.poxyServerObj.accept()
            client_req_data = client_conn.recv(4096).decode('latin-1')
            start_new_thread(self.handleClientThead,(client_conn,client_addr,client_req_data))
            
httpProxy = ProxySever()
httpProxy.listenClient()

