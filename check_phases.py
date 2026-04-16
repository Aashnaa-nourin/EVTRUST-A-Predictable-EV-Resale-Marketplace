import pandas as pd
import numpy as np

df = pd.read_csv('media/battery_csvs/01174.csv')
current = df['Current_measured'].values
time = df['Time'].values

mask = np.isfinite(current) & np.isfinite(time)
current, time = current[mask], time[mask]
dt = np.diff(time)

# Discharge Only (Current < 0)
discharge_mask = current[:-1] < 0
cap_discharge = np.sum(np.abs(current[:-1][discharge_mask]) * dt[discharge_mask]) / 3600.0

# Charge Only (Current > 0)
charge_mask = current[:-1] > 0
cap_charge = np.sum(np.abs(current[:-1][charge_mask]) * dt[charge_mask]) / 3600.0

print(f"Discharge Capacity: {cap_discharge:.4f} Ah")
print(f"Charge Capacity:    {cap_charge:.4f} Ah")
print(f"Total Abs Capacity: {cap_discharge + cap_charge:.4f} Ah")

print(f"\nSOH at 2.0 Ah (Discharge Only): {(cap_discharge / 2.0) * 100:.2f}%")
print(f"SOH at 2.2 Ah (Discharge Only): {(cap_discharge / 2.2) * 100:.2f}%")
