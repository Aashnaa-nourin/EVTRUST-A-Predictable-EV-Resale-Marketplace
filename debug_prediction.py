import os
import sys
import logging

# Log to console
logging.basicConfig(level=logging.INFO)

from utils.predictor import predict_battery_health

csv_path = os.path.abspath('media/battery_csvs/01174.csv')
print(f"Testing prediction for: {csv_path}")

try:
    result = predict_battery_health(csv_path)
    print("\nRESULT:")
    print(result)
except Exception as e:
    import traceback
    traceback.print_exc()
