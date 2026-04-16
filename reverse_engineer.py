import pandas as pd
import numpy as np
import json

df = pd.read_csv("media/battery_csvs/07443.csv")
out = {}
for col in df.columns:
    reals = []
    imags = []
    abss = []
    phases = []
    for val_str in df[col].dropna():
        val_str = str(val_str).strip()
        if val_str.startswith('(') and val_str.endswith(')'):
            val_str = val_str[1:-1]
        try:
            c = complex(val_str)
            reals.append(c.real)
            imags.append(c.imag)
            abss.append(abs(c))
            phases.append(np.angle(c))
        except:
            pass
            
    if len(reals) > 0:
        out[col] = {
            "Real_min": min(reals), "Real_max": max(reals),
            "Imag_min": min(imags), "Imag_max": max(imags),
            "Abs_min": min(abss), "Abs_max": max(abss),
            "Phase_min": min(phases), "Phase_max": max(phases)
        }

with open("csv_ranges.json", "w") as f:
    json.dump(out, f, indent=4)
