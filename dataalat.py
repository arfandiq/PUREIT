from bitalino import BITalino
import time, csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import deque
from scipy.signal import butter, sosfilt, welch

# ---------------------
# Konfigurasi
# ---------------------
macAddress = "0C:43:14:24:78:DD"
sampling_rate = 1000
channels = [0]  # A1
csv_file = "emg_data_A1.csv"
png_file = "emg_plot.png"
duration = 35  # detik
buffer_size = 2000

# ---------------------
# Buffer realtime (untuk animasi)
# ---------------------
raw_buffer = deque([0.0]*buffer_size, maxlen=buffer_size)
rms_buffer = deque([0.0]*buffer_size, maxlen=buffer_size)
xdata = np.arange(buffer_size)

# ---------------------
# Penampung full data
# ---------------------
all_raw = []
all_rms = []

# ---------------------
# Bandpass filter (20–450 Hz)
# ---------------------
def butter_bandpass(lowcut, highcut, fs, order=4):
    sos = butter(order, [lowcut, highcut], fs=fs, btype="band", output="sos")
    return sos

sos_bp = butter_bandpass(20, 450, sampling_rate)

def bandpass_filter(data):
    return sosfilt(sos_bp, data)

# ---------------------
# Envelope low-pass (5 Hz)
# ---------------------
def butter_lowpass(cutoff, fs, order=4):
    sos = butter(order, cutoff, fs=fs, btype="low", output="sos")
    return sos

sos_lp = butter_lowpass(5, sampling_rate)

def lowpass_filter(data):
    return sosfilt(sos_lp, data)

# ---------------------
# Connect ke BITalino
# ---------------------
device = BITalino(macAddress)
print("✅ Connected:", device.version())
device.start(sampling_rate, channels)

# ---------------------
# CSV logger (timestamp relatif, raw EMG, RMS)
# ---------------------
f = open(csv_file, "w", newline="")
writer = csv.writer(f)
writer.writerow(["Timestamp", "Raw_EMG", "RMS"])  # header

# ---------------------
# Plot Realtime
# ---------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)

(line1,) = ax1.plot(xdata, list(raw_buffer), lw=0.8, color="blue")
ax1.set_ylim(-800, 800)
ax1.set_ylabel("EMG (filtered)")
ax1.set_title("Realtime EMG Signal (A1)")

(line2,) = ax2.plot(xdata, list(rms_buffer), lw=0.9, color="red")
ax2.set_ylim(0, 200)
ax2.set_xlabel("Samples")
ax2.set_ylabel("EMG Envelope (RMS)")

start_time = time.time()

# ---------------------
# Update loop
# ---------------------
def update(frame):
    try:
        data = device.read(50)
        if data is None or len(data) == 0:
            return line1, line2

        # Ambil channel A1 (raw EMG)
        emg_values = [row[5] for row in data]

        emg_array = np.array(emg_values, dtype=float)
        emg_array = emg_array - np.mean(emg_array)   # DC offset

        # Bandpass
        filtered = bandpass_filter(emg_array)

        # Rectify
        rectified = np.abs(filtered)

        # Envelope (RMS via moving average)
        window = 200
        squared = rectified**2
        kernel = np.ones(window)/window
        rms = np.sqrt(np.convolve(squared, kernel, mode="same"))
        smooth_rms = lowpass_filter(rms)

        # Simpan ke CSV (pakai detik sejak start)
        for raw_val, rms_val in zip(filtered, smooth_rms):
            timestamp = round(time.time() - start_time, 4)  # presisi 4 digit
            writer.writerow([timestamp, raw_val, rms_val])

        # Update buffer realtime
        raw_buffer.extend(filtered.tolist())
        rms_buffer.extend(smooth_rms.tolist())

        # Simpan full data
        all_raw.extend(filtered.tolist())
        all_rms.extend(smooth_rms.tolist())

        # Update plot
        line1.set_ydata(list(raw_buffer))
        line2.set_ydata(list(rms_buffer))

    except Exception as e:
        print("❌ Error in update():", e)

    if time.time() - start_time > duration:
        plt.close(fig)

    return line1, line2

ani = animation.FuncAnimation(fig, update, interval=50, blit=False)
plt.tight_layout()
plt.show()

# ---------------------
# Save full plot
# ---------------------
plt.figure(figsize=(12, 8))

plt.subplot(2, 1, 1)
plt.plot(all_raw, color="blue", lw=0.7)
plt.title("Full EMG Recording (Filtered)")
plt.ylabel("Amplitude")
plt.ylim(min(all_raw)*1.2, max(all_raw)*1.2)

plt.subplot(2, 1, 2)
plt.plot(all_rms, color="red", lw=0.8)
plt.title("Full EMG Envelope (RMS)")
plt.xlabel("Samples")
plt.ylabel("RMS")
plt.ylim(0, max(all_rms)*1.2)

plt.tight_layout()
plt.savefig(png_file, dpi=150)
print(f"🖼️ Grafik FULL tersimpan: {png_file}")

# ---------------------
# Stop device
# ---------------------
try:
    device.stop()
    device.close()
except Exception:
    pass
f.close()
