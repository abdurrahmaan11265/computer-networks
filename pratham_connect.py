import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("192.168.2.214", 9876))

while True:
    data = input("You: ")
    sock.send(data.encode())
    if data.lower() == "exit":
        break
    response = sock.recv(1024)
    print("Server:", response.decode())
sock.close()
