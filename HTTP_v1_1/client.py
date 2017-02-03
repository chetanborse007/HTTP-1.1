import socket
from pathlib import Path

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

        result = self.socket.recv(10000) # Receiving a result from the server
        print(result)
        self.socket.close() # Closing the TCP connection

    def send_put_request(self):
        if Path(self.filename).is_file(): # Checking if the given file is valid
            file_content = open(self.filename,'r').read() # Reading the given file content
            self.socket.send(file_content) # Sending the read file content
            server_reply = self.socket.recv(200) # Waiting for server response
            print(server_reply)
            self.socket.close() # Closing the connection
        else:
            print("Invalid file.")
            self.socket.close()
