import pandas as pd
import numpy as np
import os

folder = r'c:\Users\gthsb\OneDrive\Desktop\pro\battery_cycles'
target_soh = 74.47
target_cap = (target_soh / 100.0) * 2.0 # 1.4894

if not os.path.exists(folder):
    print(f"Folder not found: {folder}")
else:
    for file in os.listdir(folder):
        if file.endswith('.csv'):
            try:
                df = pd.read_csv(os.path.join(folder, file))
                c = df.Current_measured.values
                t = df.Time.values
                mask = np.isfinite(c) & np.isfinite(t)
                c, t = c[mask], t[mask]
                dt = np.diff(t)
                cap = np.sum(np.abs((c[:-1] + c[1:]) / 2.0 * dt)) / 3600.0
                
                # Check raw cap against target
                if abs(cap - target_cap) < 0.1: # Loose check
                    print(f"FILE: {file} | Raw SOH: {(cap/2.0)*100:.2f}% | Target: {target_soh}%")
            except:
                pass
