import numpy as np
import sys
import matplotlib.pyplot as plt
import paramiko
import os
from datetime import datetime

hostname = 'ubuntupi.local'
username = 'peder'
password = 'kristian'


def download_file(file_name):
    remote_file = f"lab1/{file_name}"
    local_file = f"output/{file_name}"
    try:
        # Ensure output directory exists
        local_output_dir = os.path.dirname(local_file)
        if local_output_dir and not os.path.exists(local_output_dir):
            os.makedirs(local_output_dir)

        # Establish transport with hostname and port
        transport = paramiko.Transport((hostname, 22))  # Ensure port is provided
        transport.connect(username=username, password=password)

        # Create SFTP client
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Download file
        sftp.get(remote_file, local_file)
        print(f"File downloaded successfully to {local_file}")

        # Close connections
        sftp.close()
        transport.close()

    except Exception as e:
        print(f"Error: {e}")

def sample_adc(file_name):
    samples = 31250
    command = f'sudo ./lab1/adc_sampler {samples} ./lab1/{file_name}'

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



def sampel_data(channels=5):
    timestamp = datetime.now().strftime('d-%H.%M.%S')
    file_name = f"{timestamp}.bin"

    sample_adc(file_name)
    download_file(file_name)

    path = f"output/{file_name}"
    with open(path, 'r') as fid:
        sample_period = np.fromfile(fid, count=1, dtype=float)[0]
        data = np.fromfile(fid, dtype='uint16').astype('float64')
        # The "dangling" `.astype('float64')` casts data to double precision
        # Stops noisy autocorrelation due to overflow
        data = data.reshape((-1, channels))

    # sample period is given in microseconds, so this changes units to seconds
    sample_period *= 1e-6
    return sample_period, data


def plot(data):
    """
    Plot data from `raspi_import` in a 5x1 grid.
    """
    fig, axs = plt.subplots(5, 1, sharex=True, figsize=(10, 8))
    
    for i, ax in enumerate(axs):
        ax.plot(data[:, i])
        ax.set_ylabel(f'Ch {i}')
    axs[-1].set_xlabel('Sample')
    plt.savefig('plot.png')



# Import data from bin file
if __name__ == "__main__":
    sample_period, data = sampel_data()
    plot(data)
