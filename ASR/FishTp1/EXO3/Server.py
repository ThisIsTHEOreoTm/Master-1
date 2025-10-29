import socket
import threading
from tkinter import *
from tkinter import font as tkfont
from datetime import datetime

# =========================
#   CHAT SERVER
# =========================

server_socket = None
conn = None
addr = None
is_running = False
message_count = 0


themes = {
    "green": {
        "bg": "#f0fff4",
        "main": "#d4f4dd",
        "header": "#a8e6cf",
        "accent": "#2d8659",
        "control": "#e8f8f0",
        "bubble_you": "#c8e6c9",
        "emoji": "💚",
        "button": "#81c784"
    },
    "pink": {
        "bg": "#fff5f7",
        "main": "#ffe4e9",
        "header": "#ffccdd",
        "accent": "#ff6b9d",
        "control": "#fff0f5",
        "bubble_you": "#ffd3e1",
        "emoji": "💕",
        "button": "#dda0dd"
    },
    "blue": {
        "bg": "#f0f8ff",
        "main": "#d4e4ff",
        "header": "#b3d9ff",
        "accent": "#4a90e2",
        "control": "#e6f2ff",
        "bubble_you": "#d4e4ff",
        "emoji": "💙",
        "button": "#64b5f6"
    },
    "purple": {
        "bg": "#f5f0ff",
        "main": "#e8dcff",
        "header": "#d4c5f9",
        "accent": "#7c4dff",
        "control": "#f0e6ff",
        "bubble_you": "#d1c4e9",
        "emoji": "💜",
        "button": "#9575cd"
    }
}

current_theme = "green"

def start_server():
    """Démarre le serveur"""
    global server_socket, is_running
    
    try:
        port = int(entry_port.get())
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', port))
        server_socket.listen(1)
        is_running = True
        
        add_message("SYSTÈME", f"✨ Serveur démarré sur le port {port} !", "system")
        pulse_status("online")
        btn_start.config(bg="#a8e6cf", text="✓ En ligne!")
        btn_start['state'] = DISABLED
        btn_stop['state'] = NORMAL
        entry_port['state'] = DISABLED
        
        thread = threading.Thread(target=wait_for_connection, daemon=True)
        thread.start()
        
    except Exception as e:
        add_message("ERREUR", f"😓 {e}", "error")


def wait_for_connection():
    """Attend une connexion client"""
    global conn, addr, message_count
    try:
        add_message("SYSTÈME", "🔍 En attente d'un client...", "waiting")
        conn, addr = server_socket.accept()
        message_count = 0
        add_message("SYSTÈME", f"🎉 Client connecté! {addr[0]}", "connect")
        pulse_status("connected")
        connection_label.config(text=f"👤 {addr[0]}", fg=themes[current_theme]["accent"])
        btn_send['state'] = NORMAL
        entry_message['state'] = NORMAL
        
        thread = threading.Thread(target=receive_messages, daemon=True)
        thread.start()
        
    except Exception as e:
        if is_running:
            add_message("ERREUR", f"😓 {e}", "error")


def receive_messages():
    """Reçoit les messages du client"""
    global conn, is_running, message_count
    while is_running and conn:
        try:
            data = conn.recv(1024).decode()
            if data == 'exit' or data == '':
                add_message("SYSTÈME", "👋 Client parti", "disconnect")
                pulse_status("online")
                connection_label.config(text="👤 Personne", fg="#95a5a6")
                disconnect_client()
                break
            message_count += 1
            add_bubble_message("Client", data, "left")
            stats_label.config(text=f"💬 {message_count}")
        except:
            if is_running:
                add_message("SYSTÈME", "😢 Connexion perdue", "disconnect")
                pulse_status("online")
                connection_label.config(text="👤 Personne", fg="#95a5a6")
                disconnect_client()
            break


def send_message(event=None):
    """Envoie un message au client"""
    global conn, message_count
    msg = entry_message.get().strip()
    
    if not msg:
        return
    
    if not conn:
        add_message("ERREUR", "😅 Personne à qui parler!", "error")
        return
    
    try:
        conn.send(msg.encode())
        message_count += 1
        add_bubble_message("Vous", msg, "right")
        stats_label.config(text=f"💬 {message_count}")
        entry_message.delete(0, END)
    except Exception as e:
        add_message("ERREUR", f"😓 {e}", "error")
        disconnect_client()


def add_bubble_message(sender, text, side):
    """Ajoute un message en bulle kawaii"""
    timestamp = datetime.now().strftime("%H:%M")
    theme = themes[current_theme]
    
    bubble_frame = Frame(chat_canvas_frame, bg=theme["bg"])
    
    if side == "right":
        bubble_frame.pack(fill=X, padx=15, pady=6, anchor=E)
        
        time_label = Label(bubble_frame, text=timestamp, font=("Comic Sans MS", 8), 
                          bg=theme["bg"], fg="#b8b8b8")
        time_label.pack(side=RIGHT, padx=5)
        
        msg_frame = Frame(bubble_frame, bg=theme["bubble_you"], bd=0)
        msg_frame.pack(side=RIGHT)
        
        Label(msg_frame, text=theme["emoji"], font=("Segoe UI Emoji", 12), 
              bg=theme["bubble_you"]).grid(row=0, column=0, padx=(10, 5), pady=5)
        Label(msg_frame, text=text, font=("Comic Sans MS", 10), bg=theme["bubble_you"], 
              fg="#5a5a5a", wraplength=350, justify=LEFT).grid(row=0, column=1, padx=(0, 10), pady=8)
    else:
        bubble_frame.pack(fill=X, padx=15, pady=6, anchor=W)
        
        msg_frame = Frame(bubble_frame, bg="#c7ecee", bd=0)
        msg_frame.pack(side=LEFT)
        
        Label(msg_frame, text="💬", font=("Segoe UI Emoji", 12), 
              bg="#c7ecee").grid(row=0, column=0, padx=(10, 5), pady=5)
        Label(msg_frame, text=text, font=("Comic Sans MS", 10), bg="#c7ecee", 
              fg="#5a5a5a", wraplength=350, justify=LEFT).grid(row=0, column=1, padx=(0, 10), pady=8)
        
        time_label = Label(bubble_frame, text=timestamp, font=("Comic Sans MS", 8), 
                          bg=theme["bg"], fg="#b8b8b8")
        time_label.pack(side=LEFT, padx=5)
    
    chat_canvas.update_idletasks()
    chat_canvas.config(scrollregion=chat_canvas.bbox("all"))
    chat_canvas.yview_moveto(1.0)


def add_message(sender, text, msg_type):
    """Ajoute un message système kawaii"""
    theme = themes[current_theme]
    bubble_frame = Frame(chat_canvas_frame, bg=theme["bg"])
    bubble_frame.pack(fill=X, padx=15, pady=4)
    
    emojis = {
        "system": "✨",
        "error": "😓",
        "waiting": "🔍",
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
    if status == "online":
        status_label.config(text="● En attente", fg="#ffd966")
    elif status == "connected":
        status_label.config(text="● Connecté !", fg="#90ee90")
    else:
        status_label.config(text="● Hors ligne", fg="#ffb3ba")


def change_theme(theme_name):
    """Change le thème de couleur"""
    global current_theme
    current_theme = theme_name
    theme = themes[theme_name]
    
 
    root.config(bg=theme["bg"])
    main_frame.config(bg=theme["main"])
    header.config(bg=theme["header"])
    status_frame.config(bg=theme["header"])
    status_label.config(bg=theme["header"])
    connection_label.config(bg=theme["header"])
    stats_label.config(bg=theme["header"])
    control_panel.config(bg=theme["control"])
    chat_container.config(bg=theme["control"])
    chat_canvas.config(bg=theme["bg"])
    chat_canvas_frame.config(bg=theme["bg"])
    input_area.config(bg=theme["control"])
    
    
    for widget in header.winfo_children():
        if isinstance(widget, Label):
            widget.config(bg=theme["header"])
    
    for widget in control_panel.winfo_children():
        if isinstance(widget, Label):
            widget.config(bg=theme["control"], fg=theme["accent"])
    
    for widget in chat_container.winfo_children():
        if isinstance(widget, Label):
            widget.config(bg=theme["control"], fg=theme["accent"])
    
   
    entry_port.config(insertbackground=theme["accent"])
    entry_message.config(insertbackground=theme["accent"])
    
    
    if btn_start['state'] == NORMAL:
        btn_start.config(bg=theme["button"])
    
    btn_send.config(bg=theme["bubble_you"], fg=theme["accent"])
    
  
    chat_scrollbar.config(bg=theme["header"], activebackground=theme["accent"])
    
    
    emoji_map = {"green": "💚", "pink": "💖", "blue": "💙", "purple": "💜"}
    root.title(f"{emoji_map[theme_name]} Serveur Chat")
    
    
    for widget in header.winfo_children():
        if isinstance(widget, Label) and "SERVEUR" in widget.cget("text"):
            widget.config(text=f"{emoji_map[theme_name]} SERVEUR CHAT {emoji_map[theme_name]}", 
                         fg=theme["accent"])


def disconnect_client():
    """Déconnecte le client"""
    global conn
    if conn:
        try:
            conn.close()
        except:
            pass
        conn = None
    btn_send['state'] = DISABLED
    entry_message['state'] = DISABLED


def stop_server():
    """Arrête le serveur"""
    global server_socket, conn, is_running
    is_running = False
    
    if conn:
        conn.close()
    if server_socket:
        server_socket.close()
    
    add_message("SYSTÈME", "😴 Serveur arrêté", "disconnect")
    pulse_status("offline")
    connection_label.config(text="👤 Personne", fg="#95a5a6")
    btn_start.config(bg=themes[current_theme]["button"], text="▶ Démarrer")
    btn_start['state'] = NORMAL
    btn_stop['state'] = DISABLED
    btn_send['state'] = DISABLED
    entry_port['state'] = NORMAL
    entry_message['state'] = DISABLED


def on_closing():
    """Fermeture propre"""
    stop_server()
    root.destroy()



root = Tk()
root.title("💚 Serveur Chat")
root.geometry("750x650")
root.configure(bg="#f0fff4")
root.protocol("WM_DELETE_WINDOW", on_closing)


try:
    title_font = tkfont.Font(family="Comic Sans MS", size=20, weight="bold")
    header_font = tkfont.Font(family="Comic Sans MS", size=11, weight="bold")
    body_font = tkfont.Font(family="Comic Sans MS", size=10)
except:
    title_font = tkfont.Font(family="Arial", size=20, weight="bold")
    header_font = tkfont.Font(family="Arial", size=11, weight="bold")
    body_font = tkfont.Font(family="Arial", size=10)


main_frame = Frame(root, bg="#d4f4dd", bd=3, relief=RIDGE)
main_frame.place(x=15, y=15, width=720, height=620)


header = Frame(main_frame, bg="#a8e6cf", height=100)
header.pack(fill=X, padx=3, pady=3)
header.pack_propagate(False)

Label(header, text="💚 SERVEUR 💚", font=title_font,
      bg="#a8e6cf", fg="#2d8659").pack(pady=(12, 5))

status_frame = Frame(header, bg="#a8e6cf")
status_frame.pack(pady=3)

status_label = Label(status_frame, text="● Hors ligne", font=header_font,
                     bg="#a8e6cf", fg="#ffb3ba")
status_label.pack(side=LEFT, padx=10)

connection_label = Label(status_frame, text="👤 Personne", font=body_font,
                         bg="#a8e6cf", fg="#95a5a6")
connection_label.pack(side=LEFT, padx=10)

stats_label = Label(status_frame, text="💬 0", font=body_font,
                    bg="#a8e6cf", fg="#95a5a6")
stats_label.pack(side=LEFT, padx=10)


control_panel = Frame(main_frame, bg="#e8f8f0", height=70)
control_panel.pack(fill=X, padx=3, pady=8)
control_panel.pack_propagate(False)

Label(control_panel, text="🔌 Port:", font=header_font,
      bg="#e8f8f0", fg="#2d8659").place(x=20, y=20)

entry_port = Entry(control_panel, font=body_font, bg="white", fg="#5a5a5a",
                   insertbackground="#2d8659", relief=SOLID, borderwidth=2, width=10)
entry_port.insert(0, "50050")
entry_port.place(x=100, y=18, height=30)

btn_start = Button(control_panel, text="▶ Démarrer", command=start_server,
                   bg="#81c784", fg="white", font=header_font, relief=FLAT,
                   cursor="hand2", borderwidth=0)
btn_start.place(x=240, y=18, width=150, height=30)

btn_stop = Button(control_panel, text="■ Arrêter", command=stop_server,
                  bg="#ffb3ba", fg="white", font=header_font, relief=FLAT,
                  cursor="hand2", state=DISABLED, borderwidth=0)
btn_stop.place(x=410, y=18, width=150, height=30)


Label(control_panel, text="🎨", font=("Segoe UI Emoji", 14),
      bg="#e8f8f0").place(x=580, y=20)

theme_green = Button(control_panel, text="", command=lambda: change_theme("green"),
                     bg="#81c784", width=2, relief=FLAT, cursor="hand2", borderwidth=1)
theme_green.place(x=610, y=20, width=20, height=25)

theme_pink = Button(control_panel, text="", command=lambda: change_theme("pink"),
                    bg="#ffc0cb", width=2, relief=FLAT, cursor="hand2", borderwidth=1)
theme_pink.place(x=635, y=20, width=20, height=25)

theme_blue = Button(control_panel, text="", command=lambda: change_theme("blue"),
                    bg="#64b5f6", width=2, relief=FLAT, cursor="hand2", borderwidth=1)
theme_blue.place(x=660, y=20, width=20, height=25)

theme_purple = Button(control_panel, text="", command=lambda: change_theme("purple"),
                      bg="#9575cd", width=2, relief=FLAT, cursor="hand2", borderwidth=1)
theme_purple.place(x=685, y=20, width=20, height=25)


chat_container = Frame(main_frame, bg="#e8f8f0")
chat_container.pack(fill=BOTH, expand=True, padx=3, pady=5)

Label(chat_container, text="💬 Conversation", font=header_font,
      bg="#e8f8f0", fg="#2d8659").pack(anchor=W, padx=12, pady=(8, 4))


chat_canvas = Canvas(chat_container, bg="#f0fff4", highlightthickness=0)
chat_scrollbar = Scrollbar(chat_container, orient="vertical", command=chat_canvas.yview,
                           bg="#a8e6cf", troughcolor="#f0fff4", 
                           activebackground="#2d8659", width=14)
chat_canvas_frame = Frame(chat_canvas, bg="#f0fff4")

chat_canvas_frame.bind("<Configure>", 
                       lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all")))

chat_canvas.create_window((0, 0), window=chat_canvas_frame, anchor="nw")
chat_canvas.configure(yscrollcommand=chat_scrollbar.set)

chat_canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=12, pady=8)
chat_scrollbar.pack(side=RIGHT, fill=Y, pady=8, padx=(0, 12))


input_area = Frame(main_frame, bg="#e8f8f0", height=70)
input_area.pack(fill=X, padx=3, pady=3)
input_area.pack_propagate(False)

entry_message = Entry(input_area, font=body_font, bg="white", fg="#5a5a5a",
                      insertbackground="#2d8659", relief=SOLID, borderwidth=2,
                      state=DISABLED)
entry_message.place(x=15, y=18, width=520, height=35)
entry_message.bind('<Return>', send_message)

btn_send = Button(input_area, text="Envoyer 💚", command=send_message,
                  bg="#c8e6c9", fg="#2d8659", font=header_font,
                  relief=FLAT, cursor="hand2", state=DISABLED, borderwidth=0)
btn_send.place(x=550, y=18, width=150, height=35)


add_message("SYSTÈME", "Bienvenue! Cliquez sur Démarrer 🌟", "system")

root.mainloop()


# import socket
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('localhost', 50050))
# server_socket.listen(1)
# print("Server is listening on port 50050...")

# conn, addr = server_socket.accept()
# print(f"Connection from {addr} has been established!")

# #dialog loop:
# while True:
#     data = conn.recv(1024).decode()
#     if data == 'exit' or data == '':
#         print("Client has disconnected.")
#         break
#     print(f"Received from client: {data}")
    
#     response = input("TALK :") 
#     conn.send(response.encode())

# #ferm la coonnexion
# conn.close()
# server_socket.close()
# print("Server has been closed.")
