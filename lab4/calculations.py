import numpy as np
import os
from scipy.signal import detrend
import matplotlib.pyplot as plt

def raspi_import(file_name, channels=5):
    dir = f"output"

    if not os.path.exists(dir):
        os.makedirs(dir)

    path = f"{dir}/{file_name}.bin"

    with open(path, 'r') as fid:
        sample_period = np.fromfile(fid, count=1, dtype=float)[0]
        data = np.fromfile(fid, dtype='uint16').astype('float64')
        # The "dangling" `.astype('float64')` casts data to double precision
        # Stops noisy autocorrelation due to overflow
        data = data.reshape((-1, channels))

    # sample period is given in microseconds-changes units to seconds
    sample_period *= 1e-6
    return sample_period, data


def calculate_doppler(sample_period, data):
    # Extract the I (in-phase) and Q (quadrature) components
    i_data = data[:, 4]
    q_data = data[:, 3]

    # Combine I and Q components into a complex signal
    complex_signal = i_data + 1j * q_data

    # Perform FFT on the complex signal
    fft_result = np.fft.fft(complex_signal)

    # Shift the zero-frequency component to the center
    fft_result = np.fft.fftshift(fft_result)

    # Compute the Doppler shift frequencies
    freqs = np.fft.fftfreq(len(complex_signal), d=sample_period)
    freqs = np.fft.fftshift(freqs)

    # Return the FFT result and corresponding frequencies
    return fft_result, freqs

def plot(fft):
    """
    Plot the FFT result.
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.plot(fft)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude')
    ax.set_title('FFT result')
    plt.show()

def find_latest_file(folder):
    files = [f for f in os.listdir(folder) if f.endswith('.bin')]
    if not files:
        raise FileNotFoundError("No .bin files found in the folder.")
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(folder, f)))
    return os.path.splitext(latest_file)[0]

def doppler_frec(fft):
    max_index = np.argmax(np.abs(fft))
    max_frequency = freqs[max_index]
    max_amplitude = np.abs(fft[max_index])

    print(f"Max frequency: {max_frequency} Hz")
    print(f"Max amplitude: {max_amplitude}")

    c = 3e8
    f_0 = 24.13e9

    doppler_shift = max_frequency
    v = doppler_shift * c / (2 * f_0)
    return v

if __name__ == "__main__":
    file_name = "d-18.06.14" #find_latest_file("output")
    sample_period, data = raspi_import(file_name)
    print(f"Sample period: {sample_period}")
    print(f"Data shape: {data.shape}")

    detrended_data = detrend(data, axis=0)

    fft_result, freqs = calculate_doppler(sample_period, detrended_data)
    plot(fft_result)

    v = doppler_frec(fft_result)
    print(f"Measured speed: {v} m/s")

    