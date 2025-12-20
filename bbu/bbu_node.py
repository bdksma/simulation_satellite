# bbu_node.py
# ==========================================
# SIMULASI BBU / GROUND SYSTEM NODE
# - Terima TM dari Satelit (UDP)
# - Simulasi visibility window (LEO pass)
# - Simulasi RF effects: loss, noise, propagation
# - Buffer telemetry
# - Terima TC dari Web (TCP)
# - Queue TC & kirim ke satelit saat visible
# ==========================================

import socket
import threading
import time
import random
import math

# ==========================================
# NETWORK CONFIG
# ==========================================
BBU_IP = "127.0.0.1"

# UDP: Satellite <-> BBU
BBU_TM_PORT = 6001        # receive TM from satellite
BBU_TC_PORT = 6002        # send TC to satellite
SAT_IP = "127.0.0.1"
SAT_TC_PORT = 5002

# TCP: BBU <-> Web
BBU_WEB_PORT = 7001

# ==========================================
# VISIBILITY WINDOW (SIMPLIFIED)
# ==========================================
PASS_PERIOD = 120         # detik (simulasi orbit cepat)
PASS_DURATION = 40        # detik visible

# ==========================================
# RF CHANNEL PARAMETERS (rf_like)
# ==========================================
PACKET_LOSS_PROB = 0.1    # 10% TM loss
PROP_DELAY = 0.2          # detik delay propagasi

# ==========================================
# GLOBAL STATE
# ==========================================
telemetry_buffer = []
telecommand_queue = []
visible = False
running = True

# ==========================================
# VISIBILITY LOGIC
# ==========================================
def visibility_manager():
    global visible
    print("[BBU] Visibility manager started")
    while running:
        t = int(time.time()) % PASS_PERIOD
        visible = t < PASS_DURATION
        time.sleep(1)

# ==========================================
# TM RECEIVER (FROM SATELLITE)
# ==========================================
def tm_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((BBU_IP, BBU_TM_PORT))
    print("[BBU] Listening TM from satellite")

    while running:
        data, _ = sock.recvfrom(1024)
        msg = data.decode()

        if not visible:
            continue  # satellite not visible

        # Simulate packet loss
        if random.random() < PACKET_LOSS_PROB:
            print("[BBU] TM dropped (RF loss)")
            continue

        time.sleep(PROP_DELAY)
        telemetry_buffer.append(msg)
        print(f"[BBU] TM RX -> buffer: {msg}")

# ==========================================
# TM FORWARDER (TO WEB)
# ==========================================
def tm_forwarder():
    while running:
        if telemetry_buffer:
            tm = telemetry_buffer.pop(0)
            print(f"[BBU] TM forwarded to Web: {tm}")
        time.sleep(0.5)

# ==========================================
# TC SENDER (TO SATELLITE)
# ==========================================
def tc_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[BBU] TC sender ready")

    while running:
        if telecommand_queue and visible:
            tc = telecommand_queue.pop(0)
            sock.sendto(tc.encode(), (SAT_IP, SAT_TC_PORT))
            print(f"[BBU] TC sent to satellite: {tc}")
        time.sleep(1)

# ==========================================
# TC RECEIVER (FROM WEB via TCP)
# ==========================================
def tc_receiver_from_web():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((BBU_IP, BBU_WEB_PORT))
    sock.listen(1)
    print("[BBU] Waiting TC from Web (TCP)")

    while running:
        conn, addr = sock.accept()
        data = conn.recv(1024)
        tc = data.decode()
        telecommand_queue.append(tc)
        print(f"[BBU] TC queued from Web: {tc}")
        conn.close()

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    print("=== BBU NODE STARTED ===")

    threads = [
        threading.Thread(target=visibility_manager, daemon=True),
        threading.Thread(target=tm_receiver, daemon=True),
        threading.Thread(target=tm_forwarder, daemon=True),
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
        print("\n[BBU] Shutting down")
