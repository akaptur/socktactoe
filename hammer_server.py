from socktactoe_client import Client, HOST, PORT
import sys

MODE = "random"

num_clients = int(sys.argv[1]) if len(sys.argv) == 2 else 10

clients = [Client(MODE) for i in range(num_clients)]

while clients:
    for client in clients:
        client.play()
    clients = [client for client in clients if not client.done]