from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, EVListing, BatteryData

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('name', 'email', 'phone', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # AbstractUser requires a unique username
        if commit:
            user.save()
        return user

class EVListingForm(forms.ModelForm):
    class Meta:
        model = EVListing
        fields = ['vehicle_model', 'manufacturer', 'year', 'price', 'mileage', 'battery_capacity', 'description', 'vehicle_image']

class BatteryCSVForm(forms.ModelForm):
    class Meta:
        model = BatteryData
        fields = ['csv_file']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'phone']

class ContactSellerForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your message to the seller here...'}))
