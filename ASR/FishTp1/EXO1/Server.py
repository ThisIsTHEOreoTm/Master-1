import socket


Sock_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


Sock_server.bind(('localhost', 5005))
print("Le serveur est en attente de messages...")


data, addr = Sock_server.recvfrom(1024)
print(f"Message reçu de {addr} : {data.decode()}")


response = "Message bien reçu!"
Sock_server.sendto(response.encode(), addr)

Sock_server.close()
