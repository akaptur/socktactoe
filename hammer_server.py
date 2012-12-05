from socktactoe_client import Client, HOST, PORT

MODE = "random"

clients = [Client(MODE) for i in range(100)]

while clients:
    for client in clients:
        client.play()
    clients = [client for client in clients if not client.done]