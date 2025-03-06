import numpy as np 
import os
import glob
from scipy.signal import detrend

def raspi_import(path, file_name, channels=5):
    path = f"{path}/{file_name}.bin"

    with open(path, 'r') as fid:
        sample_period = np.fromfile(fid, count=1, dtype=float)[0]
        data = np.fromfile(fid, dtype='uint16').astype('float64')
        # The "dangling" `.astype('float64')` casts data to double precision
        # Stops noisy autocorrelation due to overflow
        data = data.reshape((-1, channels))
    
    # sample period is given in microseconds-changes units to seconds
    sample_period *= 1e-6
    return sample_period, data
  

def delays(sample_period, data):
    if data is None:
        return None
    data = data[:, 2:]
    D = {}
    channel_pairs = [(0, 1), (1, 2), (0, 2)]
    sampling_f = 1 / sample_period

    upsample_factor = 10
    for cpair in channel_pairs:
        d1 = detrend(data[:, cpair[0]])
        d2 = detrend(data[:, cpair[1]])

        peak_idx = np.argmax(np.abs(d1))
        start = max(0,peak_idx-1000)
        end = min(len(d1),peak_idx+1000)

        d1_window = d1[start:end]
        d2_window = d2[start:end]

        crosscorrelation = np.abs(np.correlate(d1_window, d2_window, mode='full'))
        lags = np.arange(-len(d1_window)+1, len(d1_window))

        #crosscorrelation = np.correlate(d1,d2, mode='full')
        #lags = np.arange(-len(d1)+1, len(d1))
        max_lag = lags[np.argmax(crosscorrelation)]
        delta_t = max_lag / sampling_f
        D[cpair] = delta_t

    return D


def all_delays(angle):
    folder_path = f"output/{angle}"
    bin_files = glob.glob(f"{folder_path}/*.bin")
    all_delays = []

    for bin_file in bin_files:
        file_name = os.path.splitext(os.path.basename(bin_file))[0]
        sample_period, data = raspi_import(folder_path, file_name)
        d = delays(sample_period, data)
        all_delays.append(d)
    return all_delays

def average_delays(all_delays):
    avg_delays = {}
    for cpair in all_delays[0].keys():
        avg_delays[cpair] = np.mean([d[cpair] for d in all_delays])
    return avg_delays


def std_delays(all_delays):
    # Calculate variance of delays
    var_delays = {}
    for cpair in all_delays[0].keys():
        var_delays[cpair] = np.var([d[cpair] for d in all_delays])

    # Calculate standard deviation of delays
    std_delays = {}
    for cpair in all_delays[0].keys():
        std_delays[cpair] = np.std([d[cpair] for d in all_delays])

    return std_delays


def estimate_angle(delays):
    t12 = delays[(0, 1)]
    t13 = delays[(0, 2)]
    t23 = delays[(1, 2)]

    x = (t23 - t12 + 2*t13)
    y = (t23 + t12)

    if x < 0:
        print("x<0")
        theta = - np.arctan2(np.sqrt(3)* y, x)
    elif x == 0:
        print("x = 0")
        theta = -np.pi/2
    else:
        print("x >>>> 0")
        theta = -np.arctan2(np.sqrt(3)* y, x)

    cali_factor = 43.37
    theta_deg = np.degrees(theta) + cali_factor

    print(f"Estimated angle: {theta_deg:.2f} degrees")
    return theta_deg

def compute_statistics():
    angles = [0, 36, 72, 108, 144, 180]
    estimated_angles = []
    print("Statistics for all angles:")
    for angle in angles:
        print(f"------- angle:{angle}-------")
        bin_files = glob.glob(f"output/{angle}/*.bin")
        for i in range(0, len(bin_files)):
            current_bin_file = bin_files[i]
            file_name = os.path.splitext(os.path.basename(current_bin_file))[0]
            sample_period, data = raspi_import(f"output/{angle}", file_name)
            d = delays(sample_period, data)
            estimated_angles.append(estimate_angle(d))
        print(f"Mean: {np.mean(estimated_angles):.2f}")
        print(f"Standard deviation: {np.std(estimated_angles):.2f}")
        print(f"Variance: {np.var(estimated_angles):.2f}")
        estimated_angles.clear()

if __name__ == "__main__":
    angles = [0, 36, 72, 108, 144, 180]
    compute_statistics()
    
    for angle in angles:
        bin_files = glob.glob(f"output/{angle}/*.bin")
        first_bin_file = bin_files[0]
        file_name = os.path.splitext(os.path.basename(first_bin_file))[0]
        sample_period, data = raspi_import(f"output/{angle}", file_name)
        d = delays(sample_period, data)
        print(angle)
        estimate_angle(d)
    