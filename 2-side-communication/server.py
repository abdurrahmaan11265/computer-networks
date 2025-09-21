import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
interface = "127.0.0.1"
port = 54321
sock.bind((interface, port))

sock.listen()
print("Server is listening on {}:{}".format(interface, port))

client_sock, addr = sock.accept()
print("Connection from {}".format(addr))

while True:
    data = client_sock.recv(1024)
    if not data:
        break
    print(f"Client {addr}, Data = {data.decode()}")
    client_sock.sendall("Hello from server0 \n".encode())
    client_sock.sendall("Hello from server1 \n".encode())
    # client_sock.send("Hello from server0".encode())
    # client_sock.send("Hello from server1".encode())