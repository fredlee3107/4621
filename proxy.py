import socket
import threading
import re

class Server:
  def __init__(self):
    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serverSocket.bind(('', 12345))
    self.serverSocket.listen(10)
    print("server is ready")
  
  def connectionPending(self):
    threadNo = 0
    while True:
      incomingSocket, clientAddress = self.serverSocket.accept()
      print(clientAddress)
      threadNo = threadNo + 1
      thread = threading.Thread(name=str(clientAddress), target=self.threads, args=(incomingSocket, clientAddress, threadNo))
      thread.setDaemon(True)
      thread.start()
    self.serverSocket.close()
      
  def threads(self, incomingSocket, clientAddress, threadNo):
    print("I am thread number: " + str(threadNo))
    https = False
    clientRequest = incomingSocket.recv(4096).decode("utf-8")
    if clientRequest != None:
      print(clientRequest)
      requestLength = len(clientRequest)
      #print(requestLength)
      resp_part = clientRequest.split(' ')[0]
      #print(resp_part)
      if(resp_part.find('GET') != -1):
        #print("this is get")
        httpPart = clientRequest.split(' ')[1]
        #print(httpPart)
        #print(type(httpPart))
        accessableHTTP = True
        accessableHTTP = self.accessControl(httpPart)
        if accessableHTTP == True:
          doubleSlashPosition = httpPart.find('//')
          if doubleSlashPosition == -1:
            urlPart = httpPart[1:]
            #print(urlPart)
            urlConnect = urlPart.split('/')[0]            
            #print(urlConnect)
          else:
            if httpPart.split('//')[1][-1] == "/":
              urlPart = httpPart.split('//')[1][:-1]
              #print(urlPart)
              urlConnect = urlPart.split('/')[0]
              #print(urlConnect)
            else:
              urlPart = httpPart.split('//')[1]
              #print(urlPart)
              urlConnect = urlPart.split('/')[0]
              #print(urlConnect)
          urlCheckSlash = urlPart.split('/')[1:]
          urlAfterSlash = ""
          if urlCheckSlash != None:
            for path in urlCheckSlash:
              urlAfterSlash = urlAfterSlash + "/"
              urlAfterSlash = urlAfterSlash + path
          requestPortNumber = 80
          fileName = re.sub('[^0-9a-zA-Z]', '_', urlPart)
          #print(fileName)
          self.caching(fileName, incomingSocket, requestPortNumber, clientAddress, urlConnect, urlAfterSlash, https)
        else:
          incomingSocket.send(b'HTTP/1.1 404 not found\r\n\r\n')
      #else here for https!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1111
      elif (resp_part.find('CONNECT') != -1):
        urlPort = clientRequest.split(' ')[1]
        print(urlPort)
        HTTPSurl = urlPort.split(':')[0]
        print(HTTPSurl)
        HTTPSport = urlPort.split(':')[1]
        print(HTTPSport)
        if HTTPSport == str(443):
          print("this is https")
          https = True
        accessableHTTPS = self.accessControl(HTTPSurl)
        if accessableHTTPS == True:
          self.HTTPSrequest(incomingSocket, 443, clientAddress, HTTPSurl, clientRequest)
      else:  
        incomingSocket.send(b"HTTP/1.1 405 Method Not allowed\r\n\r\n")
    else:  
      incomingSocket.send("")
      incomingSocket.close()    

  def accessControl(self, input):
    result1 = input.find('sing.cse.ust.hk')
    if result1 == -1:
      return True
    else:
      return False

  def caching(self, fileName, incomingSocket, requestPortNumber, clientAddress, urlConnect, urlAfterSlash, https):
    # print(https)
    # print(fileName)
    # print(requestPortNumber)
    # print(clientAddress)
    # print(urlConnect)
    # print(urlAfterSlash + "anything?")
    try:
      cache = open(fileName, "rb")
      print("I am from cache")
      message = b""
      for line in cache:
        message = message + line
      
      #print(message)
      cache.close()
      #b = bytes(message, 'utf-8')
      #incomingSocket.send(b'HTTP/1.1 404 not found\r\n\r\n')
      incomingSocket.send(message)
    except FileNotFoundError:
      if https == False:
        proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxySocket.connect((urlConnect, requestPortNumber))
        webRequest = str()
        if urlAfterSlash != None:
          webRequest = "GET /" + urlAfterSlash[0:] + " HTTP/1.1\nHost: " + urlConnect + "\n\n"
          #webRequest = "GET http://example.com/ HTTP/1.1 \n\n"
          #print(webRequest)
        else:
          webRequest = "GET / HTTP/1.1\nHost:" + urlConnect + "\n\n"
          #print(webRequest + "noslash")
        sending = bytes(webRequest, 'utf-8')
        proxySocket.send(sending)
        fullWebsite = b""
        proxySocket.settimeout(5)
        while True:
          try:
            packets = proxySocket.recv(4096)#.decode("utf-8")
            #s = packets.decode("utf-8")
            #print(s)
          except socket.timeout:
            break
          if len(packets) > 0:
            fullWebsite = fullWebsite + packets
          else:
            break
        #print("b")
        #output = bytes(fullWebsite, 'utf-8')
        incomingSocket.send(fullWebsite)
        newfile = open(fileName, "wb")
        newfile.write(fullWebsite)
        newfile.close()
        proxySocket.close()
        incomingSocket.close()

  def HTTPSrequest(self, incomingSocket, portNumber, clientAddress, HTTPSurl, clientRequest):
    pass
#     proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     proxySocket.connect((HTTPSurl, 443))
    
#     clientRequest = clientRequest + "Authorization: Basic"
#     print (clientRequest)
#     request = bytes(clientRequest, 'utf-8')
#     proxySocket.send(request)
#     message = proxySocket.recv(4096)
#     print(message)

#     #incomingSocket.send(b'HTTP/1.1 404 not found\r\n\r\n')
#     incomingSocket.send(b'HTTP/1.1 200 OK')
#     proxySocket.close()
#     incomingSocket.close()

    
      


if __name__ == "__main__":
  server = Server()
  server.connectionPending()
