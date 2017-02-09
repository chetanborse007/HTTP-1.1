import os
import argparse

from HTTP_v1_1.client import HTTPClient
from HTTP_v1_1.client import ConnectionError
from HTTP_v1_1.client import RequestError


def ClientApp(**args):
    clientIP = args["client_ip"]
    clientPort = args["client_port"]
    serverIP = args["server_ip"]
    serverPort = args["server_port"]
    method = args["method"]
    filename = args["filename"]
    clientDirectory = args["client_directory"]
    
    httpClient = HTTPClient(clientIP, clientPort, clientDirectory)
    
    try:
        httpClient.connect(serverIP, serverPort)
        httpClient.request(method, filename)
    except ConnectionError as e:
        print("Unexpected exception in establishing connection with HTTP server!")
        print(e)
    except RequestError as e:
        print("Unexpected exception in http request to HTTP server!")
        print(e)
    except Exception as e:
        print("Unexpected exception!")
        print(e)
    finally:
        if httpClient:
            httpClient.close()


if __name__ == "__main__":
    # Argument parser
    parser = argparse.ArgumentParser(description='HTTP Client Application',
                                     prog='python \
                                           ClientApp.py \
                                           -s <client_ip> \
                                           -c <client_port> \
                                           -t <server_ip> \
                                           -p <server_port> \
                                           -m <method> \
                                           -f <filename> \
                                           -d <client_directory>')

    parser.add_argument("-s", "--client_ip", type=str, default="127.0.0.1",
                        help="Client hostname, default: 127.0.0.1")
    parser.add_argument("-c", "--client_port", type=int, default=8081,
                        help="Client port, default: 8081")
    parser.add_argument("-t", "--server_ip", type=str, default="127.0.0.1",
                        help="Server hostname, default: 127.0.0.1")
    parser.add_argument("-p", "--server_port", type=int, default=8080,
                        help="Server port, default: 8080")
    parser.add_argument("-m", "--method", type=str, default="GET",
                        help="Request method, default: GET")
    parser.add_argument("-f", "--filename", type=str, default="index.html",
                        help="File name, default: index.html")
    parser.add_argument("-d", "--client_directory", type=str, default=os.path.join(os.getcwd(), "data", "client"),
                        help="Client directory, default: /<Current Working Directory>/data/client/")

    # Read user inputs
    args = vars(parser.parse_args())

    # Run Client Application
    ClientApp(**args)