import pandas as pd
import numpy as np

df = pd.read_csv(r'c:\Users\gthsb\OneDrive\Desktop\pro\battery_cycles\01174.csv')
current = df['Current_measured'].values
time = df['Time'].values

mask = (np.isfinite(current)) & (np.isfinite(time))
current, time = current[mask], time[mask]
dt = np.diff(time)

# High threshold to avoid noise
threshold = 0.5
c_mask = np.abs(current[:-1]) > threshold
cap = np.sum(np.abs(current[:-1][c_mask]) * dt[c_mask]) / 3600.0

print(f"Capacity (>0.5A): {cap:.4f} Ah")
print(f"SOH (at 2.0 Ah): {(cap / 2.0) * 100:.2f}%")
print(f"Difference from 80.21%: {((cap/2.0)*100) - 80.21:.2f}%")
