import socket

# takes IP type and socket type as arguments
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket successfully created")


interface = "127.0.0.1"
port = 54321
sock.bind((interface, port))
print(f"Socket bound to {interface}:{port}")

sock.listen()
print("Socket is listening")

conn, addr = sock.accept()
print(f"Got connection from client: {addr}")

while True:
    data = conn.recv(1024)
    if not data:
        break
    print(f"Data from client: {data.decode()}")

conn.close()
sock.close()
print("Connection closed")