import numpy as np 
import os
import glob


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

    D = {}
    channel_pairs = [(0, 1), (1, 2), (0, 2)]
    sampling_f = 1 / sample_period
    for cpair in channel_pairs:
        crosscorrelation = np.abs(np.correlate(data[:, cpair[0]], data[:, cpair[1]], mode='full'))
        lags = np.arange(-len(data)+1, len(data))
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

def delay_calculations(all_delays):
    # Calculate average delays
    avg_delays = {}
    for cpair in all_delays[0].keys():
        avg_delays[cpair] = np.mean([d[cpair] for d in all_delays])

    # Calculate variance of delays
    var_delays = {}
    for cpair in all_delays[0].keys():
        var_delays[cpair] = np.var([d[cpair] for d in all_delays])

    # Calculate standard deviation of delays
    std_delays = {}
    for cpair in all_delays[0].keys():
        std_delays[cpair] = np.std([d[cpair] for d in all_delays])

    return avg_delays, std_delays


def estimate_angle(all_delays):
    d = 6 #cm
    delays = all_delays
    placements = [[], [], []]


if __name__ == "__main__":
    path = "output/0"
    file_name = "d-19.47.30"
    
    angles = [0, 36, 72, 108, 144, 180]
    for angle in angles:
        ad = all_delays(angle)
        avg, std = delay_calculations(ad)