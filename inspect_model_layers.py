import tensorflow as tf
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
try:
    model = tf.keras.models.load_model('c:/Users/gthsb/OneDrive/Desktop/antpro/best_evtrust_model.h5', compile=False)
    print("Layer Names:")
    for layer in model.layers:
        print(f"- {layer.name} ({type(layer).__name__})")
        if hasattr(layer, 'input_shape'):
             print(f"  Input: {layer.input_shape}")
except Exception as e:
    print(f"Error: {e}")
