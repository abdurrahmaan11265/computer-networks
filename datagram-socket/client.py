import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("127.0.0.1", 54321)

sock.sendto("Hello1, Server!".encode(), server_address)
sock.sendto("Hello2, Server!".encode(), server_address)
sock.sendto("Hello3, Server!".encode(), server_address)