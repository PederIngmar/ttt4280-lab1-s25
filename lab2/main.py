from datetime import datetime
import raspi_import as rpi
import os

def sample_and_download(angle):
    """
    Sample ADC data, download it, and plot the results.
    """
    inputdir = f"data/{angle}"
    outdir = f"plots/{angle}"
    
    os.makedirs(inputdir, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)

    filename = datetime.now().strftime("%Y%m%d_%H%M%S")

    rpi.remote_sample_adc(filename)
    rpi.download_file(inputdir, inputdir, filename, filename)
    return filename

if __name__ == "__main__":
    angle = 0
    local_dir = f"data/{angle}"
    filename = sample_and_download(angle)
    filename, data = rpi.import_latest_file(local_dir)
    rpi.plot(local_dir, filename, data)