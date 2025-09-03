import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

interface = "127.0.0.1"
port = 54321
sock.bind((interface, port))

data, addr = sock.recvfrom(1024)
print("Client = {}, Data = {}".format(addr, data.decode()))