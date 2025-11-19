import socket
import sys
import threading

LOCALHOST = "127.0.0.1"
BUFFER = 4096

def receive(sock):
    """Boucle infinie de réception."""
    while True:
        data, addr = sock.recvfrom(BUFFER)
        msg = data.decode()
        print("\n----- MESSAGE REÇU -----")
        print(f"Depuis : {addr}")
        print(f"Contenu : {msg}")
        print("------------------------\n")


def send(sock):
    """Laisser la main à l'utilisateur pour envoyer des messages."""
    while True:
        dest_port = input("→ Entrez le port de destination : ").strip()
        msg = input("→ Entrez le message à envoyer : ").strip()
        
        if not dest_port.isdigit():
            print("Port invalide.")
            continue
        
        sock.sendto(msg.encode(), (LOCALHOST, int(dest_port)))
        print(f"[SEND] Message envoyé à {dest_port} !\n")


def main():
    # Vérification des arguments
    if len(sys.argv) != 2:
        print("Usage : python node.py port_local")
        return
    
    local_port = int(sys.argv[1])

    # Création socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCALHOST, local_port))

    print(f"--- NŒUD DÉMARRÉ ---")
    print(f"Port local : {local_port}")
    print(f"En attente de messages...\n")

    # Thread réception
    t = threading.Thread(target=receive, args=(sock,), daemon=True)
    t.start()

    # Fonction envoi
    send(sock)


if __name__ == "__main__":
    main()
