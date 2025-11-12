# ===========================
# CLIENT UDP / TCP avec GUI
# ===========================

import sys
import socket
import os
from tkinter import *
from tkinter import messagebox


# ===========================
# EXERCICE 2 + 3 : Console
# ===========================
def console_mode():
    if len(sys.argv) != 3:
        print("Usage: python script.py <message> <port>")
        sys.exit(1)

    message = sys.argv[1]

    try:
        port_distant = int(sys.argv[2])
    except ValueError:
        print("Erreur : le port doit être un entier")
        sys.exit(1)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        s.sendto(message.encode(), ('localhost', port_distant))
        print("Message envoyé avec succès !")
    except Exception as e:
        print("Erreur lors de l'envoi :", e)
        sys.exit(1)

    # Effacer l’écran
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

#: récupère le message et le port depuis la ligne de commande. 
# python script.py "Bonjour" 60000


