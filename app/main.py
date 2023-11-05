# Uncomment this to pass the first stage
import socket

PORT = 4221
BUFFER = 1024
CRLF = "\r\n"

def requests_path(data):
    decoded_data = data.decode()
    first_line = decoded_data.split("\r\n")[0]
    path = first_line.split(" ")[1]
    return path

def make_response(line):
    return f"{line}".encode()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage

    print("Starting the server...")
    server_socket = socket.create_server(("localhost", PORT), reuse_port=True)
    # test for enable port
    socket.create_connection(("localhost", PORT), timeout=5)
    print("Listen...")
    server_socket.accept() # wait for client

    client_socket, client_addr = server_socket.accept()

    with client_socket:
        print(f"Connected to {client_addr}")
        data = b""
        chunk = client_socket.recv(BUFFER)
        data += chunk
        path = requests_path(data)
        if path == '/':
            client_socket.send(make_response(f"HTTP/1.1 200 OK {CRLF}"))
        elif path.startswith('/echo/'):
            message = path.split("/echo/")[1]
            client_socket.send(make_response(f"HTTP/1.1 200 OK {CRLF}"))
            client_socket.send(make_response(f"Content-Type: text/plain{CRLF}"))
            client_socket.send(make_response(f"Content-Length: {len(message)} {CRLF}"))
            client_socket.send(make_response(f"{CRLF}"))
            client_socket.send(make_response(f"{message}"))
        else:
            client_socket.send(make_response(f"HTTP/1.1 404 Not Found {CRLF}"))


if __name__ == "__main__":
    main()
