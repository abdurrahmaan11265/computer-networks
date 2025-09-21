import socket
import sys
from datetime import datetime, timezone
import os
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore
import json
import random
import string

init(autoreset=True)

server_running = True


def is_good_path(file_path):
    parts = file_path.replace("\\", "/").split("/")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(base_dir, "resources")
    abs_path = os.path.abspath(os.path.join(resources_dir, *parts))

    is_inside = os.path.commonpath([resources_dir, abs_path]) == resources_dir

    return is_inside, abs_path


def handle_get(file_path, http_version, connection):
    is_good, abs_path = is_good_path(file_path)
    if not is_good:
        return error_res_html("403 Forbidden")

    # file extension
    ext = os.path.splitext(abs_path)[1].lower()

    # content-type mapping
    content_types = {
        ".html": "text/html; charset=utf-8",
        ".txt": "application/octet-stream",
        ".png": "application/octet-stream",
        ".jpg": "application/octet-stream",
        ".jpeg": "application/octet-stream",
    }

    if ext not in content_types:
        return error_res_html("415 Unsupported Media Type")

    try:
        if ext == ".html":
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
            content_bytes = content.encode("utf-8")
        else:
            with open(abs_path, "rb") as f:
                content_bytes = f.read()
    except FileNotFoundError:
        return error_res_html("404 Not Found")
    except Exception:
        return error_res_html("500 Internal Server Error")

    content_length = len(content_bytes)
    date_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # headers
    header_conn = "Connection: close"
    if http_version == "HTTP/1.1" and connection != "close":
        header_conn = "Connection: keep-alive"

    headers = [
        "HTTP/1.1 200 OK",
        f"Content-Type: {content_types[ext]}",
        f"Content-Length: {content_length}",
        f"Date: {date_str}",
        "Server: Simple HTTP Server",
        header_conn,
    ]

    if ext in [".txt", ".png", ".jpg", ".jpeg"]:
        filename = os.path.basename(abs_path)
        headers.append(f'Content-Disposition: attachment; filename="{filename}"')

    header_bytes = ("\r\n".join(headers) + "\r\n\r\n").encode("utf-8")

    return header_bytes + content_bytes


def error_res_html(message):
    print(Fore.RED + f"Error: {message}\n")
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

    headers = [
        f"HTTP/1.1 {message}",
        "Content-Type: text/html; charset=utf-8",
        f"Content-Length: {content_length}",
        f"Date: {date_str}",
        "Server: Simple HTTP Server",
        "Connection: close",
    ]

    header_bytes = ("\r\n".join(headers) + "\r\n\r\n").encode("utf-8")

    return header_bytes + content_bytes


def handle_post(path, headers, body, http_version, connection):
    # Only accept /upload for POST
    if path != "/upload":
        return error_res_html("404 Not Found")

    content_type = headers.get("content-type", "").lower()
    if content_type != "application/json":
        return error_res_html("415 Unsupported Media Type")

    try:
        data = json.loads(body.decode("utf-8"))
    except Exception:
        return error_res_html("400 Bad Request")

    # Ensure uploads directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    upload_dir = os.path.join(base_dir, "resources", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # Filename: upload_[timestamp]_[random_id].json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    filename = f"upload_{timestamp}_{random_id}.json"
    abs_path = os.path.join(upload_dir, filename)

    # Save JSON to file
    with open(abs_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Build response JSON
    response_body = {
        "status": "success",
        "message": "File created successfully",
        "filepath": f"/uploads/{filename}",
    }
    body_bytes = json.dumps(response_body).encode("utf-8")

    content_length = len(body_bytes)
    date_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    header_conn = "Connection: close"
    if http_version == "HTTP/1.1" and connection != "close":
        header_conn = "Connection: keep-alive"

    headers = [
        "HTTP/1.1 201 Created",
        "Content-Type: application/json; charset=utf-8",
        f"Content-Length: {content_length}",
        f"Date: {date_str}",
        "Server: Simple HTTP Server",
        header_conn,
    ]

    header_bytes = ("\r\n".join(headers) + "\r\n\r\n").encode("utf-8")
    return header_bytes + body_bytes

def handle_client(client_socket, addr):
    print(Fore.YELLOW + f"Connection from: {addr}\n")
    client_socket.settimeout(5.0)
    try:
        while server_running:
            try:
                data = client_socket.recv(8192)
                if not data:
                    print(Fore.GREEN + f"Client {addr} disconnected gracefully\n")
                    break
            except socket.timeout:
                continue
            except ConnectionResetError:
                print(Fore.BLUE + f"Client {addr} forcibly closed the connection\n")
                break

            # Find end of headers
            header_end = data.find(b"\r\n\r\n")
            if header_end == -1:
                # headers not fully received yet
                continue

            header_bytes = data[:header_end]
            body = data[header_end + 4 :]  # body may already contain data

            request_lines = header_bytes.decode("utf-8").splitlines()
            if not request_lines:
                continue

            request_line = request_lines[0]
            parts = request_line.split()
            if len(parts) < 3:
                response = error_res_html("400 Bad Request")
                client_socket.sendall(response)
                continue

            method, path, http_version = parts
            print(Fore.CYAN + f"{addr} Request: {method} {path} {http_version}\n")

            # Parse headers
            headers = {
                line.split(":", 1)[0].strip().lower(): line.split(":", 1)[1].strip()
                for line in request_lines[1:]
                if ":" in line
            }
            # print(headers)
            connection = headers.get("connection", "").lower()

            # Handle GET
            if method == "GET":
                file_type = path.split(".")[-1]
                if path == "/":
                    response = handle_get("index.html", http_version, connection)
                elif file_type in ["html", "txt", "png", "jpg", "jpeg"]:
                    response = handle_get(path.lstrip("/"), http_version, connection)
                else:
                    response = error_res_html("415 Unsupported Media Type")

            # Handle POST
            elif method == "POST":
                content_length = int(headers.get("content-length", 0))
                # Continue reading remaining body if needed
                # body = ""
                while len(body) < content_length:
                    body += client_socket.recv(8192)
                response = handle_post(path, headers, body, http_version, connection)

            else:
                response = error_res_html("405 Method Not Allowed")

            # Send response
            client_socket.sendall(response)

            # Close connection if requested
            if connection == "close":
                break

    except Exception as e:
        print(Fore.RED + f"Error handling client {addr}: {e}\n")
    finally:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        client_socket.close()
        print(Fore.YELLOW + f"Connection closed: {addr}\n")


def start_server(host, port, thread_pool_size):
    global server_running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(50)
    server_socket.settimeout(1.0)
    print(Fore.GREEN + f"Server is listening on {host}:{port}\n")

    with ThreadPoolExecutor(max_workers=thread_pool_size) as executor:
        try:
            while server_running:
                try:
                    client_socket, addr = server_socket.accept()
                    executor.submit(handle_client, client_socket, addr)
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print(Fore.GREEN + "\nShutting down server gracefully...\n")
            server_running = False
        finally:
            server_socket.close()
            print(Fore.BLUE + "Server socket closed.\n")


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8080
    thread_pool_size = 10

    try:
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
        if len(sys.argv) > 2:
            host = sys.argv[2]
        if len(sys.argv) > 3:
            thread_pool_size = int(sys.argv[3])
    except ValueError:
        print(Fore.RED + "Usage: python server.py [port] [host] [thread_pool_size]\n")
    start_server(host, port, thread_pool_size)
