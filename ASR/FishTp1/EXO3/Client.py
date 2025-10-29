import socket
import threading
from tkinter import *
from tkinter import font as tkfont
from datetime import datetime

# =========================
#  CHAT CLIENT
# =========================

client_socket = None
is_connected = False
message_count = 0

def connect_to_server():
    """Se connecte au serveur"""
    global client_socket, is_connected, message_count
    
    try:
        ip = entry_ip.get().strip()
        port = int(entry_port.get().strip())
        
        add_message("SYSTÈME", f"🔗 Connexion à {ip}...", "waiting")
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        is_connected = True
        message_count = 0
        
        add_message("SYSTÈME", "🎉 Connecté au serveur!", "connect")
        pulse_status("connected")
        server_label.config(text=f"🌐 {ip}:{port}", fg="#90ee90")
        
        btn_connect.config(bg="#baffc9", text="✓ Connecté!")
        btn_connect['state'] = DISABLED
        btn_disconnect['state'] = NORMAL
        entry_ip['state'] = DISABLED
        entry_port['state'] = DISABLED
        entry_message['state'] = NORMAL
        btn_send['state'] = NORMAL
        
        thread = threading.Thread(target=receive_messages, daemon=True)
        thread.start()
        
    except ValueError:
        add_message("ERREUR", "😅 Port invalide", "error")
    except Exception as e:
        add_message("ERREUR", f"😓 Connexion échouée: {e}", "error")


def receive_messages():
    """Reçoit les messages du serveur"""
    global client_socket, is_connected, message_count
    while is_connected and client_socket:
        try:
            data = client_socket.recv(1024).decode()
            if data == '' or not data:
                add_message("SYSTÈME", "😢 Serveur déconnecté", "disconnect")
                pulse_status("offline")
                server_label.config(text="🌐 Déconnecté", fg="#95a5a6")
                disconnect_from_server()
                break
            message_count += 1
            add_bubble_message("Serveur", data, "left")
            stats_label.config(text=f"💬 {message_count}")
        except:
            if is_connected:
                add_message("SYSTÈME", "😢 Connexion perdue", "disconnect")
                pulse_status("offline")
                server_label.config(text="🌐 Déconnecté", fg="#95a5a6")
                disconnect_from_server()
            break


def send_message(event=None):
    """Envoie un message au serveur"""
    global client_socket, is_connected, message_count
    
    msg = entry_message.get().strip()
    
    if not msg:
        return
    
    if not is_connected:
        add_message("ERREUR", "😅 Pas connecté!", "error")
        return
    
    try:
        client_socket.send(msg.encode())
        message_count += 1
        add_bubble_message("Vous", msg, "right")
        stats_label.config(text=f"💬 {message_count}")
        entry_message.delete(0, END)
        
        if msg == 'exit':
            disconnect_from_server()
            
    except Exception as e:
        add_message("ERREUR", f"😓 {e}", "error")
        disconnect_from_server()


def add_bubble_message(sender, text, side):
    """Ajoute un message en bulle kawaii"""
    timestamp = datetime.now().strftime("%H:%M")
    
    bubble_frame = Frame(chat_canvas_frame, bg="#fff5f7")
    
    if side == "right":
        bubble_frame.pack(fill=X, padx=15, pady=6, anchor=E)
        
        time_label = Label(bubble_frame, text=timestamp, font=("Comic Sans MS", 8), 
                          bg="#fff5f7", fg="#b8b8b8")
        time_label.pack(side=RIGHT, padx=5)
        
        msg_frame = Frame(bubble_frame, bg="#d4e4ff", bd=0)
        msg_frame.pack(side=RIGHT)
        
        Label(msg_frame, text="💙", font=("Segoe UI Emoji", 12), 
              bg="#d4e4ff").grid(row=0, column=0, padx=(10, 5), pady=5)
        Label(msg_frame, text=text, font=("Comic Sans MS", 10), bg="#d4e4ff", 
              fg="#5a5a5a", wraplength=350, justify=LEFT).grid(row=0, column=1, padx=(0, 10), pady=8)
    else:
        bubble_frame.pack(fill=X, padx=15, pady=6, anchor=W)
        
        msg_frame = Frame(bubble_frame, bg="#ffe4cc", bd=0)
        msg_frame.pack(side=LEFT)
        
        Label(msg_frame, text="🌟", font=("Segoe UI Emoji", 12), 
              bg="#ffe4cc").grid(row=0, column=0, padx=(10, 5), pady=5)
        Label(msg_frame, text=text, font=("Comic Sans MS", 10), bg="#ffe4cc", 
              fg="#5a5a5a", wraplength=350, justify=LEFT).grid(row=0, column=1, padx=(0, 10), pady=8)
        
        time_label = Label(bubble_frame, text=timestamp, font=("Comic Sans MS", 8), 
                          bg="#fff5f7", fg="#b8b8b8")
        time_label.pack(side=LEFT, padx=5)
    
    chat_canvas.update_idletasks()
    chat_canvas.config(scrollregion=chat_canvas.bbox("all"))
    chat_canvas.yview_moveto(1.0)


def add_message(sender, text, msg_type):
    """Ajoute un message système kawaii"""
    bubble_frame = Frame(chat_canvas_frame, bg="#fff5f7")
    bubble_frame.pack(fill=X, padx=15, pady=4)
    
    emojis = {
        "system": "✨",
        "error": "😓",
        "waiting": "🔗",
        "connect": "🎉",
        "disconnect": "👋"
    }
    
    colors = {
        "system": "#dda0dd",
        "error": "#ffb3ba",
        "waiting": "#ffd9b3",
        "connect": "#baffc9",
        "disconnect": "#ffdfba"
    }
    
    msg_frame = Frame(bubble_frame, bg=colors.get(msg_type, "#e0e0e0"), bd=0)
    msg_frame.pack()
    
    emoji = emojis.get(msg_type, "ℹ️")
    Label(msg_frame, text=f"{emoji} {text}", font=("Comic Sans MS", 9, "bold"),
          bg=colors.get(msg_type, "#e0e0e0"), fg="#5a5a5a",
          padx=12, pady=6).pack()
    
    chat_canvas.update_idletasks()
    chat_canvas.config(scrollregion=chat_canvas.bbox("all"))
    chat_canvas.yview_moveto(1.0)


def pulse_status(status):
    """Change l'indicateur de statut"""
    if status == "connected":
        status_label.config(text="● Connecté !", fg="#90ee90")
    else:
        status_label.config(text="● Hors ligne", fg="#ffb3ba")


def disconnect_from_server():
    """Se déconnecte du serveur"""
    global client_socket, is_connected
    is_connected = False
    
    if client_socket:
        try:
            client_socket.close()
        except:
            pass
        client_socket = None
    
    add_message("SYSTÈME", "👋 Déconnecté", "disconnect")
    pulse_status("offline")
    server_label.config(text="🌐 Déconnecté", fg="#95a5a6")
    
    btn_connect.config(bg="#dda0dd", text="🔗 Connecter")
    btn_connect['state'] = NORMAL
    btn_disconnect['state'] = DISABLED
    entry_ip['state'] = NORMAL
    entry_port['state'] = NORMAL
    entry_message['state'] = DISABLED
    btn_send['state'] = DISABLED


def on_closing():
    """Fermeture propre"""
    disconnect_from_server()
    root.destroy()


# GUI 
root = Tk()
root.title("💙 Client Chat ")
root.geometry("750x650")
root.configure(bg="#f0f8ff")
root.protocol("WM_DELETE_WINDOW", on_closing)

try:
    title_font = tkfont.Font(family="Comic Sans MS", size=20, weight="bold")
    header_font = tkfont.Font(family="Comic Sans MS", size=11, weight="bold")
    body_font = tkfont.Font(family="Comic Sans MS", size=10)
except:
    title_font = tkfont.Font(family="Arial", size=20, weight="bold")
    header_font = tkfont.Font(family="Arial", size=11, weight="bold")
    body_font = tkfont.Font(family="Arial", size=10)


main_frame = Frame(root, bg="#d4e4ff", bd=3, relief=RIDGE)
main_frame.place(x=15, y=15, width=720, height=620)


header = Frame(main_frame, bg="#b3d9ff", height=100)
header.pack(fill=X, padx=3, pady=3)
header.pack_propagate(False)

Label(header, text="💙 CLIENT DASH 💙", font=title_font,
      bg="#b3d9ff", fg="#4a90e2").pack(pady=(12, 5))


status_frame = Frame(header, bg="#b3d9ff")
status_frame.pack(pady=3)

status_label = Label(status_frame, text="● Hors ligne", font=header_font,
                     bg="#b3d9ff", fg="#ffb3ba")
status_label.pack(side=LEFT, padx=10)

server_label = Label(status_frame, text="🌐 Déconnecté", font=body_font,
                     bg="#b3d9ff", fg="#95a5a6")
server_label.pack(side=LEFT, padx=10)

stats_label = Label(status_frame, text="💬 0", font=body_font,
                    bg="#b3d9ff", fg="#95a5a6")
stats_label.pack(side=LEFT, padx=10)


conn_panel = Frame(main_frame, bg="#e6f2ff", height=70)
conn_panel.pack(fill=X, padx=3, pady=8)
conn_panel.pack_propagate(False)

Label(conn_panel, text="🌐 IP:", font=header_font,
      bg="#e6f2ff", fg="#4a90e2").place(x=20, y=20)

entry_ip = Entry(conn_panel, font=body_font, bg="white", fg="#5a5a5a",
                 insertbackground="#4a90e2", relief=SOLID, borderwidth=2, width=14)
entry_ip.insert(0, "localhost")
entry_ip.place(x=80, y=18, height=30)

Label(conn_panel, text="🔌 Port:", font=header_font,
      bg="#e6f2ff", fg="#4a90e2").place(x=230, y=20)

entry_port = Entry(conn_panel, font=body_font, bg="white", fg="#5a5a5a",
                   insertbackground="#4a90e2", relief=SOLID, borderwidth=2, width=8)
entry_port.insert(0, "50050")
entry_port.place(x=300, y=18, height=30)

btn_connect = Button(conn_panel, text="🔗 Connecter", command=connect_to_server,
                     bg="#dda0dd", fg="white", font=header_font, relief=FLAT,
                     cursor="hand2", borderwidth=0)
btn_connect.place(x=410, y=18, width=130, height=30)

btn_disconnect = Button(conn_panel, text="✕ Déconnecter", command=disconnect_from_server,
                        bg="#ffb3ba", fg="white", font=header_font, relief=FLAT,
                        cursor="hand2", state=DISABLED, borderwidth=0)
btn_disconnect.place(x=560, y=18, width=130, height=30)


chat_container = Frame(main_frame, bg="#e6f2ff")
chat_container.pack(fill=BOTH, expand=True, padx=3, pady=5)

Label(chat_container, text="💬 Conversation", font=header_font,
      bg="#e6f2ff", fg="#4a90e2").pack(anchor=W, padx=12, pady=(8, 4))


chat_canvas = Canvas(chat_container, bg="#fff5f7", highlightthickness=0)
chat_scrollbar = Scrollbar(chat_container, orient="vertical", command=chat_canvas.yview,
                           bg="#b3d9ff", troughcolor="#fff5f7", 
                           activebackground="#4a90e2", width=14)
chat_canvas_frame = Frame(chat_canvas, bg="#fff5f7")

chat_canvas_frame.bind("<Configure>", 
                       lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all")))

chat_canvas.create_window((0, 0), window=chat_canvas_frame, anchor="nw")
chat_canvas.configure(yscrollcommand=chat_scrollbar.set)

chat_canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=12, pady=8)
chat_scrollbar.pack(side=RIGHT, fill=Y, pady=8, padx=(0, 12))


input_area = Frame(main_frame, bg="#e6f2ff", height=70)
input_area.pack(fill=X, padx=3, pady=3)
input_area.pack_propagate(False)

entry_message = Entry(input_area, font=body_font, bg="white", fg="#5a5a5a",
                      insertbackground="#4a90e2", relief=SOLID, borderwidth=2,
                      state=DISABLED)
entry_message.place(x=15, y=18, width=520, height=35)
entry_message.bind('<Return>', send_message)

btn_send = Button(input_area, text="Envoyer 💙", command=send_message,
                  bg="#d4e4ff", fg="#4a90e2", font=header_font,
                  relief=FLAT, cursor="hand2", state=DISABLED, borderwidth=0)
btn_send.place(x=550, y=18, width=150, height=35)


add_message("SYSTÈME", "Bienvenue! Connectez-vous 🌟", "system")

root.mainloop()


# import socket

# server_ip = input("Enter server IP address: ")
# server_port = int(input("Enter server port number: "))

# clinet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# clinet_socket.connect((server_ip, server_port))
# print("Connected to the server.")
# #dialog loop:
# while True:
#     message = input("TALK :")
#     clinet_socket.send(message.encode())
#     if message == 'exit' or message == '':
#         break
#     data = clinet_socket.recv(1024).decode()
#     print(f"Received from server: {data}")


# clinet_socket.close()
# print("Connexion fermée.")