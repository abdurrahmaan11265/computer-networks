import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
interface = "127.0.0.1"
port = 54321
sock.connect((interface, port))

while True:
    msg = input("Enter message to send (or 'exit' to quit): ")
    if msg.lower() == 'exit':
        break
    sock.send(msg.encode())
    data = sock.recv(1024)
    if not data:
        break
    print(f"Received from server: {data.decode()}")