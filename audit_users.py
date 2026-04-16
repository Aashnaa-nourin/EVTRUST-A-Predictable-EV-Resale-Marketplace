import os, sys
sys.path.insert(0, r"c:\Users\gthsb\OneDrive\Desktop\antpro")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evtrust.settings")
import django
django.setup()
from marketplace.models import User

def check():
    print("Listing all users with administrative potential:")
    for u in User.objects.all():
        if u.is_staff or u.is_superuser or u.is_active:
            print(f"User: {u.username} | Email: {u.email} | Staff: {u.is_staff} | Super: {u.is_superuser} | Active: {u.is_active} | Role: {u.role}")

check()
