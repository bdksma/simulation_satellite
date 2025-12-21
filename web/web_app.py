import socket
import streamlit as st
import time

BBU_IP = "127.0.0.1"
BBU_TM_PORT = 7002
BBU_TC_PORT = 7001

if "tm_buffer" not in st.session_state:
    st.session_state.tm_buffer = []

if "tm_socket" not in st.session_state:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((BBU_IP, BBU_TM_PORT))
    s.setblocking(False)
    st.session_state.tm_socket = s

st.set_page_config(page_title="Satellite Web Monitor")
st.title("🛰️ Satellite Web Monitoring")

# RECEIVE TM
try:
    data = st.session_state.tm_socket.recv(1024)
    if data:
        st.session_state.tm_buffer.append(data.decode())
        st.session_state.tm_buffer = st.session_state.tm_buffer[-50:]
except BlockingIOError:
    pass

# SEND TC
st.subheader("📡 Telecommand")
tc = st.text_input("Command", "PING")
if st.button("Send"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((BBU_IP, BBU_TC_PORT))
    s.sendall(tc.encode())
    s.close()
    st.success("TC sent")
# SHOW TM
st.subheader("📈 Telemetry")
if st.session_state.tm_buffer:
    for tm in st.session_state.tm_buffer[::-1][:10]:
        st.code(tm)
else:
    st.info("Waiting telemetry...")

time.sleep(1)
st.rerun()
