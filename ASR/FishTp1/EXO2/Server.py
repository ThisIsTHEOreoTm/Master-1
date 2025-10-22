import socket


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_address = ('localhost', 5005)
server_socket.bind(server_address)


server_socket.listen(1)
print("Serveur TCP en attente de connexions sur le port 5005...")


connection, client_address = server_socket.accept()
print(f"Connexion établie avec : {client_address}")


data = connection.recv(1024)
print(f"Message reçu du client : {data.decode()}")
response = "Message bien reçu!"
connection.sendall(response.encode())

connection.close()
print("Connexion terminée.\nEn attente d'un autre client...")
