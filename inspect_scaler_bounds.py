import joblib
import numpy as np

try:
    scaler = joblib.load('c:/Users/gthsb/OneDrive/Desktop/antpro/scaler (2).pkl')
    print(f"Scaler loaded. Number of features: {scaler.n_features_in_}")
    
    print("\nMin values per feature:")
    print(scaler.data_min_)
    
    print("\nMax values per feature:")
    print(scaler.data_max_)

except Exception as e:
    print(f"Error: {e}")
