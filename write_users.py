import os, sys
sys.path.insert(0, r"c:\Users\gthsb\OneDrive\Desktop\antpro")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evtrust.settings")
import django
django.setup()
from marketplace.models import User

with open("user_list_all.txt", "w") as f:
    f.write("User Audit Log:\n")
    for u in User.objects.all():
        f.write(f"ID: {u.id} | Email: {u.email} | Staff: {u.is_staff} | Super: {u.is_superuser}\n")
