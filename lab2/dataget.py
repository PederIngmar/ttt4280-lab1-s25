import numpy as np
import matplotlib.pyplot as plt
import paramiko
import os
from datetime import datetime
from scipy.signal import detrend

hostname = 'ubuntupi.local'
username = 'peder'
password = 'kristian'
angle = "144"

def download_file(file_name):
    remote_file = f"lab1/{file_name}.bin"
    local_dir = f"output/{angle}"
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
        sftp.close()
        transport.close()
    except Exception as e:
        print(f"Error: {e}")

def sample_adc(file_name):
    samples = 31250
    command = f'sudo ./lab1/adc_sampler {samples} ./lab1/{file_name}.bin'

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

def sampel_data():
    timestamp = datetime.now().strftime('d-%H.%M.%S')
    file_name = f"{timestamp}"
    sample_adc(file_name)
    download_file(file_name)
    return file_name

def raspi_import(file_name, channels=5):
    dir = f"output/{angle}"

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
    Plot data from `raspi_import` in a 5x1 grid.
    """
    fig, axs = plt.subplots(5, 1, sharex=True, figsize=(10, 8))
    
    total_samples = data.shape[0]
    time_axis = np.linspace(0, 1, total_samples)

    for i, ax in enumerate(axs):
        detrended_data = detrend(data[:, i])
        ax.plot(time_axis[250:], detrended_data[250:])
        ax.set_ylabel(f'adc {i+1}')
        ax.set_xlim(0, 1)  # Set xlim to zoom in

    axs[-1].set_xlabel('Time (s)')
    fig.suptitle('Sampled signal through 5 ADCs')

    output_dir = f'plots/{angle}'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    plt.savefig(os.path.join(output_dir, f'{file_name}.png'))
    #plt.show()


if __name__ == "__main__":
    for i in range(7):
        file_name = sampel_data()
        sample_period, data = raspi_import(file_name)
        plot(file_name, data)