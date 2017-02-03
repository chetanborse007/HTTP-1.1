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
        threading.Thread.__init__(self, group=threadGroup,
                                        target=threadTarget,
                                        name=threadName,
                                        verbose=verbose)
        self.clientConnection = clientConnection
        self.clientIP = clientIP
        self.clientPort = clientPort
        self.serverIP = serverIP
        self.serverPort = serverPort
        self.bufferSize = bufferSize
        self.threadName = threadName
        self.www = www

    def run(self):
        try:
            while True:
                # Receive request from client
                log.info("[%s] Receiving client request", self.threadName)
                clientRequest = self.clientConnection.recv(self.bufferSize)
    
                # Decode client request to string
                clientRequest = bytes.decode(clientRequest)
                
                # Determine request method (GET, PUT and TERMINATE are supported)
                serverIP = clientRequest.split(' ')[0]
                serverPort = int(clientRequest.split(' ')[1])
                requestMethod = clientRequest.split(' ')[2]
                log.debug("[%s] Request Method: %s", self.threadName, requestMethod)

                # If request method is 'TERMINATE', then break
                if requestMethod == "TERMINATE":
                    break
                
                # Determine requested URL
                requestedURL = clientRequest.split(' ')[3]
                
                # Determine requested File and Arguments.
                # If no file is specified by the browser,
                # load index.html by default.
                if '?' in requestedURL:
                    requestedFile = requestedURL.split('?', 1)[0]
                    requestedArgs = requestedURL.split('?', 1)[1]
                else:
                    requestedFile = requestedURL
                    requestedArgs = None
                if requestedFile == '/':
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
        header = ""
        payload = ""
        
        log.info("[%s] Serving web page: %s", self.threadName, self.requestedFile)

        if not os.path.exists(self.requestedFile):
            log.warn("[%s] %s: File not found!", self.threadName, self.requestedFile)
            header = self._generateHeader(404)
            payload = self._generateHTML(404)
        
        # Read file content
        if os.path.exists(self.requestedFile):
            try:
                with open(self.requestedFile, 'rb') as f:
                    header = self._generateHeader(200)
                    payload = f.read()
            except Exception as e:
                log.warn("[%s] %s: IOError!", self.threadName, self.requestedFile)
                header = self._generateHeader(404)
                payload = self._generateHTML(404)
        
        # Create HTTP server response
        log.debug("[%s] Creating HTTP server response", self.threadName)
        serverResponse = header.encode()
        serverResponse += payload
        
        # Send requested file over connection to the client
        log.debug("[%s] Sending HTTP server response over connection to the client", self.threadName)
        self.clientConnection.send(serverResponse)

    def _handlePUT(self):
        pass
    
    def _generateHeader(self, code):
        """
        Generates HTTP response headers.
        """
        header = ""

        # Determine response code
        if code == 200:
            header = 'HTTP/1.1 200 OK\n'
        elif code == 404:
            header = 'HTTP/1.1 404 Not Found\n'
    
        # Add more header fields
        date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += 'Date: %r\n' % date
        header += 'Server: HTTPServer [%s:%d]\n' % (self.serverIP, self.serverPort)
        header += 'Connection: close\n\n'
    
        return header

    def _generateHTML(self):
        html = ""

        # Create HTML based on response code
        if html == 404:
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