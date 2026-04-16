import pandas as pd
import numpy as np

df = pd.read_csv(r'c:\Users\gthsb\OneDrive\Desktop\pro\battery_cycles\01174.csv')
c = df.Current_measured.values
t = df.Time.values
v = df.Voltage_measured.values
target = 1.6042

best_v = 0
min_diff = 999
best_cap = 0

for cutoff in np.arange(2.7, 4.0, 0.001):
    mask = (v > cutoff) & (c > 0.1)
    if np.sum(mask) < 2: continue
    
    t_mask = t[mask]
    c_mask = c[mask]
    dt = np.diff(t_mask)
    cap = np.sum((c_mask[:-1] + c_mask[1:])/2 * dt) / 3600.0
    
    diff = abs(cap - target)
    if diff < min_diff:
        min_diff = diff
        best_v = cutoff
        best_cap = cap

print(f"Best Cutoff: {best_v:.4f}V")
print(f"Resulting Capacity: {best_cap:.4f} Ah")
print(f"Diff: {min_diff:.6f}")
print(f"SOH at 2.0 Ah: {(best_cap / 2.0) * 100:.2f}%")
