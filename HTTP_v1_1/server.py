import sys
import os
import logging
import time
import socket
import threading


# Set logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s HTTPServer [%(levelname)s] %(message)s',)
log = logging.getLogger()


class ClientThread(threading.Thread): 

    def __init__(self, clientConnection, 
                       clientIP, 
                       clientPort, 
                       serverIP,
                       serverPort,
                       bufferSize=1024,
                       threadGroup=None,
                       threadTarget=None,
                       threadName=None,
                       verbose=None,
                       www=os.getcwd()):
        if os.name == "posix":
            threading.Thread.__init__(self, group=threadGroup,
                                            target=threadTarget,
                                            name=threadName,
                                            verbose=verbose)
        else:
            threading.Thread.__init__(self, group=threadGroup,
                                      target=threadTarget,
                                      name=threadName)
        self.clientConnection = clientConnection
        self.clientIP = clientIP
        self.clientPort = clientPort
        self.serverIP = serverIP
        self.serverPort = serverPort
        self.bufferSize = bufferSize
        self.threadName = threadName
        self.www = www

    def run(self):
        """
        Request handler.
        """
        try:
            # Receive request from client
            log.info("[%s] Receiving client request", self.threadName)
            clientRequest = self.clientConnection.recv(self.bufferSize)

            # Decode client request to string
            clientRequest = bytes.decode(clientRequest)
            
            # Determine request method (GET, PUT and TERMINATE are supported)
#            serverIP = clientRequest.split(' ')[0]
#            serverPort = int(clientRequest.split(' ')[1])
            requestMethod = clientRequest.split(' ')[0]
            log.debug("[%s] Request Method: %s", self.threadName, requestMethod)

            # Determine requested URL
            requestedURL = clientRequest.split(' ')[1]
            
            # Determine requested File and Arguments.
            # If no file is specified by the browser,
            # load index.html by default.
            if '?' in requestedURL:
                requestedFile = requestedURL.split('?', 1)[0]
                requestedFile = requestedFile.split('/', 1)[1]
                requestedArgs = requestedURL.split('?', 1)[1]
            else:
                requestedFile = requestedURL.split('/', 1)[1]
                requestedArgs = None
            if requestedFile == '':
                requestedFile = 'index.html'
            self.requestedFile = os.path.join(self.www, requestedFile)
            log.debug("[%s] Requested File: %s", self.threadName, requestedFile)
            log.debug("[%s] Requested Arguments: %s", self.threadName, requestedArgs)

            if requestMethod == 'GET':
                self._handleGET()
            elif requestMethod == 'PUT':
                self._handlePUT()
            else:
                log.warn("[%s] Unknown HTTP request method: %s", self.threadName, requestMethod)
        except:
            log.error("[%s] Problem handling client request [%s]", self.threadName, clientRequest)
        
        # Close client connection
        log.info("[%s] Closing client connection", self.threadName)
        self.clientConnection.close()

    def _handleGET(self):
        """
        Handle GET.
        """
        header = ""
        payload = ""
        
        log.info("[%s] Serving web page: %s", self.threadName, self.requestedFile)

        if not os.path.exists(self.requestedFile):
            log.warn("[%s] %s: File not found!", self.threadName, self.requestedFile)
            log.debug("[%s] Sending HTTP response!", self.threadName)
            header = self._generateHeader(404)
            payload = self._generateHTML(404)
            httpResponse = self._createHTTPResponse(header, payload)
            self.clientConnection.send(httpResponse)
        else:
            try:
                log.debug("[%s] Sending HTTP response!", self.threadName)
                header = self._generateHeader(200)
                httpResponse = self._createHTTPResponse(header, payload)
                self.clientConnection.send(httpResponse)
                
                # Send requested file over TCP connection to the client
                with open(self.requestedFile, 'rb') as f:
                    payload = f.read(self.bufferSize)
                    while payload:
                        log.debug("[%s] 1024 bytes were sent.....", self.threadName)
                        self.clientConnection.send(payload)
                        payload = f.read(self.bufferSize)
                    
                    time.sleep(2)
                    
                    self.clientConnection.send("EOF".encode())
            except Exception as e:
                log.warn("[%s] %s: IOError!", self.threadName, self.requestedFile)
                log.debug("[%s] %r", self.threadName, e)
                log.debug("[%s] Sending HTTP response!", self.threadName)
                header = self._generateHeader(404)
                payload = self._generateHTML(404)
                httpResponse = self._createHTTPResponse(header, payload)
                self.clientConnection.send(httpResponse)

    def _handlePUT(self):
        """
        Handle PUT.
        """
        log.info("[%s] Writing to web server: %s", self.threadName, self.requestedFile)

        if not os.path.exists(self.requestedFile):
            open(self.requestedFile, 'wb').close()

        try:
            # Writing to requested file at the server
            with open(self.requestedFile, 'wb') as f:
                while True:
                    data = self.clientConnection.recv(self.bufferSize)

                    if data.decode("utf-8").strip() == u"EOF":
                        break
                    else:
                        log.debug("[%s] 1024 bytes were written.....", self.threadName)
                        f.write(data)

            log.debug("[%s] Sending HTTP response!", self.threadName)
            header = self._generateHeader(200, 'PUT')
            httpResponse = self._createHTTPResponse(header, "")
            self.clientConnection.send(httpResponse)
        except Exception as e:
            log.warn("[%s] %s: IOError!", self.threadName, self.requestedFile)
            log.debug("[%s] %s", self.threadName, e)
            header = self._generateHeader(204, 'PUT')
            payload = self._generateHTML(204)
            httpResponse = self._createHTTPResponse(header, payload)
            self.clientConnection.send(httpResponse)
    
    def _createHTTPResponse(self, header, payload):
        log.debug("[%s] Creating HTTP server response", self.threadName)
        httpResponse = header
        httpResponse += payload
        return httpResponse.encode()

    def _generateHeader(self, code, method='GET'):
        """
        Generates HTTP response headers.
        """
        header = ""

        # Determine response code
        if code == 200 and method == 'GET':
            header = 'HTTP/1.1 200 OK\n'
        elif code == 200 and method == 'PUT':
            header = 'HTTP/1.1 200 OK File Created\n'
        elif code == 204:
            header = 'HTTP/1.1 204 No Content\n'
        elif code == 404:
            header = 'HTTP/1.1 404 Not Found\n'
    
        # Add more header fields
        date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += 'Date: %r\n' % date
        header += 'Server: HTTPServer [%s:%d]\n' % (self.serverIP, self.serverPort)
        header += 'Connection: keep-alive\n\n'
    
        return header

    def _generateHTML(self, code):
        """
        Generates HTML page as a payload for a HTTP response.
        """
        html = ""

        # Create HTML based on response code
        if code == 200:
            html += b"<html><body><p>Status Code 200: OK!</p></body></html>"
        elif code == 204:
            html += b"<html><body><p>Status Code 204: No Content!</p></body></html>"
        elif code == 404:
            html += b"<html><body><p>ERROR 404: File not found!</p></body></html>"
    
        return html


class HTTPServer(object):
    
    def __init__(self, hostname="127.0.0.1", port=8080, www=os.getcwd(), capacity=10):
        self.hostname = hostname
        self.port = port
        self.www = www
        self.capacity = capacity

    def start(self):
        """ 
        Start the server.
        """
        log.info("Launching HTTP server on %s:%d", self.hostname, self.port)

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.hostname, self.port))
        except Exception as e:
            log.warn("Could not aquire port %d", self.port)
            log.debug(e)
            
            try:
                log.debug("Launching HTTP server on %s:8080", self.hostname)
                self.socket.bind((self.hostname, self.port))
            except Exception as e:
                log.error("Failed to launch HTTP server!")
                log.debug(e)
                self.stop()
                sys.exit(1)

        log.info("HTTP server is successfully launched at %s:%d", self.hostname, self.port)
        log.info("Press Ctrl+C to shut down the running HTTP server and exit.")

        log.info("HTTP server is listening at port %d", self.port)
        self.socket.listen(self.capacity)

        while True:
            # Established client connection
            clientConnection, (clientIP, clientPort) = self.socket.accept()
            log.info("Established client connection with %s:%d", clientIP, clientPort)

            # Start a new HTTP server socket thread for the new connection
            threadName = "%d->%s:%d" % (self.port, clientIP, clientPort)
            newConnection = ClientThread(clientConnection, 
                                         clientIP, 
                                         clientPort,
                                         self.hostname,
                                         self.port,
                                         threadName=threadName,
                                         www=self.www)
            #newConnection.daemon = True
            log.debug("New HTTP server socket thread started for the client %s:%d", clientIP, clientPort)
            
            newConnection.start()
            
    def stop(self):
        """ 
        Stop the server.
        """
        log.info("Shutting down HTTP server %s:%d", self.hostname, self.port)

        try:
            # Wait for completion
            for t in threading.enumerate():
                if t is threading.current_thread():
                    continue
                
                logging.debug('Joining %s', t.getName())
                t.join()
            
            # Shutdown the socket
            self.socket.shutdown(socket.SHUT_RDWR)
            
            # Give some time to the server
            time.sleep(10)
        except Exception as e:
            log.error("Could not shut down the socket!")
            log.debug(e)