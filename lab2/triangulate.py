import numpy as np 
import os

angle = ""


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

if __name__ == "__main__":
    path = "output/0"
    file_name = "d-19.06.35"
    sample_period, data = raspi_import(path, file_name)
    delays(sample_period, data)
  