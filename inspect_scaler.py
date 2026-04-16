import joblib
import pandas as pd

try:
    scaler = joblib.load('c:/Users/gthsb/OneDrive/Desktop/antpro/scaler (2).pkl')
    print("Scaler loaded successfully.")
    
    if hasattr(scaler, 'feature_names_in_'):
        print("\nFeature Names:")
        for i, name in enumerate(scaler.feature_names_in_):
            print(f"{i}: {name}")
    else:
        print("\nScaler does not have feature_names_in_ attribute.")
        print(f"Number of features: {scaler.n_features_in_}")

except Exception as e:
    print(f"Error: {e}")
