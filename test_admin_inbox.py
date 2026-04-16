import os, sys
sys.path.insert(0, r"c:\Users\gthsb\OneDrive\Desktop\antpro")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evtrust.settings")
import django
django.setup()
from django.test import RequestFactory
from marketplace.views import admin_inbox
from marketplace.models import User
from django.contrib.messages.storage.fallback import FallbackStorage

def test():
    admin = User.objects.filter(is_superuser=True).first()
    factory = RequestFactory()
    request = factory.get('/admin-dashboard/inbox/')
    request.user = admin
    # Add messages middleware
    from django.contrib.sessions.backends.db import SessionStore
    request.session = SessionStore()
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    try:
        response = admin_inbox(request)
        print("Success! Response length:", len(response.content))
    except Exception as e:
        import traceback
        traceback.print_exc()

test()
