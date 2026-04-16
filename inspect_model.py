import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
try:
    import tensorflow as tf
except ImportError:
    print("TensorFlow is not installed.")
    import sys
    sys.exit(1)

model_path = 'evtrust_model (1).h5'
try:
    model = tf.keras.models.load_model(model_path, compile=False)
    print("Model loaded successfully.")
    print("--- Model Summary ---")
    model.summary()
    print("--- Input Shape ---")
    for i, input_tensor in enumerate(model.inputs):
        print(f"Input {i}: shape={input_tensor.shape}, dtype={input_tensor.dtype}")
    print("--- Output Shape ---")
    for i, output_tensor in enumerate(model.outputs):
        print(f"Output {i}: shape={output_tensor.shape}, dtype={output_tensor.dtype}")
except Exception as e:
    print(f"Error loading model: {e}")
