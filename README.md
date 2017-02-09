# HTTP-v1.1


## DESCRIPTION
Implementation of an HTTP Client and Server that run a simplified version of HTTP/1.1

Methods supported:
1. GET
2. PUT


## RUN SERVER
python ClientApp.py -s <client_ip> -t <server_ip> -p <server_port> -m <method> -f <filename> -d <client_directory>


## RUN CLIENT
python ClientApp.py -s <client_ip> -t <server_ip> -p <server_port> -m <method> -f <filename> -d <client_directory>

### GET
python ClientApp.py -t "127.0.0.1" -p "8080" -m "GET" -f "index.html"

### PUT
python ClientApp.py -t "127.0.0.1" -p "8080" -m "PUT" -f "client_index.html"

