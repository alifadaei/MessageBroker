# echo-client.py

from msilib.schema import Binary
from pydoc_data.topics import topics
import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 1373  # The port used by the server


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    msg = input('msg: ')
    s.sendall(bytes(msg, 'utf-8'))
    if msg.split(' ')[0] == 'publish':  # publish
        data = s.recv(1024).decode('utf-8')
        if data == 'puback':
            print("your message published suucessfully")
        else:
            print("your message publishing failed")

    elif msg.split(' ')[0] == 'subscribe':  # subscribe
        data = s.recv(1024).decode('utf-8')
        if data == 'suback':
            print(f'subscribing on {" ".join(msg.split(" ")[1:])}')
        else:
            print('subscribing failed')
        data = s.recv(1024).decode('utf-8')
        if data:
            print(data)

    elif msg.split(' ')[0] == 'ping':
        data = s.recv(1024).decode('utf-8')
        print(data)
