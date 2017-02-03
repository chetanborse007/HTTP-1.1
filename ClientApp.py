from HTTP_v1_1 import client
import sys

cli = client.Socket(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
cli.make_connection()

if sys.argv[3] == "GET":
    cli.send_get_request()
elif sys.argv[3] == "PUT":
    cli.send_put_request()