# Uncomment this to pass the first stage
import socket
import threading

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

def handler_req(client_socket,client_addr):
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
            else:
                client_socket.send(make_response(f"HTTP/1.1 404 Not Found {CRLF + CRLF}"))
            print(f"requests {path}")
    except ConnectionError:
        pass # nc probe

    client_socket.close()

def main():
    print("Starting the server...")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Listen...")
    #socket.create_connection(("localhost", PORT), timeout=5)
    while True:
        sock, addr = server_socket.accept()  # wait for client
        threading.Thread(target=handler_req, args=(sock,addr,)).start()

if __name__ == "__main__":
    main()
