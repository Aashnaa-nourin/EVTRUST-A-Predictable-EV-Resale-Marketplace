"""
model_loader.py
---------------
Singleton pattern for loading the Keras model and scalers ONCE at startup.
"""

import os
import logging

logger = logging.getLogger(__name__)

# -- Singleton holders --
_battery_model = None
_feature_scaler = None
_nasa_scaler = None
_soh_scaler = None

# -- Path constants --
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH          = os.path.join(BASE_DIR, 'best_evtrust_model.h5')
FEATURE_SCALER_PATH = os.path.join(BASE_DIR, 'scaler (2).pkl')  # Impedance Scaler
NASA_SCALER_PATH    = os.path.join(BASE_DIR, 'scaler_nasa.pkl')  # NASA Telemetry Scaler
SOH_SCALER_PATH     = os.path.join(BASE_DIR, 'scaler_soh.pkl')


def get_model():
    global _battery_model
    if _battery_model is not None: return _battery_model
    try:
        import tensorflow as tf
        if not os.path.exists(MODEL_PATH): return None
        _battery_model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        return _battery_model
    except: return None


def get_feature_scaler():
    """Returns the Impedance feature scaler."""
    global _feature_scaler
    if _feature_scaler is not None: return _feature_scaler
    try:
        import joblib
        if os.path.exists(FEATURE_SCALER_PATH):
            _feature_scaler = joblib.load(FEATURE_SCALER_PATH)
            return _feature_scaler
    except: return None


def get_nasa_scaler():
    """Returns the NASA Telemetry feature scaler (10 inputs: 9 features + SOH)."""
    global _nasa_scaler
    if _nasa_scaler is not None: return _nasa_scaler
    try:
        import joblib
        if os.path.exists(NASA_SCALER_PATH):
            _nasa_scaler = joblib.load(NASA_SCALER_PATH)
            return _nasa_scaler
    except: return None


def get_soh_scaler():
    global _soh_scaler
    if _soh_scaler is not None: return _soh_scaler
    try:
        import joblib
        if os.path.exists(SOH_SCALER_PATH):
            _soh_scaler = joblib.load(SOH_SCALER_PATH)
            return _soh_scaler
    except: return None
