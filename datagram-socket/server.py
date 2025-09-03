import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

interface = "127.0.0.1"
port = 54321
sock.bind((interface, port))
print("Server is listening on {}:{}".format(interface, port))

data, addr = sock.recvfrom(1024)
print("Client = {}, Data = {}".format(addr, data.decode()))

data1, addr1 = sock.recvfrom(1024)
print("Client = {}, Data = {}".format(addr1, data1.decode()))

data2, addr2 = sock.recvfrom(1024)
print("Client = {}, Data = {}".format(addr2, data2.decode()))