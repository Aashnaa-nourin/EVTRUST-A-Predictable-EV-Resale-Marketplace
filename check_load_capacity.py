import pandas as pd
import numpy as np

df = pd.read_csv('media/battery_csvs/01174.csv')
current_load = df['Current_load'].values
time = df['Time'].values

mask = np.isfinite(current_load) & np.isfinite(time)
current_load, time = current_load[mask], time[mask]
dt = np.diff(time)

capacity_load = np.sum(np.abs((current_load[:-1] + current_load[1:]) / 2.0 * dt)) / 3600.0

print(f"Capacity (unfiltered Current_load): {capacity_load:.4f} Ah")

# Try filtering for Discharge phase only (Current_load > 0 and Voltage drops)
v = df['Voltage_measured'].values
discharge_phase = (current_load > 0.1) & (v > 2.7)
mask = discharge_phase[:-1]
cap_filtered = np.sum(np.abs(current_load[:-1][mask]) * dt[mask]) / 3600.0

print(f"Capacity (Filtered Discharge):     {cap_filtered:.4f} Ah")
print(f"Target Capacity for 80.21% SOH:   1.6042 Ah")
