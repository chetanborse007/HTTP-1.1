import os
import time
import logging
import socket


# Set logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s HTTPClient [%(levelname)s] %(message)s',)
log = logging.getLogger()


class ConnectionError(Exception):
    pass


class RequestError(Exception):
    pass


class HTTPClient:

    def __init__(self, clientIP, 
                       clientPort,
                       clientDirectory=os.path.join(os.getcwd(), "data", "client")):
        self.clientIP = clientIP
        self.clientPort = clientPort
        self.clientDirectory = clientDirectory

        # Creating a socket
        log.info("Creating client socket.....")
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, serverIP, serverPort):
        """
        Connect to the HTTP server.
        """
        log.info("Connecting with HTTP server %s:%d", serverIP, serverPort)

        try:
            self.clientSocket.connect((serverIP, serverPort)) 
        except Exception as e:
            log.error("Could not establish connection with the server!")
            log.debug(e)
            raise ConnectionError("[%s:%d] Connection with HTTP server failed!" % (serverIP, serverPort))

    def request(self, method, filename):
        """
        Send http request to HTTP server.
        """
        if method == "GET":
            self.get(method, filename)
        elif method == "PUT":
            self.put(method, filename)
    
    def get(self, method, filename):
        """
        GET request.
        """
        filename = os.path.join(self.clientDirectory, filename)

        # Send a GET request to HTTP server
        log.info("[%s] Sending http request to HTTP server.....", method)
        request = (method + " /" + filename.rsplit(os.sep, 1)[1] + " HTTP/1.1\n" +
                   "Host: " + self.clientIP + "\n\n")
        self.clientSocket.send(request.encode())
        log.debug("[%s] HTTP Request: %s", method, request)
        
        # Receive server response
        response = self.clientSocket.recv(2048)
        response = response.decode('utf-8')
        log.info("[%s] HTTP Response: %s", method, response)
        
        # Start fetching file, if GET is successful
        if "HTTP/1.1 200 OK" in response:
            try:
                with open(filename, 'wb') as f:
                    while True:
                        data = self.clientSocket.recv(1024)
                    
                        if data.decode("utf-8").strip() == u"EOF":
                            break
                        else:
                            log.debug("[%s] 1024 bytes received....." % (method,))
                            f.write(data)
            except Exception as e:
                log.error("[%s] HTTP request failed!" % (method,))
                log.debug(e)
                raise RequestError("[%s] HTTP request failed!" % (method,))

    def put(self, method, filename):
        """
        PUT request.
        """
        filename = os.path.join(self.clientDirectory, filename)

        # Checking if the given file is valid
        if not os.path.isfile(filename):
            raise RequestError("[%s] File does not exist!" % (method,))
        
        # Send a PUT request to HTTP server
        log.info("[%s] Sending http request to HTTP server.....", method)
        request = (method + " /" + filename.rsplit(os.sep, 1)[1] + " HTTP/1.1\n" +
                   "Host: " + self.clientIP + "\n\n")
        self.clientSocket.send(request.encode())
        log.debug("[%s] HTTP Request: %s", method, request)
        
        # Wait for some time after sending PUT request
        time.sleep(2)
        
        # Send file over TCP connection to the server
        try:
            with open(filename, 'rb') as f:
                payload = f.read(1024)
                while payload:
                    log.debug("[%s] 1024 bytes were sent....." % (method,))
                    self.clientSocket.send(payload)
                    payload = f.read(1024)
                
                time.sleep(2)
                
                self.clientSocket.send("EOF".encode())
        except Exception as e:
            log.error("[%s] HTTP request failed!" % (method,))
            log.debug(e)
            raise RequestError("[%s] HTTP request failed!" % (method,))

        time.sleep(2)

        response = self.clientSocket.recv(2048)
        response = response.decode('utf-8')
        log.info("[%s] HTTP Response: %s", method, response)
    
    def close(self):
        """
        Close the TCP connection.
        """
        log.info("Closing client socket.....")
        
        try:
            self.clientSocket.close()
        except Exception as e:
            log.error("Could not shut down the socket!")
            log.debug(e)

