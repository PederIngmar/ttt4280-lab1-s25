import numpy as np 
import os

angle = ""


def raspi_import(file_name, channels=5):
    path = f"/output/{file_name}.bin"

    with open(path, 'r') as fid:
        sample_period = np.fromfile(fid, count=1, dtype=float)[0]
        data = np.fromfile(fid, dtype='uint16').astype('float64')
        # The "dangling" `.astype('float64')` casts data to double precision
        # Stops noisy autocorrelation due to overflow
        data = data.reshape((-1, channels))

    # sample period is given in microseconds-changes units to seconds
    sample_period *= 1e-6
    return sample_period, data


def average_signals(folder_name):
    all_data = []
    for file_name in os.listdir(folder_name):
        if file_name.endswith('.bin'):
            sample_period, data = raspi_import(os.path.join(folder_name, file_name))
            all_data.append(data)
    
    if all_data:
        avg_data = np.mean(all_data, axis=0)
        return avg_data
    else:
        return None

if __name__ == "__main__":
    folder_name = "output"
    avg_data = average_signals()
  