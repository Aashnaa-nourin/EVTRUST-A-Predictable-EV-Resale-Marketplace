import pandas as pd
import numpy as np

# Use the ORIGINAL desktop file
df = pd.read_csv(r'c:\Users\gthsb\OneDrive\Desktop\pro\battery_cycles\01174.csv')
current = df['Current_measured'].values
time = df['Time'].values

mask = np.isfinite(current) & np.isfinite(time)
current, time = current[mask], time[mask]
dt = np.diff(time)

# Calculate capacity with noise threshold (e.g. > 0.1A)
# In this file, positive current seems to be discharge
discharge_mask = current[:-1] > 0.1
capacity = np.sum(np.abs(current[:-1][discharge_mask]) * dt[discharge_mask]) / 3600.0

print(f"File: pro/.../01174.csv")
print(f"Capacity (Current > 0.1A): {capacity:.4f} Ah")
print(f"SOH (at 2.0 Ah): {(capacity / 2.0) * 100:.2f}%")
print(f"Target Capacity: 1.6042 Ah")
