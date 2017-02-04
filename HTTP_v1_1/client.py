import socket
import os
import time


class Socket:
    def __init__(self,host,port,command,filename):
        #Initializing hostname, port number, method and filename
        self.host = host
        self.port = int(port)
        self.command = command
        self.filename = filename

        # Creating a socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def make_connection(self):
        try:
            self.socket.connect((self.host,self.port)) # Connecting with the server

        except Exception as e:
            print("Something is wrong with %s and %d: %s" % (self.host,self.port,e))


    def send_get_request(self):
        request = self.command + " /" + self.filename + " HTTP/1.1\nHost: " + self.host + "\n\n" # Building a GET request
        self.socket.send(request.encode()) # TO convert string request into bytes

        result = self.socket.recv(2048)
        print(result)
        
        if "HTTP/1.1 200 OK" in result:
            with open('ReceivedFile.txt', 'wb') as f:
                while True:
                    data = self.socket.recv(1024)
                    
                    if data.strip() == "EOF":
                        break
                    else:
                        print('1024 bytes received.....')
                        f.write(data)
        
            print("Displaying ReceivedFile.txt....")
            with open('ReceivedFile.txt', 'r') as f:
                print(f.read())
        
        self.socket.close() # Closing the TCP connection

    def send_put_request(self):
        if os.path.isfile(self.filename): # Checking if the given file is valid
            # TPDO: Send PUT request first
            
            # Wait for some time after sending PUT request
            time.sleep(2)
            
            # Send file over TCP connection to the server
            filename = os.path.join(os.getcwd(), "ReceivedFile.txt")
            with open(filename, 'rb') as f:
                payload = f.read(1024)
                while payload:
                    print("1024 bytes were sent.....")
                    self.socket.send(payload)
                    payload = f.read(1024)
                self.clientConnection.send("EOF")
            
            server_reply = self.socket.recv(2048) # Waiting for server response
            print(server_reply)
            
            self.socket.close() # Closing the connection
        else:
            print("Invalid file.")
            self.socket.close()
