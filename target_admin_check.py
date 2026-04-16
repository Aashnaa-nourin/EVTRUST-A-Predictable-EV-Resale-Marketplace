import os, sys
sys.path.insert(0, r"c:\Users\gthsb\OneDrive\Desktop\antpro")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evtrust.settings")
import django
django.setup()
from marketplace.models import User
from django.db.models import Q

def check():
    print("SEARCH RESULTS:")
    admins = User.objects.filter(Q(email__icontains='admin') | Q(is_staff=True) | Q(is_superuser=True))
    for u in admins:
        print(f"ID: {u.id} | Email: {u.email} | Staff: {u.is_staff} | Super: {u.is_superuser}")

if __name__ == "__main__":
    check()
