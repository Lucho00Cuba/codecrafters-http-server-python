# Uncomment this to pass the first stage
import socket
import threading
import argparse
import sys
from pathlib import Path

PORT = 4221
BUFFER = 1024
CRLF = "\r\n"

def requests_path(data):
    decoded_data = data.decode()
    first_line = decoded_data.split("\r\n")[0]
    path = first_line.split(" ")[1]
    return path

def requests_userAgent(data):
    decoded_data = data.decode()
    first_line = decoded_data.split("\r\n")
    for header in first_line:
        if header.startswith("User-Agent:"):
            return header.split(" ")[1]

def make_response(line):
    return line.encode()

def getFileContent(directory_path, file_path):
    whole_path = Path(directory_path).joinpath(Path(file_path))
    if whole_path.exists():
        print("exists")
        with open(whole_path, "r") as file:
            file_contents = file.read()
        return True, file_contents
    return False, ""

def handler_req(client_socket,client_addr, directory_path):
    try:
        with client_socket:
            print(f"Connected to {client_addr}")
            data = client_socket.recv(BUFFER)
            path = requests_path(data)
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
                message = requests_userAgent(data)
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
    except ConnectionError:
        pass # nc probe

    client_socket.close()

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
        threading.Thread(target=handler_req, args=(sock,addr,directory_path,)).start()

if __name__ == "__main__":
    main()
