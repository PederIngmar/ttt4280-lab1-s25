import csv
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
import sys

def raspi_import(path, channels=5):
    """
    Import data produced using adc_sampler.c.

    Returns sample period and a (samples, channels) float64 array of
    sampled data from all channels channels.

    Example (requires a recording named foo.bin):
    

>>> from raspi_import import raspi_import
    >>> sample_period, data = raspi_import('foo.bin')
    >>> print(data.shape)
    (31250, 5)
    >>> print(sample_period)
    3.2e-05


    """

    with open(path, 'r') as fid:
        sample_period = np.fromfile(fid, count=1, dtype=float)[0]
        data = np.fromfile(fid, dtype='uint16').astype('float64')
        # The "dangling" .astype('float64') casts data to double precision
        # Stops noisy autocorrelation due to overflow
        data = data.reshape((-1, channels))

    # sample period is given in microseconds, so this changes units to seconds
    sample_period *= 1e-6
    return sample_period, data


# Import data from bin file
if __name__ == "__main__":
    sample_period, data = raspi_import(sys.argv[1] if len(sys.argv) > 1
            else 'output\hundreHz.bin')


#################################################################################################

data = signal.detrend(data,axis = 0) #Fjerner DC-komponenten
data *= 0.8e-3 #Konverterer til volt
data_single = data[:, 4] #Velger kun den første kanalen


#Generate time axis
num_of_samples = data_single.shape[0]
t = np.linspace(start=0, stop=num_of_samples*sample_period, num=num_of_samples)

#Generate frequency axis and take FFT
freq = np.fft.fftfreq(n=num_of_samples, d=sample_period)
spectrum = np.fft.fft(data_single)

#Hanning window
vindu = np.hanning(num_of_samples)
vindu_data = data_single * vindu
zero_padding_factor = 10
n_padded = len(vindu_data) * zero_padding_factor
vindu_data_padded = np.pad(vindu_data, (0, n_padded - len(vindu_data)), mode='constant')

data_single_padded = np.pad(data_single, (0, n_padded - len(data_single)), mode='constant')

#Compute FFT's
FFT_without_padding_or_window = np.fft.fft(data_single)
FFT_vindu = np.fft.fft(vindu_data_padded)
FFT_data_single_padded = np.fft.fft(data_single_padded)

#Frequency axis for zero-padded data
freq_padded = np.fft.fftfreq(n=n_padded, d=sample_period)

#Normalizing the FFT without padding or window:
FFT_mag_without_padding_or_window = abs(FFT_without_padding_or_window)
FFT_mag_dB_without_padding_or_window = 20*np.log10(FFT_mag_without_padding_or_window)
FFT_mag_dB_normalized_without_padding_or_window = FFT_mag_dB_without_padding_or_window - np.max(FFT_mag_dB_without_padding_or_window)


#Normalizing the windowed_data_padded FFT:
S_vindu = 20*np.log10(abs(FFT_vindu)/np.max(abs(FFT_vindu)))

#Normalizing the data_single_padded FFT:
FFT_mag_data_single_padded = abs(FFT_data_single_padded)
FFT_mag_dB_data_single_padded = 20*np.log10(FFT_mag_data_single_padded)
FFT_mag_dB_normalized_data_single_padded = FFT_mag_dB_data_single_padded - np.max(FFT_mag_dB_data_single_padded)


# Now we can plot, only the positive frequencies:
plt.plot(freq_padded[:n_padded//2], S_vindu[:n_padded//2], label='Med hanning-vindu', color = 'Blue')
#plt.plot(freq_padded[:n_padded//2], FFT_mag_dB_normalized_data_single_padded[:n_padded//2], label='Uten hanning-vindu', color = 'Orange')
plt.xlabel('Frekvens [Hz]')
plt.ylabel('Normalisert amplitude [dB]')
plt.xlim(50, 150)
plt.ylim(-120, 0)
plt.axhline(y=-90, color='red', linestyle='dotted', label='y = -90 dB') 
plt.legend()
plt.grid()
plt.show()

############################################################################################

# Plotting the time-domain signal for all channels
fig, axs = plt.subplots(5, 1, sharex=True, figsize=(10, 8))
for i, ax in enumerate(axs):
    ax.plot(t, data[:, i])
    ax.set_title(f'ADC {i}')
axs[-1].set_xlabel('Tid [s]')
axs[2].set_ylabel('Amplitude [V]')
plt.xlim(0, 0.1)
plt.tight_layout()
plt.show()

############################################################################################

#Plotting the frequency spectrum without padding or windows:

plt.plot(freq[:num_of_samples//2], FFT_mag_dB_normalized_without_padding_or_window[:num_of_samples//2], color='Purple')
plt.title('Frekvensspektrum til 100 Hz sinussignal, ADC 4')
plt.xlabel('Frekvens [Hz]')
plt.ylabel('Normalisert amplitude [dB]')
plt.xlim(0, 200)
plt.ylim(-120, 10)
plt.legend()
plt.grid()
plt.show()
