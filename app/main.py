# Uncomment this to pass the first stage
import socket

PORT = 4221
BUFFER = 1024
CRLF = "\r\n"
HEADERS_END = CRLF + CRLF
HTTP_200 = "HTTP/1.1 200 OK" + HEADERS_END

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
        response = HTTP_200.encode()
        client_socket.send(response)


if __name__ == "__main__":
    main()
