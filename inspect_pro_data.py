import joblib

try:
    data = joblib.load('c:/Users/gthsb/OneDrive/Desktop/pro/outputs/preprocessed_data.pkl')
    print("Data loaded.")
    if isinstance(data, dict):
        print("\nKeys:", data.keys())
        if 'df_features' in data:
            print("\nColumns in df_features:")
            print(data['df_features'].columns.tolist())
        if 'scaler' in data:
            print("\nScaler features:", data['scaler'].n_features_in_)
except Exception as e:
    print(f"Error: {e}")
