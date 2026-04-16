import pandas as pd
import numpy as np

df = pd.read_csv('media/battery_csvs/01174.csv')
current = df['Current_measured'].values
time = df['Time'].values

mask = np.isfinite(current) & np.isfinite(time)
current, time = current[mask], time[mask]

dt = np.diff(time)
avg_current = np.abs((current[:-1] + current[1:]) / 2.0)
capacity_ah = np.sum(avg_current * dt) / 3600.0

print(f"File: 01174.csv")
print(f"Calculated Capacity: {capacity_ah:.4f} Ah")
print(f"SOH (at 2.0 Ah): {(capacity_ah / 2.0) * 100:.2f}%")
print(f"SOH (at 2.2 Ah): {(capacity_ah / 2.2) * 100:.2f}%")
print(f"Initial Time: {time[0]}, Final Time: {time[-1]}, Duration: {time[-1] - time[0]} s")
