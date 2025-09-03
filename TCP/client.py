import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("127.0.0.1", 54321))


while True:
    text = input("Enter text to send to server (or 'exit' to quit): ")
    if text.lower() == 'exit':
        break
    sock.send(text.encode())

sock.close()