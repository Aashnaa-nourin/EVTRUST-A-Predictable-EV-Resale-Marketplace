import os
import django
import sys
from pathlib import Path

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evtrust.settings')
django.setup()

from marketplace.models import User

def reset_all_passwords():
    print("Starting global password reset...")
    users = User.objects.all()
    count = 0
    for user in users:
        # Get username part from email (e.g. 'john' from 'john@gmail.com')
        new_password = user.email.split('@')[0]
        
        # Set and hash the password
        user.set_password(new_password)
        user.save()
        count += 1
        print(f"Updated: {user.email} -> password is now '{new_password}' (hashed with Argon2)")

    print(f"\nSuccess! Total users updated: {count}")
    print("All passwords in the database have been converted to Argon2.")

if __name__ == "__main__":
    reset_all_passwords()
