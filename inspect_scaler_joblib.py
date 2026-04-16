import joblib
import json

try:
    scaler = joblib.load("scaler (1).pkl")
    out = {
        "type": str(type(scaler)),
        "n_features": int(getattr(scaler, "n_features_in_", getattr(scaler, "n_features_", 0))),
    }
    if hasattr(scaler, "mean_"):
        out["mean"] = scaler.mean_.tolist()
        out["scale"] = scaler.scale_.tolist()
    elif hasattr(scaler, "min_"):
        out["min"] = scaler.min_.tolist()
        out["scale"] = scaler.scale_.tolist()
        
    with open("scaler_info.json", "w") as f:
        json.dump(out, f, indent=4)
except Exception as e:
    with open("scaler_info.json", "w") as f:
        json.dump({"error": str(e)}, f)
