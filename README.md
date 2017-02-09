# HTTP-v1.1


## DESCRIPTION
Implementation of an HTTP Client and Server that run a simplified version of HTTP/1.1

Methods supported:
  1. GET
  2. PUT


## RUN SERVER
python ServerApp.py -t [hostname] -p [port] -w [web_server_directory]

e.g. python ServerApp.py -t "127.0.0.1" -p 8080


## RUN CLIENT
python ClientApp.py -s [client_ip] -t [server_ip] -p [server_port] -m [method] -f [filename] -d [client_directory]

#### GET
python ClientApp.py -t "127.0.0.1" -p 8080 -m "GET" -f "index.html"

#### PUT
python ClientApp.py -t "127.0.0.1" -p 8080 -m "PUT" -f "client_index.html"

