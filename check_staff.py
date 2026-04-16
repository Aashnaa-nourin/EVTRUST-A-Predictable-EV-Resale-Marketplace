import os, sys
sys.path.insert(0, r"c:\Users\gthsb\OneDrive\Desktop\antpro")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evtrust.settings")
import django
django.setup()
from marketplace.models import User

def check():
    for u in User.objects.filter(is_superuser=True):
        print(f"User: {u.email}, is_staff: {u.is_staff}, is_superuser: {u.is_superuser}")

check()
