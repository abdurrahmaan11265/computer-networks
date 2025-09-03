import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("127.0.0.1", 54321))

sock.send("Hello1".encode())
sock.send("Hello2".encode())
sock.send("Hello3".encode())

