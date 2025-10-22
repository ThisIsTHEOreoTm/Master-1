import socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 50050))
server_socket.listen(1)
print("Server is listening on port 50050...")

conn, addr = server_socket.accept()
print(f"Connection from {addr} has been established!")

#dialog loop:
while True:
    data = conn.recv(1024).decode()
    if data == 'exit' or data == '':
        print("Client has disconnected.")
        break
    print(f"Received from client: {data}")
    
    response = input("TALK :") 
    conn.send(response.encode())

#ferm la coonnexion
conn.close()
server_socket.close()
print("Server has been closed.")
