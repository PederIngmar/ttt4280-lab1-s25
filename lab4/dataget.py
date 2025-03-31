import numpy as np
import matplotlib.pyplot as plt
import paramiko
import os
from datetime import datetime
from scipy.signal import detrend
import calculations as calc

hostname = 'ubuntupi.local'
username = 'peder'
password = 'kristian'

def download_file(file_name):
    remote_file = f"lab4/{file_name}.bin"
    local_dir = f"output"
    local_file = f"{local_dir}/{file_name}.bin"
    
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    try:
        local_output_dir = os.path.dirname(local_file)
        if local_output_dir and not os.path.exists(local_output_dir):
            os.makedirs(local_output_dir)

        transport = paramiko.Transport((hostname, 22))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_file, local_file)
        print(f"File downloaded successfully to {local_file}")
        
        # Delete the remote file
        sftp.remove(remote_file)
        print(f"Remote file {remote_file} deleted successfully")
        
        sftp.close()
        transport.close()
    except Exception as e:
        print(f"Error: {e}")


def sample_adc(file_name):
    samples = 31250
    command = f'sudo ./lab4/adc_sampler {samples} ./lab4/{file_name}.bin'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)

    try:
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode('utf-8'))
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        client.close()


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

def plot(file_name, data):
    """
    Plot data from `raspi_import` for channels 4 and 5 in the same plot.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    total_samples = data.shape[0]
    time_axis = np.linspace(0, 1, total_samples)

    for i in range(3, 5):  # Channels 4 and 5 (indices 3 and 4)
        detrended_data = detrend(data[:, i])
        ax.plot(time_axis[250:], detrended_data[250:], label=f'adc {i+1}')
       
    
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('ADC Value')
    ax.set_xlim(0, 1)  # Set xlim to zoom in
    ax.legend()
    ax.set_title('Sampled signal through ADCs 4 and 5')

    output_dir = f'plots'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    plt.savefig(os.path.join(output_dir, f'{file_name}.png'))
    plt.show()


if __name__ == "__main__":
    timestamp = datetime.now().strftime('d-%H.%M.%S')
    file_name = f"{timestamp}"
    sample_adc(file_name)
    download_file(file_name)

    sample_period, data = raspi_import(file_name)
    data = detrend(data, axis=0)
    print(f"Sample period: {sample_period}")
    print(f"Data shape: {data.shape}")
    plot(file_name, data)
    fft_result, freqs = calc.calculate_doppler(sample_period, data)
    calc.plot(fft_result)
    
    max_index = np.argmax(np.abs(fft_result))
    max_frequency = freqs[max_index]
    max_amplitude = np.abs(fft_result[max_index])

    print(f"Max frequency: {max_frequency} Hz")
    print(f"Max amplitude: {max_amplitude}")

    c = 3e8
    f_0 = 24.13e9

    doppler_shift = max_frequency
    v = doppler_shift * c / (2 * f_0)

    print(f"Measured speed: {v} m/s")
