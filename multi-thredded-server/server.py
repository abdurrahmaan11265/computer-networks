import threading
import socket

# If I have multiple client threads (each handling its own socket), how does the OS/Python make sure that the thread handling socket1 gets only data from socket1, and not from another client’s socket?

def handle_client(client_sock, addr):
    while True:
        data = client_sock.recv(1024)
        if not data:
            print(f"Client {addr} disconnected")
            client_sock.close()
            break
        print("Client = {}, Data = {}".format(addr, data.decode()))

    

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
interface = "127.0.0.1"
port = 54321
sock.bind((interface, port))
sock.listen(5)
print("Server is listening on {}:{}".format(interface, port))

clients = []
client_threads = []

running = True

while running:
    try:
        client_sock, addr = sock.accept()
        print("Connection from {}".format(addr))
        clients.append((client_sock, addr))
        client_thread = threading.Thread(target=handle_client, args=(client_sock, addr))
        client_thread.start()
        client_threads.append(client_thread)
    except KeyboardInterrupt:
        print("Shutting down server...")
        running = False

for thread in client_threads:
    thread.join()

sock.close()




    