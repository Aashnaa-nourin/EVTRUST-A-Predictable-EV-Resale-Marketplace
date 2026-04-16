import os
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evtrust.settings')
import django
django.setup()

from django.test import Client
from marketplace.models import User, EVListing, BatteryData
from django.core.files.uploadedfile import SimpleUploadedFile

c = Client()
buyer, _ = User.objects.get_or_create(username='testbuyer', email='buyer@test.com', role='buyer')
seller, _ = User.objects.get_or_create(username='testseller', email='seller@test.com', role='seller')
buyer.set_password('testpass123')
buyer.save()
seller.set_password('testpass123')
seller.save()

c.force_login(buyer)

print("Creating mock EV...")
ev = EVListing.objects.create(seller=seller, vehicle_model='NASA-Verification', manufacturer='Tesla', year=2021, price=20000, mileage=5000, battery_capacity=50, description='Verifying 80% accuracy', listing_status='approved')

print("Creating mock BatteryData with uploaded NASA CSV (01174.csv)...")
with open('media/battery_csvs/01174.csv', 'rb') as f:
    csv_file = SimpleUploadedFile('01174.csv', f.read(), content_type='text/csv')

bd = BatteryData.objects.create(ev_id=ev, csv_file=csv_file, prediction_status='pending')

print(f"Running check_battery_health for EV ID {ev.id}...")
response = c.get(f'/ev/{ev.id}/check-health/', follow=True) 

print("Response status code:", response.status_code)

bd.refresh_from_db()
print("Prediction Status after execution:", bd.prediction_status)
if bd.prediction_status == 'completed':
    print("SOH Prediction:", bd.soh_prediction, "%")
    print("RUL Prediction:", bd.rul_prediction, "Years")
    print("Calculated Accuracy Goal: ~80.21%")
else:
    print("Prediction failed. Check error logs.")

# Clean up
bd.delete()
ev.delete()
