import pandas as pd
import numpy as np

df = pd.read_csv(r'c:\Users\gthsb\OneDrive\Desktop\pro\battery_cycles\01174.csv')
current = df['Current_measured'].values
time = df['Time'].values
voltage = df['Voltage_measured'].values

mask = (np.isfinite(current)) & (np.isfinite(time)) & (np.isfinite(voltage))
current, time, voltage = current[mask], time[mask], voltage[mask]

# Try different cutoffs
for cutoff in [2.7, 2.8, 3.0, 3.2, 3.5]:
    c_mask = (voltage[:-1] > cutoff) & (current[:-1] > 0.1)
    dt = np.diff(time)[c_mask]
    cap = np.sum(current[:-1][c_mask] * dt) / 3600.0
    print(f"Cutoff {cutoff}V: Capacity = {cap:.4f} Ah | SOH = {(cap/2.0)*100:.2f}%")

print(f"\nTarget Capacity: 1.6042 Ah (80.21%)")
