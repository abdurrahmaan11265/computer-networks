import socket
import sys
from datetime import datetime, timezone
import os


def ok_res_html(file_path):
    parts = file_path.replace("\\", "/").split("/")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(base_dir, "resources")
    abs_path = os.path.join(resources_dir, *parts)

    abs_path = os.path.abspath(abs_path)
    if not abs_path.startswith(resources_dir):
        return error_res_html("403 Forbidden")

    print("Looking for:", abs_path)

    message = "200 OK"
    try:
        with open(abs_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        return error_res_html("404 Not Found")
    except Exception as e:
        return error_res_html("500 Internal Server Error")

    content_bytes = content.encode("utf-8")
    content_length = len(content_bytes)

    date_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    response = (
        f"HTTP/1.1 {message}\r\n"
        f"Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {content_length}\r\n"
        f"Date: {date_str}\r\n"
        f"Server: Simple HTTP Server\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"{content}"
    )
    return response


def error_res_html(message):
    print(f"Error: {message}")
    content = f"""  
    <!DOCTYPE html>
    <html>
    <head><title>{ message }</title></head>
    <body>
        <h1>{ message }</h1>
        <p>The requested resource could not be served.</p>
        <hr>
        <p><em>Simple HTTP Server</em></p>
    </body>
    </html>
    """

    content_bytes = content.encode("utf-8")
    content_length = len(content_bytes)

    date_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    response = (
        f"HTTP/1.1 {message}\r\n"
        f"Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {content_length}\r\n"
        f"Date: {date_str}\r\n"
        f"Server: Simple HTTP Server\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"{content}"
    )
    return response


def handle_client(client_socket, addr):
    print(f"Connection from: {addr}")
    try:
        data = client_socket.recv(4096)
        if not data:
            return

        data = data.decode("utf-8").splitlines()[0]
        parts = data.split()
        if len(parts) < 3:
            response = error_res_html("400 Bad Request")
            client_socket.sendall(response.encode("utf-8"))

        method, path, http_version = parts
        print(f"Request: {method} {path} {http_version}")
        if method != "GET":
            response = error_res_html("405 Method Not Allowed")
        else:
            if path == "/":
                response = ok_res_html("index.html")
            else:
                response = ok_res_html(path.lstrip("/"))

        client_socket.sendall(response.encode("utf-8"))

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        client_socket.close()
        print(f"Connection closed: {addr}")


def start_server(host="127.0.0.1", port=8080):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    server_socket.settimeout(1.0) 
    print(f"Server is listening on {host}:{port}")

    try:
        while True:
            try:
                client_socket, addr = server_socket.accept()
                handle_client(client_socket, addr)
            except socket.timeout:
                continue 
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
    finally:
        server_socket.close()
        print("Server socket closed.")


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8080

    try:
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
        if len(sys.argv) > 2:
            host = sys.argv[2]
    except ValueError:
        print("Usage: python server.py [port] [host]")
    start_server(host, port)
