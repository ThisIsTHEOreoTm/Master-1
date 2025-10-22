import socket


client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

server_ip = input("Enter IPv6 address of the server (ex: ::1): ")
server_port = int(input("Enter server port number: "))

client_socket.connect((server_ip, server_port))
print("Connected to the server (IPv6).")

while True:
    message = input("TALK: ")
    client_socket.send(message.encode('utf-8'))

    if message.lower() == 'exit' or message == '':
        print("Ending conversation...")
        break

    data = client_socket.recv(1024).decode('utf-8')
    print(f"Server: {data}")

client_socket.close()
print("Connection closed.")
