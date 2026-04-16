import os, sys
sys.path.insert(0, r"c:\Users\gthsb\OneDrive\Desktop\antpro")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evtrust.settings")
import django
django.setup()
from marketplace.models import User, Message

def check():
    supers = User.objects.filter(is_superuser=True)
    print(f"Superusers count: {supers.count()}")
    for s in supers:
        msgs = Message.objects.filter(receiver=s).count()
        print(f"Admin: {s.email} - ID: {s.id} - Messages received: {msgs}")

check()
