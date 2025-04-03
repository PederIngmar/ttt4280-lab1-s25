import numpy as np 
import os
import glob
from scipy.signal import detrend
import raspi_import as rpi
import matplotlib.pyplot as plt

def delays(sample_period, data):
    if data is None:
        return None
    data = data[:, 2:]
    D = {}
    channel_pairs = [(0, 1), (1, 2), (0, 2)]
    sampling_f = 1 / sample_period

    upsample_factor = 10
    for cpair in channel_pairs:
        d1 = data[:, cpair[0]]
        d2 = data[:, cpair[1]]

        #peak_idx = np.argmax(np.abs(d1))
        #start = max(0,peak_idx-1000)
        #end = min(len(d1),peak_idx+1000)
        #d1_window = d1[start:end]
        #d2_window = d2[start:end]

        crosscorrelation = np.abs(np.correlate(d1, d2, mode='full'))
        lags = np.arange(-len(d1)+1, len(d1))

        max_lag = lags[np.argmax(crosscorrelation)]
        delta_t = max_lag / sampling_f
        D[cpair] = delta_t

    return D


def all_delays(sample_period, data_list):
    for data in data_list:
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
    t12 = delays[(1, 2)]
    t13 = delays[(0, 1)]
    t23 = delays[(0, 2)]

    x = (t13 - t12 + 2*t23)
    y = (t13 + t12)

    if x < 0:
        formel = "x<0"
        theta = np.arctan2(np.sqrt(3)* y, x) + np.pi
    elif x == 0:
        formel = "x = 0"
        theta = -np.pi/2
    else:
        formel = "x > 0"
        theta = np.arctan2(np.sqrt(3)* y, x)

    cali_factor = 0
    theta_deg = np.degrees(theta) + cali_factor

    print(f"Estimated angle: {theta_deg:.2f} degrees, with formula: {formel}")
    print(f"t12: {t12:.2f}, t13: {t13:.2f}, t23: {t23:.2f}")
    return theta_deg




if __name__ == "__main__":
    angles = [0, 36, 75, 110]
    for angle in angles:
        input_dir = f"data/{angle}"
        datas = rpi.import_all_files(input_dir)
        for data in datas:
            d = delays(31250, data)
            print(angle)
            estimate_angle(d)


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
            sample_period, data = rpi.raspi_import(f"output/{angle}", file_name)
            d = delays(sample_period, data)
            estimated_angles.append(estimate_angle(d))
        print(f"Mean: {np.mean(estimated_angles):.2f}")
        print(f"Standard deviation: {np.std(estimated_angles):.2f}")
        print(f"Variance: {np.var(estimated_angles):.2f}")
        estimated_angles.clear()
