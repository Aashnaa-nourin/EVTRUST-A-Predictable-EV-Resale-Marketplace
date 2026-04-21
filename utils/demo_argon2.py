import os
import django

# Set up Django environment
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evtrust.settings')
django.setup()

from marketplace.models import User

def reset_and_verify():
    try:
        # Get the first user (usually the admin)
        user = User.objects.get(id=1)
        
        # This will set the password to 'password123' 
        # and use the NEWly configured Argon2 hasher
        user.set_password('password123')
        user.save()
        
        print(f"Success! User '{user.username}' password has been reset to 'password123'.")
        print(f"New hash in database now starts with: {user.password[:20]}...")
        print("\nNow, refresh your 'DB Browser for SQLite'. You will see that the hash for ID 1 has changed from 'pbkdf2_sha256' to 'argon2'!")
        
    except User.DoesNotExist:
        print("User with ID 1 not found. Please check your database.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_and_verify()
