import os
import pandas as pd
import numpy as np
import tensorflow as tf

def preprocess_and_predict(csv_path):
    print("Loading model...")
    model_path = 'evtrust_model (1).h5'
    BATTERY_MODEL = tf.keras.models.load_model(model_path, compile=False)
    
    print("Loading CSV...")
    df = pd.read_csv(csv_path)
    df_subset = df.head(20)
    features = []
    
    for index, row in df_subset.iterrows():
        timestep_features = []
        for i, col in enumerate(df_subset.columns):
            val_str = str(row[col]).strip()
            if val_str.startswith('(') and val_str.endswith(')'):
                val_str = val_str[1:-1]
            try:
                c_val = complex(val_str)
            except ValueError:
                c_val = complex(0)
            
            timestep_features.append(c_val.real)
            if i < 4:
                timestep_features.append(c_val.imag)
                
        features.append(timestep_features)

    while len(features) < 20:
        features.append([0.0] * 9)

    print("Executing prediction...", len(features), len(features[0]))
    input_data = np.array([features], dtype=np.float32)
    prediction = BATTERY_MODEL.predict(input_data)
    
    predicted_value = float(prediction[0][0])
    print(f"Raw predicted value: {predicted_value}")

preprocess_and_predict('media/battery_csvs/07443.csv')
