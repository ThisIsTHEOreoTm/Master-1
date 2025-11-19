#!/usr/bin/env python3
"""
node.py - simple UDP node for exercises:
 - Exercice 1: socket node with send() and receive()
 - Exercice 2: token-ring behavior: optional 'jeton' argument

Usage:
  python node.py port_local [succ_port] [jeton]

Examples:
  # start a node listening on 5000, successor unknown, no token
  python node.py 5000

  # start a node listening on 5001, successor is port 5002, node has the token initially
  python node.py 5001 5002 jeton

Notes:
 - This is UDP-based for simplicity.
 - Messages have simple prefixes: "TOKEN" (token), "MSG|<from_port>|<text>" (regular message).
"""

import socket
import threading
import sys
import time

BUFFER = 4096
LOCALHOST = "127.0.0.1"


class Node:
    def __init__(self, local_port: int, succ_port: int = None, has_token: bool = False):
        self.local_port = int(local_port)
        self.succ_port = int(succ_port) if succ_port is not None else None
        self.has_token = bool(has_token)
        self.running = True

        # create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((LOCALHOST, self.local_port))
        self.sock.settimeout(1.0)

        print("=" * 50)
        print(f"[NODE START] Listening on {LOCALHOST}:{self.local_port}")
        print(f" Successor port: {self.succ_port}")
        print(f" Has token: {self.has_token}")
        print("=" * 50)

    def receive_loop(self):
        """Function receive(): blocking loop to receive messages indefinitely."""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(BUFFER)
                msg = data.decode("utf-8", errors="replace")
                # Distinguish token vs normal message
                if msg.startswith("TOKEN"):
                    print("\n" + "-" * 40)
                    print(f"[RECEIVE] TOKEN received from {addr}")
                    self.has_token = True
                    print("[STATE] I now hold the TOKEN.")
                    print("-" * 40 + "\n")
                elif msg.startswith("MSG|"):
                    # format: MSG|from_port|text
                    parts = msg.split("|", 2)
                    if len(parts) >= 3:
                        from_port = parts[1]
                        text = parts[2]
                        print("\n" + "-" * 40)
                        print(f"[RECEIVE] Message from node:{from_port} (addr {addr}):")
                        print(f"  CONTENT -> {text}")
                        print("-" * 40 + "\n")
                    else:
                        print(f"[RECEIVE] Malformed MSG from {addr}: {msg}")
                else:
                    print(f"[RECEIVE] Unknown payload from {addr}: {msg}")
            except socket.timeout:
                continue
            except Exception as e:
                print("[ERROR] receive_loop:", e)
                break

    def send_message(self, dest_ip: str, dest_port: int, text: str):
        """Send a normal message (allowed anytime; in token-ring rules
        you'd normally require token to send, but we show both behaviors)."""
        payload = f"MSG|{self.local_port}|{text}"
        self.sock.sendto(payload.encode("utf-8"), (dest_ip, int(dest_port)))
        print(f"[SEND] Sent message to {dest_ip}:{dest_port}")

    def pass_token(self, dest_ip: str, dest_port: int):
        """Send the token to the successor and relinquish the token."""
        payload = "TOKEN"
        self.sock.sendto(payload.encode("utf-8"), (dest_ip, int(dest_port)))
        self.has_token = False
        print(f"[TOKEN] Passed token to {dest_ip}:{dest_port}. I no longer have it.")

    def menu_send(self):
        """Replacement for send(): interactive menu that asks user what to do.
        If node has token, it can either send a message or pass the token.
        If it does not have token, only passing token is allowed if the
        user decides to forward (but semantically they should wait)."""
        print("\n**** ENTERING MENU (menu_send) ****")
        print("Commands:")
        print("  1) send message")
        print("  2) pass token to successor")
        print("  3) set/change successor port")
        print("  4) show status")
        print("  q) quit node")
        print("Note: in token-ring, only the node with the token should send messages.\n")

        while self.running:
            cmd = input("menu> ").strip().lower()
            if cmd == "1" or cmd == "send" or cmd == "1)":
                # If token-rule enforced, check has_token:
                if not self.has_token:
                    print("[MENU] You do NOT hold the token. According to token-ring rules you shouldn't send messages.")
                    yn = input("  Still send message anyway? (y/N): ").strip().lower()
                    if yn not in ("y", "yes"):
                        continue
                dest = input("  Enter destination port (localhost): ").strip()
                text = input("  Enter message text: ").strip()
                if dest.isdigit():
                    self.send_message(LOCALHOST, int(dest), text)
                else:
                    print("[MENU] invalid port")

            elif cmd == "2" or cmd == "pass" or cmd == "2)":
                # pass token to successor
                if self.succ_port is None:
                    sp = input("  No successor set. Enter successor port to send token to: ").strip()
                    if sp.isdigit():
                        self.succ_port = int(sp)
                    else:
                        print("[MENU] invalid port; token not passed")
                        continue
                # send token (even if we don't have it; user may pass it)
                self.pass_token(LOCALHOST, self.succ_port)

            elif cmd == "3":
                sp = input("  Enter successor port: ").strip()
                if sp.isdigit():
                    self.succ_port = int(sp)
                    print(f"[MENU] successor updated to {self.succ_port}")
                else:
                    print("[MENU] invalid port")

            elif cmd == "4":
                print("-" * 30)
                print(f"Local port: {self.local_port}")
                print(f"Successor: {self.succ_port}")
                print(f"Holds token: {self.has_token}")
                print("-" * 30)

            elif cmd == "q" or cmd == "quit" or cmd == "exit":
                print("[MENU] quitting node...")
                self.running = False
                break

            else:
                print("[MENU] unknown command (type 1,2,3,4 or q)")

    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass


def main():
    # parse args
    if len(sys.argv) < 2:
        print("Usage: python node.py port_local [succ_port] [jeton]")
        sys.exit(1)

    local_port = int(sys.argv[1])
    succ_port = None
    has_token = False

    if len(sys.argv) >= 3:
        # If second arg is 'jeton', treat as token flag; otherwise succ_port
        if sys.argv[2].lower() == "jeton":
            has_token = True
        else:
            try:
                succ_port = int(sys.argv[2])
            except ValueError:
                print("Second arg should be successor port or 'jeton'.")
                sys.exit(1)
    if len(sys.argv) >= 4:
        # third arg may be 'jeton'
        if sys.argv[3].lower() == "jeton":
            has_token = True

    node = Node(local_port, succ_port, has_token)

    # start receiver thread
    recv_thread = threading.Thread(target=node.receive_loop, daemon=True)
    recv_thread.start()

    try:
        # start interactive menu -> menu_send (replaces simple send)
        node.menu_send()
    except KeyboardInterrupt:
        print("\n[MAIN] KeyboardInterrupt received. Shutting down...")
    finally:
        node.stop()
        time.sleep(0.2)
        print("[MAIN] Node stopped.")


if __name__ == "__main__":
    main()
