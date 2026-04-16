import pandas as pd
import numpy as np
import os

folder = r'c:\Users\gthsb\OneDrive\Desktop\pro\battery_cycles'
target_cap = 1.6042

if not os.path.exists(folder):
    print(f"Folder not found: {folder}")
else:
    for file in os.listdir(folder):
        if file.endswith('.csv'):
            try:
                df = pd.read_csv(os.path.join(folder, file))
                current = df['Current_measured'].values
                time = df['Time'].values
                mask = np.isfinite(current) & np.isfinite(time)
                current, time = current[mask], time[mask]
                dt = np.diff(time)
                cap = np.sum(np.abs((current[:-1] + current[1:]) / 2.0 * dt)) / 3600.0
                
                if abs(cap - target_cap) < 0.01:
                    print(f"MATCH: {file} | Capacity: {cap:.4f}")
            except:
                pass
