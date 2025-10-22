import socket

server_ip = input("Enter server IP address: ")
server_port = int(input("Enter server port number: "))

clinet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clinet_socket.connect((server_ip, server_port))
print("Connected to the server.")
#dialog loop:
while True:
    message = input("TALK :")
    clinet_socket.send(message.encode())
    if message == 'exit' or message == '':
        break
    data = clinet_socket.recv(1024).decode()
    print(f"Received from server: {data}")


clinet_socket.close()
print("Connexion fermée.")