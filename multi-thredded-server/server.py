import threading
import socket

# If I have multiple client threads (each handling its own socket), how does the OS make sure that the thread handling socket1 gets only data from socket1, and not from another client’s socket?


def handle_client(client_sock, addr, running_flag):
    client_sock.settimeout(1.0)
    while running_flag[0]:
        try:
            data = client_sock.recv(1024)
            if not data:
                break
            print(f"Client {addr}, Data = {data.decode()}")
        except socket.timeout:
            continue
        except OSError:
            break
    client_sock.close()
    print(f"Client {addr} disconnected")


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
interface = "127.0.0.1"
port = 54321
sock.bind((interface, port))
sock.listen(5)
print("Server is listening on {}:{}".format(interface, port))

clients = []
client_threads = []

running = True
running_flag = [True]
sock.settimeout(1.0)

while running:
    try:
        client_sock, addr = sock.accept()
        print("Connection from {}".format(addr))
        clients.append((client_sock, addr))
        client_thread = threading.Thread(
            target=handle_client, args=(client_sock, addr, running_flag)
        )
        client_thread.start()
        client_threads.append(client_thread)
        
    except socket.timeout:
        continue
    except KeyboardInterrupt:
        print("\nShutting down server...")
        running = False
        running_flag[0] = False

for client_sock, addr in clients:
    try:
        client_sock.close()
    except OSError:
        pass
    # client_sock.close()

for thread in client_threads:
    thread.join()

sock.close()
