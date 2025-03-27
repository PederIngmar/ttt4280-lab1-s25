import numpy as np
import os
from scipy.signal import detrend

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


if __name__ == "__main__":
    sample_period, data = raspi_import("d-16.06.57")
    print(f"Sample period: {sample_period}")
    print(f"Data shape: {data.shape}")

    # Detrend the data
    detrended_data = detrend(data, axis=0)
    