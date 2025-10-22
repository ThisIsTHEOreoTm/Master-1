import socket

Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 5005)

message = "Bonjour, serveur!"
Socket.sendto(message.encode(), server_address)

data, server = Socket.recvfrom(1024)
print(f"Réponse du serveur: {data.decode()}")

Socket.close()
