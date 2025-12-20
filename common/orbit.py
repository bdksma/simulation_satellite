# orbit.py
# =====================================================
# ORBIT & VISIBILITY MODEL (SIMPLIFIED LEO)
# - Visibility window (ON / OFF)
# - Doppler shift simulation
# =====================================================

import math
import time

# =====================================================
# ORBIT CONFIG (SIMPLIFIED)
# =====================================================
ORBIT_PERIOD = 90 * 60        # 90 menit (LEO typical)
PASS_DURATION = 10 * 60       # 10 menit visible per orbit
MAX_DOPPLER = 5000            # Hz (order of magnitude LEO)

# =====================================================
# VISIBILITY WINDOW
# =====================================================
def is_visible(t=None):
    """
    Return True jika satellite sedang visible ke ground station
    berdasarkan model periodik sederhana
    """
    if t is None:
        t = time.time()

    phase = t % ORBIT_PERIOD
    return phase < PASS_DURATION

# =====================================================
# DOPPLER MODEL
# =====================================================
def doppler_shift(t=None):
    """
    Simulasi doppler shift sinusoidal
    Positif: mendekat, Negatif: menjauh
    """
    if t is None:
        t = time.time()

    phase = (t % ORBIT_PERIOD) / ORBIT_PERIOD
    return int(MAX_DOPPLER * math.sin(2 * math.pi * phase))

# =====================================================
# DEBUG TEST
# =====================================================
if __name__ == "__main__":
    while True:
        print("Visible:", is_visible(), "Doppler:", doppler_shift())
        time.sleep(1)
