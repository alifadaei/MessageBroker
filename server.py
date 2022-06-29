import socket
import threading
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 1373  # Port to listen on (non-privileged ports are > 1023)

clients = []
publishes = []
lock = threading.Lock()


class Client():
    def __init__(self, conn, addr, clients, publishes, lock) -> None:
        self.conn = conn
        self.addr = addr
        self.subscribes = []
        self.thread = threading.Thread(
            target=handler, args=(self, clients, publishes, lock))

    def sendMessage(self, msg):
        self.conn.sendall(bytes(msg, 'utf-8'))

    def close(self):
        self.conn.close()

    def start(self):
        self.thread.start()


class Publish():
    def __init__(self, msg, topic, publisher) -> None:
        self.publisher = publisher
        self.msg = msg
        self.topic = topic


def handler(client, clients, publishes, lock):
    with client.conn:
        print('Connected by', client.addr)
        data = client.conn.recv(1024).decode('utf-8')
        print(f"address: {client.addr} sent: {data}")
        data = data.split(' ')
        print
        if data[0] == 'publish':  # publish
            topic = data[1]
            message = data[2]
            client.sendMessage('puback')
            publish = Publish(message, topic, client)
            lock.acquire()
            publishes.append(publish)
            for clienti in clients:
                if topic in clienti.subscribes:
                    print(clienti.addr)
                    clienti.sendMessage(message)
            lock.release()

        elif data[0] == 'subscribe':  # subscribe
            client.sendMessage('suback')
            topics = data[1:]
            lock.acquire()
            client.subscribes.extend(topics)
            for publish in publishes:
                if publish.topic in client.subscribes:
                    client.sendMessage(publish.msg)
            lock.release()

        elif data[0] == 'ping':
            client.sendMessage('pong')

    print('clients: ', clients)
    print('publishes: ', publishes)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        # print('start listening!')
        conn, addr = s.accept()
        client = Client(conn, addr, clients, publishes, lock)
        clients.append(client)
        client.start()
        # print("accepted")
