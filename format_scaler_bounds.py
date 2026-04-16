import joblib
import pandas as pd

try:
    scaler = joblib.load('c:/Users/gthsb/OneDrive/Desktop/antpro/scaler (2).pkl')
    df = pd.DataFrame({
        'Feature': range(scaler.n_features_in_),
        'Min': scaler.data_min_,
        'Max': scaler.data_max_
    })
    print(df.to_string(index=False))

except Exception as e:
    print(f"Error: {e}")
