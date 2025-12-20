# satellite_node.py
# ================================
# Simulasi NODE SATELIT LEO
# - Kirim Telemetry (TM) via UDP ke BBU
# - Terima Telecommand (TC) via UDP dari BBU
# - Hitung efek Doppler sederhana
# - Tidak tahu apa-apa soal Web / TCP

import socket
import time
import math
import threading

# ================================
# KONFIGURASI JARINGAN
# ================================
SAT_IP = "127.0.0.1"
SAT_TM_PORT = 5001      # TM keluar ke BBU
SAT_TC_PORT = 5002      # TC masuk dari BBU
BBU_IP = "127.0.0.1"
BBU_TM_PORT = 6001      # Port TM listener di BBU

# ================================
# PARAMETER ORBIT (SIMPLIFIED)
# ================================
ORBIT_PERIOD = 5400     # detik (90 menit)
MAX_DOPPLER = 5000      # Hz (contoh LEO)
TM_INTERVAL = 1.0       # detik

seq_tm = 0
running = True

# ================================
# FUNGSI DOPPLER SIMPLIFIED
# ================================
def compute_doppler(t):
    """
    Doppler sinusoidal sederhana
    Positif saat mendekat, negatif saat menjauh
    """
    phase = 2 * math.pi * (t % ORBIT_PERIOD) / ORBIT_PERIOD
    return int(MAX_DOPPLER * math.sin(phase))

# ================================
# THREAD: KIRIM TELEMETRY
# ================================
def telemetry_sender():
    global seq_tm
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("[SAT] Telemetry sender started")
    t0 = time.time()

    while running:
        t = time.time() - t0
        doppler = compute_doppler(t)

        tm_msg = f"TM,{seq_tm},{doppler}"
        sock.sendto(tm_msg.encode(), (BBU_IP, BBU_TM_PORT))

        print(f"[SAT] TM seq={seq_tm} doppler={doppler}")
        seq_tm += 1
        time.sleep(TM_INTERVAL)

# ================================
# THREAD: TERIMA TELECOMMAND
# ================================
def telecommand_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SAT_IP, SAT_TC_PORT))

    print("[SAT] Telecommand receiver listening")

    while running:
        data, addr = sock.recvfrom(1024)
        tc = data.decode()
        print(f"[SAT] TC received: {tc}")

# ================================
# MAIN
# ================================
if __name__ == "__main__":
    print("=== SATELLITE NODE STARTED ===")

    t_tm = threading.Thread(target=telemetry_sender, daemon=True)
    t_tc = threading.Thread(target=telecommand_receiver, daemon=True)

    t_tm.start()
    t_tc.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        running = False
        print("\n[SAT] Shutting down")
