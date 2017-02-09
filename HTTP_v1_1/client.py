import os
import time
import logging
import socket


# Set logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s HTTPClient [%(levelname)s] %(message)s',)
log = logging.getLogger()


class HTTPClient:

    def __init__(self, clientIP, 
                       clientPort,
                       clientDirectory=os.path.join(os.getcwd(), "data", "client")):
        self.clientIP = clientIP
        self.clientPort = clientPort
        self.clientDirectory = clientDirectory

        # Creating a socket
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, serverIP, serverPort):
        """
        Connect to the server.
        """
        try:
            self.clientSocket.connect((serverIP, serverPort)) 
        except Exception as e:
            print("Something is wrong with %s and %d: %s" % (serverIP, serverPort, e))

    def request(self, method, filename):
        if method == "GET":
            self.get(method, filename)
        elif method == "PUT":
            self.put(method, filename)
    
    def get(self, method, filename):
        # Building a GET request
        request = (method + " /" + filename + " HTTP/1.1\n" +
                   "Host: " + self.clientIP + "\n\n")
        
        # Send request to server
        self.clientSocket.send(request.encode())
        
        # Receive server response
        response = self.clientSocket.recv(2048)
        response = response.decode('utf-8')
        print(response)
        
        # Start fetching file, if GET is successful
        if "HTTP/1.1 200 OK" in response:
            try:
                file = os.path.join(self.clientDirectory, filename)
                with open(file, 'wb') as f:
                    while True:
                        data = self.clientSocket.recv(1024)
                    
                        if data.strip() == "EOF":
                            break
                        else:
                            print('1024 bytes received.....')
                            f.write(data)
            except Exception as e:
                print(e)

    def put(self, method, filename):
        # Checking if the given file is valid
        if not os.path.isfile(self.filename):
            raise IOError("File does not exist!")
        
        # Building a PUT request
        request = (method + " /" + filename + " HTTP/1.1\n" +
                   "Host: " + self.clientIP + "\n\n")
        
        # Send request to server
        self.clientSocket.send(request.encode())
        
        # Wait for some time after sending PUT request
        time.sleep(2)
        
        # Send file over TCP connection to the server
        try:
            file = os.path.join(self.clientDirectory, filename)
            with open(file, 'rb') as f:
                payload = f.read(1024)
                while payload:
                    print("1024 bytes were sent.....")
                    self.clientSocket.send(payload)
                    payload = f.read(1024)
                self.clientSocket.send("EOF".encode())
        except Exception as e:
            print(e)

        time.sleep(2)
		
        response = self.clientSocket.recv(2048)
        print(str(response))
    
    def close(self):
        """
        Close the TCP connection.
        """
        self.clientSocket.close()

