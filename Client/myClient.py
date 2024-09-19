#remove files other file before start
import sys, os
import webbrowser
import requests
from bs4 import BeautifulSoup
from http.client import HTTPConnection
HTTPConnection._http_vsn_str = 'HTTP/1.0'
files = []

prefix = ''

def makeGetRequest(ip_address,port,prefix,filePath):
    ip_type = "http"
    if port == 443:
        ip_type = 'https'
    url = '{}://{}:{}/{}'.format(ip_type,ip_address, port, prefix + filePath)
    print("Making request to : - ",url)
    response = requests.get(url)
    return response

def parseArguments(arguments):
    global prefix
    address, port = arguments[0], int(arguments[1])
    filePath = arguments[-1]
    if len(arguments) == 5:
        prefix = 'http://{}:{}/'.format(arguments[2], int(arguments[3]))
        # print("pefix",prefix)
    return address, port, filePath

def parseHTML(filePath, response):
    with open(filePath, 'w') as file:
        file.write(response.content.decode())
        files.append(filePath)
    with open(filePath, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')
        allCss = soup.findAll('link', href=True)
        for link in  allCss:
            stylePath = link.get('href')
            if(stylePath.find('.') > -1):

                # style = requests.get('https://{}:{}/{}'.format(address, port, prefix + stylePath))
                styleResponse = makeGetRequest(address,port,prefix,stylePath)
                local_css_name = stylePath.split("/").pop()
                with open(local_css_name, 'w') as file:
                    file.write(styleResponse.text)
                    files.append(local_css_name)
        allScripts = soup.findAll('script')
        for jsTag in allScripts:
            jsSrc = jsTag.get("src")
            if(jsSrc):
                scriptResponse = makeGetRequest(address,port,prefix,jsSrc)
                # script = requests.get('https://{}:{}/{}'.format(address, port, prefix + jsSrc))
                local_js_name = jsSrc.split("/").pop()
                with open(local_js_name, 'w') as file:
                    file.write(scriptResponse.text)
                    files.append(local_js_name)
        if soup.find('img'):
            for imageObject in soup.find_all('img'):
                imagePath = imageObject.get('src')
                imageResponse = makeGetRequest(address,port,prefix,imagePath)
                # image = requests.get('https://{}:{}/{}'.format(address, port, prefix + imagePath))
                local_img_name = imagePath.split("/").pop()
                with open(local_img_name, 'wb') as file:
                    file.write(imageResponse.content)
                    files.append(local_img_name)
    return


# TO make request direcltly to server
# python3 Client.py www.example.com 80 index.html

# TO make request through proxy to server
# python3 Client.py localhost 8082 www.example.com 80 index.html   
arguments = sys.argv[1:]

address, port, filePath = parseArguments(arguments)
# ip_p = "http"
# if port == 443:
#     ip_p = 'https'
# url = '{}://{}:{}/{}'.format(ip_p,address, port, prefix + filePath)
# print("Making request to : - ",url)
# response = requests.get(url)
response = makeGetRequest(address,port,prefix,filePath)
print("Response:-")
print(response.content)

if response.status_code == 200:

    if filePath.endswith('.html'):
        parseHTML(filePath, response)

    else:
        with open(filePath, 'wb') as file:
            file.write(response.content)
            files.append(filePath)

else:
    with open('error.html', 'wb') as file:
        file.write(response.content)
        files.append('error.html')
        filePath = 'error.html'

webbrowser.open(filePath)

for file in files:
    os.remove(file)
