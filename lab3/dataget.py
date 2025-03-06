import numpy as np
import matplotlib.pyplot as plt
import paramiko
import os
from datetime import datetime
from scipy.signal import detrend

hostname = 'ubuntupi.local'
username = 'peder'
password = 'kristian'

def download_file(file_name):
    remote_file = f"lab3/{file_name}.mp4"
    local_dir = f"output"
    local_file = f"{local_dir}/{file_name}.mp4"
    
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

def rpi_record_video_upgrade(file_name):
    command = f'python ./lab3/record_video_upgrade.py ./lab3/{file_name}.mp4'

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


def video():
    timestamp = datetime.now().strftime('d-%H.%M.%S')
    file_name = f"{timestamp}"
    rpi_record_video_upgrade(file_name)
    download_file(file_name)
    return file_name

if __name__ == "__main__":
    file_name = video()