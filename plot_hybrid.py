import csv
import matplotlib.pyplot as plt

# Read the CSV file
frequencies = []
magnitudes = []

with open('hybrid_pi_lawpass_network.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        frequencies.append(float(row[0]))
        magnitudes.append(float(row[1]))

# Plot the data
plt.plot(frequencies, magnitudes)
plt.xlabel('Frequency')
plt.ylabel('Magnitude (dB)')
plt.xlim(0,300)
plt.title('Frequency vs Magnitude')
plt.grid(True)
plt.show()
