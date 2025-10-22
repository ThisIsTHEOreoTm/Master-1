import socket
from tkinter import *
from tkinter import font as tkfont
import random
import threading

# =========================
#  Trying interface
# =========================

client_socket = None
is_connected = False



def connect_to_server():
    """Se connecte au serveur TCP"""
    global client_socket, is_connected
    
    try:
        ip = W_IP.get().strip()
        port = int(W_Port.get().strip())
        
        if not ip or port <= 0:
            Message.insert(END, "🥺 Oh non ! IP ou port invalide. Réessaie ? 😔\n", "error")
            return
        
        Message.insert(END, f"🔄 Connexion en cours vers {ip}:{port}... 💭\n", "warn")
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        is_connected = True
        
        Message.insert(END, f"🌈 Connexion établie avec {ip}:{port} ! Yay ! 🥳\n", "info")
        B_connect['state'] = DISABLED
        B_disconnect['state'] = NORMAL
        B_send['state'] = NORMAL
        B_connect.config(bg="#A0D9B1", text="💖 Connecté(e) !", fg="white")
        canvas.itemconfig(status_indicator, text="💖")
        
    except ValueError:
        Message.insert(END, "🥺 Oh non ! Le port doit être un nombre ! 😔\n", "error")
    except Exception as e:
        Message.insert(END, f"💔 Erreur de connexion: {e} 💔\n", "error")
        is_connected = False


def disconnect_from_server():
    """Se déconnecte du serveur"""
    global client_socket, is_connected
    
    try:
        if client_socket:
            client_socket.close()
        is_connected = False
        
        Message.insert(END, "👋 Déconnecté(e) ! À bientôt ! 🌟\n", "warn")
        B_connect['state'] = NORMAL
        B_disconnect['state'] = DISABLED
        B_send['state'] = DISABLED
        B_connect.config(bg="#ADD8E6", text="Connecte-moi ! 🚀", fg="white")
        canvas.itemconfig(status_indicator, text="💔")
        
    except Exception as e:
        Message.insert(END, f"💔 Erreur lors de la déconnexion: {e} 💔\n", "error")


def send_message(event=None):
    """Envoie le message au serveur"""
    global client_socket, is_connected
    
    if not is_connected:
        Message.insert(END, "⚠️ Hmm, il faut se connecter d'abord ! 🥺\n", "error")
        return

    msg = input_text.get().strip()
    if msg == "":
        Message.insert(END, "💭 Ton message est vide ! Envoie quelque chose ! 😉\n", "warn")
        return

    try:
        client_socket.send(msg.encode())
        Message.insert(END, f"👉 MOI: {msg}\n", "you")
        
        # Réception dans un thread pour ne pas bloquer l'interface
        def receive():
            try:
                data = client_socket.recv(1024)
                if data:
                    Message.insert(END, f"👈 SERVEUR: {data.decode()}\n", "server")
                    Message.see(END)
                else:
                    Message.insert(END, "💔 Le serveur a fermé la connexion 💔\n", "error")
                    disconnect_from_server()
            except Exception as e:
                Message.insert(END, f"💔 Erreur de réception: {e} 💔\n", "error")
        
        thread = threading.Thread(target=receive, daemon=True)
        thread.start()
        
    except Exception as e:
        Message.insert(END, f"💔 Erreur d'envoi: {e} 💔\n", "error")
        is_connected = False
        disconnect_from_server()

    input_text.delete(0, END)
    Message.see(END)



clouds = []
stars = []

def animate_cute_bg():
    global clouds, stars
    canvas.delete("cute_bg_elements")

    
    for i, cloud in enumerate(clouds):
        x, y, size = cloud
        x += 0.5
        if x > 600 + size*2:
            x = -size*2
            y = random.randint(0, 200)
        clouds[i] = (x, y, size)
        
       
        canvas.create_oval(x, y, x + size, y + size * 0.7, fill="#FFFFFF", outline="#F0F8FF", width=1, tags="cute_bg_elements")
        canvas.create_oval(x + size/2, y - size/4, x + size*1.5, y + size/2, fill="#FFFFFF", outline="#F0F8FF", width=1, tags="cute_bg_elements")
        canvas.create_oval(x + size, y + size/4, x + size*2, y + size*0.8, fill="#FFFFFF", outline="#F0F8FF", width=1, tags="cute_bg_elements")

    
    for i, star in enumerate(stars):
        x, y, size, color = star
        if random.random() < 0.1:
            color = "#FFD700" if random.random() < 0.5 else "#FFFFFF"
            size = random.randint(1, 3)
        stars[i] = (x, y, size, color)
        canvas.create_oval(x, y, x + size, y + size, fill=color, outline=color, tags="cute_bg_elements")

    canvas.tag_lower("cute_bg_elements")
    fenetre.after(100, animate_cute_bg)


def on_closing():
    """Fermeture propre de l'application"""
    disconnect_from_server()
    fenetre.destroy()



fenetre = Tk()
fenetre.geometry('600x550')
fenetre.title("💖 Mon Super Mignon Chat TCP ! 💖")
fenetre.configure(bg='#FFF0F5')
fenetre.protocol("WM_DELETE_WINDOW", on_closing)


try:
    title_font = tkfont.Font(family="Comic Sans MS", size=16, weight="bold")
    body_font = tkfont.Font(family="Comic Sans MS", size=11)
    small_font = tkfont.Font(family="Comic Sans MS", size=9)
except:
    title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
    body_font = tkfont.Font(family="Helvetica", size=11)
    small_font = tkfont.Font(family="Helvetica", size=9)


canvas = Canvas(fenetre, width=600, height=550, bg='#FFE4E1', highlightthickness=0)
canvas.place(x=0, y=0)


for i in range(550):
    r = int(255 - i * (255-245)/550)
    g = int(228 - i * (228-240)/550)
    b = int(225 - i * (240-255)/550)
    canvas.create_line(0, i, 600, i, fill=f'#{r:02x}{g:02x}{b:02x}', width=1)


for _ in range(5):
    clouds.append((random.randint(0, 600), random.randint(0, 150), random.randint(40, 80)))
for _ in range(20):
    stars.append((random.randint(0, 600), random.randint(0, 450), random.randint(1, 3), "#FFFFFF"))


canvas.create_oval(-20, -20, 70, 70, fill='#FFDAB9', outline='#FFB6C1', width=2)
canvas.create_oval(550, -20, 620, 70, fill='#FFDAB9', outline='#FFB6C1', width=2)
canvas.create_rectangle(0, 0, 600, 50, fill='#FFDAB9', outline='#FFB6C1', width=2)
canvas.create_text(300, 25, text="💖 Mon Royaume de Chat TCP ! 💖", 
                   font=title_font, fill='#E57373')


status_indicator = canvas.create_text(555, 27, text="💔", font=("Segoe UI Emoji", 18), fill='#E57373')


canvas.create_oval(10, 60, 40, 90, fill='#ADD8E6', outline='#87CEEB', width=2)
canvas.create_oval(560, 60, 590, 90, fill='#ADD8E6', outline='#87CEEB', width=2)
canvas.create_rectangle(20, 70, 580, 160, fill='#ADD8E6', outline='#87CEEB', width=2)


canvas.create_text(40, 85, text="✨ Adresse IP :", font=body_font, fill='#4682B4', anchor='w')
W_IP = Entry(fenetre, bg='#F0F8FF', fg='#4682B4', font=body_font, 
             insertbackground='#4682B4', relief=FLAT, borderwidth=0)
canvas.create_rectangle(180, 75, 350, 105, fill='#F0F8FF', outline='#87CEEB', width=1)
W_IP.place(x=185, y=80, width=160, height=20)
W_IP.insert(0, "localhost")


canvas.create_text(40, 120, text="✨ Port magique :", font=body_font, fill='#4682B4', anchor='w')
W_Port = Entry(fenetre, bg='#F0F8FF', fg='#4682B4', font=body_font, 
               insertbackground='#4682B4', relief=FLAT, borderwidth=0)
canvas.create_rectangle(180, 110, 280, 140, fill='#F0F8FF', outline='#87CEEB', width=1)
W_Port.place(x=185, y=115, width=90, height=20)
W_Port.insert(0, "5005")


B_connect = Button(fenetre, text="Connecte-moi ! 🚀", command=connect_to_server,
                   bg='#ADD8E6', fg='white', font=small_font, relief=FLAT,
                   activebackground='#87CEEB', activeforeground='white',
                   borderwidth=0, cursor='hand2')
canvas.create_rectangle(380, 75, 560, 105, fill='#ADD8E6', outline='#87CEEB', width=2)
B_connect.place(x=385, y=80, width=170, height=20)

B_disconnect = Button(fenetre, text="Se déconnecter 👋", command=disconnect_from_server,
                      bg='#FFB6C1', fg='white', font=small_font, relief=FLAT,
                      activebackground='#FF69B4', activeforeground='white',
                      borderwidth=0, cursor='hand2', state=DISABLED)
canvas.create_rectangle(380, 110, 560, 140, fill='#FFB6C1', outline='#87CEEB', width=2)
B_disconnect.place(x=385, y=115, width=170, height=20)

# Cadre des messages
canvas.create_rectangle(20, 180, 580, 430, fill='#FFFFFF', outline='#FFB6C1', width=2)
canvas.create_text(30, 170, text="💌 Nos doux messages 💌", 
                   font=small_font, fill='#E57373', anchor='w')


Message = Text(fenetre, width=65, height=15, font=body_font,
               bg='#FFFFFF', fg='#696969', insertbackground='#FFB6C1',
               relief=FLAT, borderwidth=0, padx=10, pady=10)
Message.place(x=25, y=185, width=550, height=240)

scrollbar = Scrollbar(fenetre, command=Message.yview, bg='#F0F8FF', 
                      troughcolor='#FFFFFF', activebackground='#FFDAB9',
                      relief=FLAT, borderwidth=0)
Message.config(yscrollcommand=scrollbar.set)
scrollbar.place(x=575, y=185, height=240)


Message.tag_config("info", foreground="#8A2BE2", font=(body_font, 11, "bold"))
Message.tag_config("error", foreground="#FF69B4", font=(body_font, 11, "bold"))
Message.tag_config("warn", foreground="#FFD700", font=(body_font, 11, "bold"))
Message.tag_config("you", foreground="#6A5ACD")
Message.tag_config("server", foreground="#FF6347")


canvas.create_rectangle(20, 450, 580, 520, fill='#ADD8E6', outline='#87CEEB', width=2)
canvas.create_text(30, 440, text="✨ Dis quelque chose... ✨", 
                   font=small_font, fill='#4682B4', anchor='w')


input_text = Entry(fenetre, bg='#F0F8FF', fg='#4682B4', font=body_font,
                   insertbackground='#4682B4', relief=FLAT, borderwidth=0)
canvas.create_rectangle(30, 470, 430, 505, fill='#F0F8FF', outline='#87CEEB', width=1)
input_text.place(x=35, y=475, width=390, height=25)
input_text.bind('<Return>', send_message)


B_send = Button(fenetre, text="Envoi ! 💌", command=send_message,
                bg='#ADD8E6', fg='white', font=small_font, relief=FLAT,
                activebackground='#87CEEB', activeforeground='white',
                borderwidth=0, cursor='hand2', state=DISABLED)
canvas.create_rectangle(450, 470, 570, 505, fill='#ADD8E6', outline='#87CEEB', width=2)
B_send.place(x=455, y=475, width=110, height=25)


Message.insert(END, "💖 ~~~~~~~ Bienvenue dans le monde TCP des petits mots ! ~~~~~~~ 💖\n", "info")
Message.insert(END, "        (On est si content de te voir !) 🥰\n", "info")
Message.insert(END, "💖 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 💖\n", "info")
Message.insert(END, "\n👉 Entre l'IP et le port, puis clique 'Connecte-moi !' ✨\n\n", "warn")


animate_cute_bg()

fenetre.mainloop()



# ip = input("Entrez l’adresse IP du serveur (ex: localhost): ")
# port = int(input("Entrez le port du serveur: "))
# message = input("Entrez le message à envoyer: ")

# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_socket.connect((ip, port))
# print(f"Connexion établie avec le serveur {ip}:{port}")

# client_socket.send(message.encode())
# data = client_socket.recv(1024)
# print("Réponse du serveur:", data.decode())

# client_socket.close()



#netstat -an | find "5005"