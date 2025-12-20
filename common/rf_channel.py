# rf_channel.py
# =====================================================
# RF CHANNEL SIMULATION
# - Packet loss
# - Propagation delay
# - Noise / corruption
# =====================================================

import random
import time

# =====================================================
# CHANNEL CONFIG
# =====================================================
PACKET_LOSS_PROB = 0.05      # 5% loss
PROPAGATION_DELAY = 0.25     # seconds (LEO ~ few hundred ms RTT)
BIT_ERROR_PROB = 0.02        # probability payload corrupted

# =====================================================
# CHANNEL FUNCTIONS
# =====================================================
def propagate(packet: dict):
    """
    Simulate RF propagation effects
    Return None if packet lost
    """

    # Propagation delay
    time.sleep(PROPAGATION_DELAY)

    # Packet loss
    if random.random() < PACKET_LOSS_PROB:
        return None

    # Bit error / corruption
    if random.random() < BIT_ERROR_PROB:
        packet = packet.copy()
        packet["corrupted"] = True

    return packet

# =====================================================
# DEBUG TEST
# =====================================================
if __name__ == "__main__":
    for i in range(10):
        pkt = {"seq": i, "data": "TM", "corrupted": False}
        out = propagate(pkt)
        print(out)
