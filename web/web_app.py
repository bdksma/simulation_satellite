# web_app.py
# ==========================================
# WEB MONITORING & TELECOMMAND UI
# - Monitoring telemetry dari BBU
# - Kirim telecommand ke BBU (TCP)
# - TC bisa dikirim kapan saja
# ==========================================

import socket
import streamlit as st
import time

# ==========================================
# NETWORK CONFIG
# ==========================================
BBU_IP = "127.0.0.1"
BBU_WEB_PORT = 7001

# ==========================================
# STREAMLIT UI SETUP
# ==========================================
st.set_page_config(page_title="Satellite Web Monitor", layout="centered")

st.title("🛰️ Satellite Web Monitoring")
st.markdown("Monitoring Telemetry & Sending Telecommand via BBU")

# ==========================================
# TELECOMMAND SECTION
# ==========================================
st.subheader("📡 Telecommand")

tc_input = st.text_input("Enter Telecommand", value="PING")

if st.button("Send Telecommand"):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((BBU_IP, BBU_WEB_PORT))
        sock.sendall(tc_input.encode())
        sock.close()
        st.success(f"Telecommand '{tc_input}' sent to BBU")
    except Exception as e:
        st.error(f"Failed to send TC: {e}")

# ==========================================
# TELEMETRY MONITOR (SIMULATED VIEW)
# ==========================================
st.subheader("📈 Telemetry Monitor")

placeholder = st.empty()

# NOTE:
# Untuk LEVEL 2 demo, telemetry ditampilkan sebagai log status
# Real telemetry streaming bisa ditambahkan via WebSocket / REST

while True:
    with placeholder.container():
        st.write("[WEB] Monitoring telemetry from BBU...")
        st.caption(time.strftime("%Y-%m-%d %H:%M:%S"))
    time.sleep(2)