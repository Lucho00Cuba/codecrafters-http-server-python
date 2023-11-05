# Uncomment this to pass the first stage
import socket
import threading
import argparse
import sys
from pathlib import Path

PORT = 4221
BUFFER = 1024
CRLF = "\r\n"

def getPath(data):
    decoded_data = data.decode()
    first_line = decoded_data.split("\r\n")[0]
    path = first_line.split(" ")[1]
    return path

def getHeaderUserAgent(data):
    decoded_data = data.decode()
    first_line = decoded_data.split("\r\n")
    for header in first_line:
        if header.startswith("User-Agent:"):
            return header.split(" ")[1]

def make_response(line):
    return line.encode()

def getBody(data: str):
    decoded_data = data[data.find(b"\r\n\r\n") + 4 :]
    return decoded_data.decode()

def getFileContent(directory_path, file_path):
    whole_path = Path(directory_path).joinpath(Path(file_path))
    if whole_path.exists():
        print("exists")
        with open(whole_path, "r") as file:
            file_contents = file.read()
        return True, file_contents
    return False, ""

def writeToFile(directory_path, file_path: str, content):
    whole_path = Path(directory_path).joinpath(Path(file_path))
    if Path(directory_path).exists() and bool(file_path.strip()):
        with open(whole_path, "w") as file:
            file.write(content)
            file.close()
        return True
    return False

def handle_POST_request(data: str, sock: socket.socket, directory_path: str):
    path = getPath(data)
    if path.startswith("/files/"):
        body = getBody(data)
        file_path = path.split("/files/")[1]
        success = writeToFile(directory_path, file_path, body)
        if success:
            sock.send(b"HTTP/1.1 201 Created\r\n\r\n")
        else:
            sock.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
    else:
        sock.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
    sock.close()

def handle_GET_request(data, client_socket, directory_path):
    path = getPath(data)
    if path == '/':
        client_socket.send(make_response(f"HTTP/1.1 200 OK {CRLF + CRLF}"))
    elif path.startswith('/echo/'):
        message = path.split("/echo/")[1]
        client_socket.send(make_response(f"HTTP/1.1 200 OK {CRLF}"))
        client_socket.send(make_response(f"Content-Type: text/plain{CRLF}"))
        client_socket.send(make_response(f"Content-Length: {len(message)} {CRLF}"))
        client_socket.send(make_response(f"{CRLF}"))
        client_socket.send(make_response(f"{message} {CRLF + CRLF}"))
    elif path == '/user-agent':
        message = getHeaderUserAgent(data)
        client_socket.send(make_response(f"HTTP/1.1 200 OK {CRLF}"))
        client_socket.send(make_response(f"Content-Type: text/plain{CRLF}"))
        client_socket.send(make_response(f"Content-Length: {len(message)} {CRLF}"))
        client_socket.send(make_response(f"{CRLF}"))
        client_socket.send(make_response(f"{message} {CRLF + CRLF}"))
    elif path.startswith('/files/'):
        file_path = path.split("/files/")[1]
        file_exists, content = getFileContent(directory_path, file_path)
        if file_exists:
            client_socket.send(make_response(f"HTTP/1.1 200 OK {CRLF}"))
            client_socket.send(make_response(f"Content-Type: application/octet-stream {CRLF}"))
            client_socket.send(make_response(f"Content-Length: {len(content)} {CRLF}"))
            client_socket.send(make_response(f"{CRLF}"))
            client_socket.send(make_response(f"{content} {CRLF + CRLF}"))
        else:
            client_socket.send(make_response(f"HTTP/1.1 404 Not Found {CRLF + CRLF}"))
    else:
        client_socket.send(make_response(f"HTTP/1.1 404 Not Found {CRLF + CRLF}"))
    print(f"requests {path}")
    client_socket.close()

def handle_request(client_socket, client_addr, directory_path):
    print(f"Connected to {client_addr}")
    data = client_socket.recv(1024)
    if "GET" in data.decode():
        handle_GET_request(data, client_socket, directory_path)
    if "POST" in data.decode():
        handle_POST_request(data, client_socket, directory_path)

def main():

    # cli
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", help="the directory path")
    args = parser.parse_args()
    directory_path = args.directory or None

    # server
    print("Starting the server...")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Listen...")
    #socket.create_connection(("localhost", PORT), timeout=5)
    while True:
        sock, addr = server_socket.accept()  # wait for client
        threading.Thread(target=handle_request, args=(sock,addr,directory_path,)).start()

if __name__ == "__main__":
    main()
