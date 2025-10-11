import socket
import asyncio
import threading
from textual.app import App
from fts.app.backend.contacts import get_broadcast_addresses, has_public_broadcast
from fts.app.config import CHAT_PORT

CHAT_KEY = b"FTSCHATMSG"

def send(msg, timeout=0.5) -> str:
    try:
        msg = CHAT_KEY + bytes(str(msg), "utf-8")
    except:
        return "failed to convert message to utf-16"

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("0.0.0.0", 0))  # OS assigns a free port
    sock.settimeout(timeout)

    broadcasts = get_broadcast_addresses()
    try:
        for baddr in broadcasts:
            if has_public_broadcast(baddr):
                return "no public broadcast allowed"
            sock.sendto(msg, (baddr, CHAT_PORT))
    except Exception as e:
        sock.close()
        return e.message

    sock.close()
    return ""

def start_chat_listener(app: App, port: int, callback):
    """
    Start a background thread that listens for UDP broadcast packets.
    Calls `callback(data, addr)` on the main thread.
    """
    def listen():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", port))
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                app.call_from_thread(callback, data, addr)
            except Exception as e:
                print("UDP listener error:", e)
                break

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()
    return thread