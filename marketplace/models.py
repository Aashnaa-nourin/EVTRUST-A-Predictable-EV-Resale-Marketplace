from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('seller', 'Seller'),
        ('buyer', 'Buyer'),
    )
    ACCOUNT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('blocked', 'Blocked'),
    )

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    account_status = models.CharField(max_length=10, choices=ACCOUNT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return f"{self.name} ({self.role})"


class EVListing(models.Model):
    LISTING_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('pending_sale', 'Pending Sale'),  # locked while purchase is under admin review
        ('sold', 'Sold'),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ev_listings', limit_choices_to={'role': 'seller'})
    vehicle_model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mileage = models.PositiveIntegerField(help_text="Mileage in km")
    battery_capacity = models.PositiveIntegerField(help_text="Battery capacity in kWh")
    description = models.TextField()
    vehicle_image = models.ImageField(upload_to='ev_images/', blank=True, null=True)
    listing_status = models.CharField(max_length=15, choices=LISTING_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def display_name(self):
        if self.vehicle_model.lower().startswith(self.manufacturer.lower()):
            # Fallback if the user typed "MG ZS EV" instead of just "ZS EV"
            return self.vehicle_model
        return f"{self.manufacturer} {self.vehicle_model}"

    def __str__(self):
        return f"{self.manufacturer} {self.vehicle_model} ({self.year})"


class BatteryData(models.Model):
    PREDICTION_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    ev_id = models.ForeignKey(EVListing, on_delete=models.CASCADE, related_name='battery_data')
    csv_file = models.FileField(upload_to='battery_csvs/')
    upload_date = models.DateTimeField(auto_now_add=True)
    soh_prediction = models.FloatField(blank=True, null=True, help_text="State of Health as a percentage")
    rul_prediction = models.FloatField(blank=True, null=True, help_text="Remaining Useful Life in years")
    prediction_status = models.CharField(max_length=10, choices=PREDICTION_STATUS_CHOICES, default='pending')
    purchase_enabled = models.BooleanField(default=False, help_text="True only when prediction is successfully completed")

    def __str__(self):
        return f"Battery Data for EV {self.ev_id.id}"


class Message(models.Model):
    ev = models.ForeignKey(EVListing, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        ev_name = self.ev.vehicle_model if self.ev else "General Support"
        return f"Message from {self.sender.name} to {self.receiver.name} regarding {ev_name}"


class PurchaseRequest(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('seller_confirmed', 'Seller Confirmed'),
        ('under_review', 'Under Admin Review'),
        ('invoice_sent', 'Invoice Sent'),
        ('payment_submitted', 'Payment Submitted'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    )

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_requests')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sale_requests')
    listing = models.ForeignKey(EVListing, on_delete=models.CASCADE, related_name='purchase_requests')
    request_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Purchase Request #{self.id} by {self.buyer.name} for {self.listing}"
