import socket

server_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
server_socket.bind(('::1', 5005))
server_socket.listen(1)

print("Server is listening on port 50050...")

conn , addr = server_socket.accept()
print(f"Connection from {addr}")

while True:
    data = conn.recv(1024).decode()
    if data.lower() == 'exit' or data == '':
        print("Exiting server.")
        break
    print(f"Received from client: {data}")
    reponse = input("Enter response to client: ")
    conn.sendall(reponse.encode())

conn.close()
server_socket.close()
print("Server closed.")


#CMD      netstat -an | find "5005"
#GIT BASH netstat -an | grep 5005
