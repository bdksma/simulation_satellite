# ==========================================
# SIMULASI BBU NODE (FINAL STABLE)
# ==========================================

import socket
import threading
import time
import random

from common.orbit import is_visible

BBU_IP = "127.0.0.1"

# Satellite
BBU_TM_PORT = 6001
SAT_IP = "127.0.0.1"
SAT_TC_PORT = 5002

# Web
BBU_TC_PORT = 7001   # Web -> BBU (TC)
BBU_TM_PORT_WEB = 7002  # BBU -> Web (TM)

PASS_PERIOD = 120
PASS_DURATION = 40
PACKET_LOSS_PROB = 0.1
PROP_DELAY = 0.2

telemetry_buffer = []
telecommand_queue = []
visible = False
running = True
web_tm_conn = None

# ==========================================
def visibility_manager():
    global visible
    while running:
        visible = (int(time.time()) % PASS_PERIOD) < PASS_DURATION
        time.sleep(1)

# ==========================================
def tm_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((BBU_IP, BBU_TM_PORT))
    print("[BBU] Listening TM from satellite")

    while running:
        data, _ = sock.recvfrom(1024)
        tm = data.decode()
        telemetry_buffer.append(tm)
        print(f"[BBU] TM RX -> buffer: {tm}")


# ==========================================
def tm_server_for_web():
    global web_tm_conn
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((BBU_IP, BBU_TM_PORT_WEB))
    server.listen(1)
    print("[BBU] TM server for Web listening on 7002")

    web_tm_conn, _ = server.accept()
    print("[BBU] Web connected for TM")

    while running:
        if telemetry_buffer and visible:
            tm = telemetry_buffer.pop(0)
            try:
                web_tm_conn.sendall(tm.encode())
                print(f"[BBU] TM sent to Web: {tm}")
            except:
                telemetry_buffer.insert(0, tm)
                print("[BBU] Web disconnected")
                break
        time.sleep(1)

# ==========================================
def tc_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while running:
        if telecommand_queue and visible:
            tc = telecommand_queue.pop(0)
            sock.sendto(tc.encode(), (SAT_IP, SAT_TC_PORT))
            print(f"[BBU] TC sent to satellite: {tc}")
        time.sleep(1)

# ==========================================
def tc_receiver_from_web():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((BBU_IP, BBU_TC_PORT))
    sock.listen(1)
    print("[BBU] Waiting TC from Web")

    while running:
        conn, _ = sock.accept()
        tc = conn.recv(1024).decode()
        telecommand_queue.append(tc)
        print(f"[BBU] TC queued from Web: {tc}")
        conn.close()

# ==========================================
if __name__ == "__main__":
    print("=== BBU NODE STARTED ===")

    threads = [
        threading.Thread(target=visibility_manager, daemon=True),
        threading.Thread(target=tm_receiver, daemon=True),
        threading.Thread(target=tm_server_for_web, daemon=True),
        threading.Thread(target=tc_sender, daemon=True),
        threading.Thread(target=tc_receiver_from_web, daemon=True),
    ]

    for t in threads:
        t.start()

    try:
        while True:
            print(f"[BBU] Visible={visible} | TM_buffer={len(telemetry_buffer)} | TC_queue={len(telecommand_queue)}")
            time.sleep(3)
    except KeyboardInterrupt:
        running = False
