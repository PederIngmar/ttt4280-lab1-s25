import csv
import matplotlib.pyplot as plt
import numpy as np

# Les CSV-filen
frequencies = []
magnitudes = []

with open('lavpassMeasurement3.0.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        frequencies.append(float(row[0]))
        magnitudes.append(float(row[1]))

# Konverter lister til numpy-arrays for enklere behandling
frequencies = np.array(frequencies)
magnitudes = np.array(magnitudes)

# Lag to subplots side om side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Venstre plott: originalplot med xlim(0, 1000)
ax1.plot(frequencies, magnitudes)
ax1.set_xlabel('Frekvens (Hz)')
ax1.set_ylabel('Amplitude (dB)')
ax1.set_xlim(0, 1000)
ax1.grid(True)

# Høyre plott: samme plot, men med xlim(0, 300)
ax2.plot(frequencies, magnitudes)
ax2.set_xlabel('Frekvens (Hz)')
ax2.set_ylabel('Amplitude (dB)')
ax2.set_xlim(0, 100)
ax2.set_ylim(-40, 10)
ax2.grid(True)

# Finn -3 dB krysningen i det høyre plottet
# Vi betrakter kun dataene der frekvensen er mellom 0 og 100 Hz
mask = (frequencies >= 0) & (frequencies <= 100)
f_mask = frequencies[mask]
m_mask = magnitudes[mask]

f_cross = None

# Gå gjennom dataene for å finne intervallet der kurven krysser -3 dB
for i in range(1, len(f_mask)):
    if m_mask[i-1] > -3 and m_mask[i] <= -3:
        # Lineær interpolasjon for å finne eksakt krysning
        f1, f2 = f_mask[i-1], f_mask[i]
        m1, m2 = m_mask[i-1], m_mask[i]
        # Interpolasjonsformel:
        f_cross = f1 + (f2 - f1) * ((-3 - m1) / (m2 - m1))
        break

# Dersom vi fant et krysningpunkt, marker det med en rød prikk og legg til legend
if f_cross is not None:
    ax2.plot(f_cross, -3, 'ro', label=f'krysning med -3 dB ved {f_cross:.1f} Hz')
    ax2.legend()

plt.tight_layout()
plt.show()


