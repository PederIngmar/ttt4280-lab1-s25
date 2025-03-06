import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# Load data (assuming space/tab-separated values)
filename = "lab3/roi_output/latest.txt"  # Replace with your actual filename
data = np.loadtxt(filename)

# Extract time (if available) and RGB columns
if data.shape[1] == 4:  # If first column is time
    time = data[:, 0]
    R, G, B = data[:, 1], data[:, 2], data[:, 3]
else:
    time = np.arange(len(data))  # If time is missing, assume sample index
    R, G, B = data[:, 0], data[:, 1], data[:, 2]

# Apply a low-pass filter to remove noise
def filter_signal(signal_data, cutoff=3, fs=100, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return signal.filtfilt(b, a, signal_data)

# Filter each signal
fs = 100  # Sampling frequency (adjust if known)
R_filtered = filter_signal(R, fs=fs)
G_filtered = filter_signal(G, fs=fs)
B_filtered = filter_signal(B, fs=fs)

# Find peaks (heartbeats)
def find_pulse_rate(filtered_signal, time, fs):
    peaks, _ = signal.find_peaks(filtered_signal, distance=fs/2)  # Min 0.5s between beats
    peak_intervals = np.diff(time[peaks])  # Time differences between peaks
    pulse_rate = 60 / np.mean(peak_intervals) if len(peak_intervals) > 0 else 0
    return pulse_rate, peaks

pulse_R, peaks_R = find_pulse_rate(R_filtered, time, fs)
pulse_G, peaks_G = find_pulse_rate(G_filtered, time, fs)
pulse_B, peaks_B = find_pulse_rate(B_filtered, time, fs)

# Print results
print(f"Pulse Rate from R: {pulse_R:.2f} BPM")
print(f"Pulse Rate from G: {pulse_G:.2f} BPM")
print(f"Pulse Rate from B: {pulse_B:.2f} BPM")

# Plot signals
plt.figure(figsize=(10, 5))
plt.plot(time, R_filtered, label="Filtered R", color='red')
plt.plot(time[peaks_R], R_filtered[peaks_R], "ro", label="R Peaks")
plt.plot(time, G_filtered, label="Filtered G", color='green')
plt.plot(time[peaks_G], G_filtered[peaks_G], "go", label="G Peaks")
plt.plot(time, B_filtered, label="Filtered B", color='blue')
plt.plot(time[peaks_B], B_filtered[peaks_B], "bo", label="B Peaks")
plt.xlabel("Time")
plt.ylabel("Intensity")
plt.legend()
plt.title("Pulse Detection from Light Signals")
plt.show()

