import os
import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import detrend

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

    output_dir = f'plots'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    plt.savefig(os.path.join(output_dir, f'{file_name}.png'))
    #plt.show()

