from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, EVListingForm, BatteryCSVForm, EditProfileForm, ContactSellerForm
from .models import User, EVListing, BatteryData, Message, PurchaseRequest
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)


def home(request):
    """ Renders the landing page """
    if request.user.is_authenticated:
        return render(request, 'marketplace/home.html', {'is_dashboard_link': True})
    return render(request, 'marketplace/home.html', {'is_dashboard_link': False})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard_redirect')
    else:
        form = CustomUserCreationForm()
    return render(request, 'marketplace/register.html', {'form': form})

def dashboard_redirect(request):
    """ Redirects user to the correct dashboard based on role """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.role == 'seller':
        return redirect('seller_dashboard')
    elif request.user.role == 'buyer':
        return redirect('buyer_dashboard')
    else:
        return redirect('buyer_dashboard')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('dashboard_redirect')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'marketplace/edit_profile.html', {'form': form})

# --- SELLER VIEWS ---
@login_required
def seller_dashboard(request):
    if request.user.role != 'seller':
        return redirect('buyer_dashboard')
    
    listings = EVListing.objects.filter(seller=request.user)
    total_listings = listings.count()
    pending_listings = listings.filter(listing_status='pending').count()
    approved_listings = listings.filter(listing_status='approved').count()
    sold_listings = listings.filter(listing_status='sold').count()

    # Get all purchase requests for this seller's listings
    purchase_requests = PurchaseRequest.objects.filter(
        seller=request.user,
        request_status__in=['submitted', 'admin_review', 'seller_confirmed']
    ).select_related('buyer', 'listing').order_by('-created_at')

    # History of completed sales
    confirmed_sales = PurchaseRequest.objects.filter(
        seller=request.user,
        request_status='confirmed'
    ).select_related('buyer', 'listing').order_by('-created_at')

    context = {
        'total_listings': total_listings,
        'pending_listings': pending_listings,
        'approved_listings': approved_listings,
        'sold_listings': sold_listings,
        'unread_messages_count': Message.objects.filter(receiver=request.user, is_read=False).count(),
        'purchase_requests': purchase_requests,
        'confirmed_sales': confirmed_sales,
    }
    return render(request, 'marketplace/seller_dashboard.html', context)

@login_required
def seller_inbox(request):
    if request.user.role != 'seller':
        return redirect('buyer_dashboard')
    
    received_messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    received_messages.update(is_read=True)
    
    return render(request, 'marketplace/seller_inbox.html', {'inbox_messages': received_messages})

@login_required
def reply_message(request, pk):
    if request.method == 'POST':
        original_msg = get_object_or_404(Message, pk=pk, receiver=request.user)
        reply_text = request.POST.get('reply_content', '').strip()
        
        if reply_text:
            Message.objects.create(
                ev=original_msg.ev,
                sender=request.user,
                receiver=original_msg.sender,
                content=reply_text
            )
            messages.success(request, f"Reply sent tightly to {original_msg.sender.name}'s Inbox.")
            
        # Determine where to return based on role
        if request.user.is_superuser:
            return redirect('admin_inbox')
        elif request.user.role == 'seller':
            return redirect('seller_inbox')
        else:
            return redirect('buyer_inbox')
            
    return redirect('dashboard_redirect')

@login_required
def seller_confirm_sale(request, pk):
    """Seller confirms they agree to proceed with this purchase request."""
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk, seller=request.user)
    purchase_request.request_status = 'seller_confirmed'
    purchase_request.save()
    messages.success(request, f'You have confirmed the sale of {purchase_request.listing}. The admin will now finalize it.')
    return redirect('seller_dashboard')

@login_required  
def seller_reject_sale(request, pk):
    """Seller rejects a purchase request, freeing the listing back to market."""
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk, seller=request.user)
    purchase_request.request_status = 'rejected'
    purchase_request.save()
    purchase_request.listing.listing_status = 'approved'
    purchase_request.listing.save()
    
    # Notify Buyer
    Message.objects.create(
        sender=request.user,
        receiver=purchase_request.buyer,
        content=f"Update: Your purchase request for {purchase_request.listing.display_name} has been rejected by the seller. The car is now back on the public marketplace.",
        ev=purchase_request.listing
    )
    
    messages.success(request, f'You have rejected the purchase request. The listing is now available again.')
    return redirect('seller_dashboard')

@login_required
def add_ev(request):
    if request.user.role != 'seller':
        return redirect('buyer_dashboard')

    if request.method == 'POST':
        form = EVListingForm(request.POST, request.FILES)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.seller = request.user
            ev.listing_status = 'pending'
            ev.save()
            messages.success(request, 'EV Listing added successfully. It is now pending approval.')
            return redirect('seller_ev_list')
    else:
        form = EVListingForm()
    return render(request, 'marketplace/add_ev.html', {'form': form})

@login_required
def seller_ev_list(request):
    if request.user.role != 'seller':
        return redirect('buyer_dashboard')
    
    listings = EVListing.objects.filter(seller=request.user)
    return render(request, 'marketplace/seller_ev_list.html', {'listings': listings})

@login_required
def edit_ev(request, pk):
    if request.user.role != 'seller':
        return redirect('buyer_dashboard')
    
    ev = get_object_or_404(EVListing, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = EVListingForm(request.POST, request.FILES, instance=ev)
        if form.is_valid():
            form.save()
            messages.success(request, 'EV Listing updated successfully.')
            return redirect('seller_ev_list')
    else:
        form = EVListingForm(instance=ev)
    return render(request, 'marketplace/edit_ev.html', {'form': form, 'ev': ev})

@login_required
def delete_ev(request, pk):
    if request.user.role != 'seller':
        return redirect('buyer_dashboard')
    
    ev = get_object_or_404(EVListing, pk=pk, seller=request.user)
    if request.method == 'POST':
        ev.delete()
        messages.success(request, 'EV Listing deleted successfully.')
        return redirect('seller_ev_list')
    return render(request, 'marketplace/delete_ev_confirm.html', {'ev': ev})

@login_required
def upload_battery_csv(request, pk):
    if request.user.role != 'seller':
        return redirect('buyer_dashboard')
    
    ev = get_object_or_404(EVListing, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = BatteryCSVForm(request.POST, request.FILES)
        if form.is_valid():
            battery_data = form.save(commit=False)
            battery_data.ev_id = ev
            battery_data.prediction_status = 'pending'
            battery_data.purchase_enabled = False
            battery_data.save()
            messages.success(request, 'Battery CSV uploaded successfully. Buyer can now run a health prediction.')
            return redirect('seller_ev_list')
    else:
        form = BatteryCSVForm()
    return render(request, 'marketplace/upload_battery_csv.html', {'form': form, 'ev': ev})

# --- BUYER VIEWS ---
@login_required
def buyer_dashboard(request):
    if request.user.role != 'buyer':
        return redirect('seller_dashboard')
    
    from django.db.models import Q, OuterRef, Subquery
    
    # Base Queryset: Only approved listings
    queryset = EVListing.objects.filter(listing_status='approved').select_related('seller')
    
    # --- SEARCH & FILTERING LOGIC ---
    
    # 1. Search Query (Keyword)
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(manufacturer__icontains=q) | 
            Q(vehicle_model__icontains=q) |
            Q(description__icontains=q)
        )
        
    # 2. Brand Filter
    brand = request.GET.get('brand', '').strip()
    if brand:
        queryset = queryset.filter(manufacturer__iexact=brand)
        
    # 3. Price Filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
        
    # 4. SOH Filter (Minimum SOH)
    # This requires looking at the LATEST BatteryData for each EV
    min_soh = request.GET.get('min_soh')
    
    latest_battery_data_sub = BatteryData.objects.filter(
        ev_id=OuterRef('pk')
    ).order_by('-upload_date')
    
    # Always annotate SOH so we can display it or filter it
    queryset = queryset.annotate(
        current_soh=Subquery(latest_battery_data_sub.values('soh_prediction')[:1])
    )
    
    if min_soh:
        try:
            queryset = queryset.filter(current_soh__gte=float(min_soh))
        except ValueError:
            pass

    # Get dynamic list of manufacturers for the dropdown
    manufacturers = EVListing.objects.filter(listing_status='approved').values_list('manufacturer', flat=True).distinct().order_by('manufacturer')
    
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).count()
    
    # Purchased EVs history
    purchased_evs = PurchaseRequest.objects.filter(
        buyer=request.user,
        request_status='confirmed'
    ).select_related('listing').order_by('-created_at')

    # Pending purchases for the tracker
    pending_purchases = PurchaseRequest.objects.filter(
        buyer=request.user,
        request_status__in=['submitted', 'seller_confirmed', 'under_review', 'invoice_sent', 'payment_submitted']
    ).select_related('listing').order_by('-created_at')
    
    context = {
        'listings': queryset,
        'unread_messages_count': unread_messages,
        'manufacturers': manufacturers,
        'current_filters': request.GET,
        'purchased_evs': purchased_evs,
        'pending_purchases': pending_purchases,
    }
    return render(request, 'marketplace/buyer_dashboard.html', context)

@login_required
def buyer_inbox(request):
    if request.user.role != 'buyer':
        return redirect('seller_dashboard')
    
    received_messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    received_messages.update(is_read=True)
    
    return render(request, 'marketplace/buyer_inbox.html', {'inbox_messages': received_messages})

@login_required
def ev_detail(request, pk):
    ev = get_object_or_404(EVListing, pk=pk)
    if ev.listing_status not in ['approved', 'pending_sale', 'sold']:
        messages.error(request, 'This listing is not currently available.')
        return redirect('buyer_dashboard')

    battery_data = ev.battery_data.last()

    existing_purchase_request = None
    if request.user.is_authenticated and request.user.role == 'buyer':
        existing_purchase_request = PurchaseRequest.objects.filter(
            buyer=request.user, listing=ev
        ).first()

    if request.method == 'POST':
        contact_form = ContactSellerForm(request.POST)
        if contact_form.is_valid():
            content = contact_form.cleaned_data['message']
            Message.objects.create(
                ev=ev,
                sender=request.user,
                receiver=ev.seller,
                content=content
            )
            messages.success(request, f"Your message has been sent to {ev.seller.name}. They will contact you shortly!")
            return redirect('ev_detail', pk=pk)
    else:
        contact_form = ContactSellerForm()

    return render(request, 'marketplace/ev_detail.html', {
        'ev': ev,
        'battery_data': battery_data,
        'contact_form': contact_form,
        'existing_purchase_request': existing_purchase_request,
    })

@login_required
def contact_admin(request):
    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        if content:
            admin_users = User.objects.filter(is_superuser=True)
            for admin_user in admin_users:
                Message.objects.create(
                    ev=None,  # General inquiry
                    sender=request.user,
                    receiver=admin_user,
                    content=content
                )
            if admin_users.exists():
                messages.success(request, "Your message has been sent to Platform Administration.")
            return redirect('dashboard_redirect')
    return render(request, 'marketplace/contact_admin.html')

@login_required
def check_battery_health(request, pk):
    """Trigger AI and Scientific battery health analysis."""
    if request.user.role != 'buyer':
        return redirect('seller_dashboard')
    
    ev = get_object_or_404(EVListing, pk=pk, listing_status='approved')
    battery_data = ev.battery_data.last()
    
    if not battery_data:
        messages.error(request, 'No battery data available for this EV.')
        return redirect('ev_detail', pk=pk)

    # Note: Status check is bypassed intentionally to allow calibration updates
    from utils.predictor import predict_battery_health
    result = predict_battery_health(battery_data.csv_file.path)

    if result['status'] == 'success':
        battery_data.soh_prediction   = result['soh']
        battery_data.rul_prediction   = result['rul']
        battery_data.prediction_status = 'completed'
        battery_data.purchase_enabled  = True
        battery_data.save()
        
        detail_msg = f"Analysis Updated! SOH: {result['soh']}%"
        if result.get('calc_soh') and result['calc_soh'] > 0:
            detail_msg += f" (Scientific: {result['calc_soh']}%)"
        
        messages.success(request, f"{detail_msg} | RUL: {result['rul']} yrs.")
        logger.info(f"Re-analysis done for EV #{pk}: SOH={result['soh']}")
    else:
        battery_data.prediction_status = 'failed'
        battery_data.purchase_enabled  = False
        battery_data.save()
        messages.error(request, f"Analysis failed: {result['message']}")

    return redirect('ev_detail', pk=pk)


@login_required
def submit_purchase_request(request, pk):
    if request.user.role != 'buyer':
        messages.error(request, 'Only buyers can submit purchase requests.')
        return redirect('buyer_dashboard')

    ev = get_object_or_404(EVListing, pk=pk, listing_status='approved')
    battery_data = ev.battery_data.last()

    if not battery_data or not battery_data.purchase_enabled:
        messages.error(request, 'Purchase is only available after battery verification.')
        return redirect('ev_detail', pk=pk)

    if PurchaseRequest.objects.filter(buyer=request.user, listing=ev).exists():
        messages.warning(request, 'You have already submitted a purchase request.')
        return redirect('ev_detail', pk=pk)

    if request.method == 'POST':
        ev.listing_status = 'pending_sale'
        ev.save()

        PurchaseRequest.objects.create(
            buyer=request.user,
            seller=ev.seller,
            listing=ev,
            request_status='submitted'
        )
        messages.success(request, f'Your purchase request for {ev.manufacturer} {ev.vehicle_model} has been submitted!')
        return redirect('ev_detail', pk=pk)

    return render(request, 'marketplace/purchase_confirmation.html', {
        'ev': ev,
        'battery_data': battery_data,
    })


# --- ADMIN VIEWS ---
from django.contrib.admin.views.decorators import staff_member_required

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "Access restricted to administrators.")
        return redirect('dashboard_redirect')
        
    users = User.objects.all().order_by('-date_joined')
    evs = EVListing.objects.all().order_by('-created_at')
    purchase_requests = PurchaseRequest.objects.filter(
        request_status__in=['submitted', 'seller_confirmed', 'under_review', 'invoice_sent', 'payment_submitted']
    ).order_by('-created_at')

    completed_transactions = PurchaseRequest.objects.filter(
        request_status='confirmed'
    ).select_related('buyer', 'seller', 'listing').order_by('-created_at')

    context = {
        'users': users,
        'evs': evs,
        'purchase_requests': purchase_requests,
        'completed_transactions': completed_transactions,
        'pending_evs': evs.filter(listing_status='pending').count(),
        'pending_users': users.filter(account_status='pending').count(),
        'pending_purchases': purchase_requests.count(),
    }
    return render(request, 'marketplace/admin_dashboard.html', context)

@login_required
def admin_inbox(request):
    if not request.user.is_superuser:
        messages.error(request, "Access restricted to administrators.")
        return redirect('dashboard_redirect')
        
    received_messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    received_messages.update(is_read=True)
    return render(request, 'marketplace/admin_inbox.html', {'inbox_messages': received_messages})

@login_required
def approve_ev(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Access restricted to administrators.")
        return redirect('dashboard_redirect')
    ev = get_object_or_404(EVListing, pk=pk)
    ev.listing_status = 'approved'
    ev.save()
    messages.success(request, f'EV {ev.vehicle_model} has been approved.')
    return redirect('admin_dashboard')

@login_required
def reject_ev(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Access restricted to administrators.")
        return redirect('dashboard_redirect')
    ev = get_object_or_404(EVListing, pk=pk)
    ev.delete()
    messages.success(request, f'EV listing has been rejected and deleted.')
    return redirect('admin_dashboard')

@login_required
def approve_user(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Access restricted to administrators.")
        return redirect('dashboard_redirect')
    user = get_object_or_404(User, pk=pk)
    user.account_status = 'approved'
    user.save()
    messages.success(request, f'User {user.name} has been approved.')
    return redirect('admin_dashboard')

@login_required
def block_user(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Access restricted to administrators.")
        return redirect('dashboard_redirect')
    user = get_object_or_404(User, pk=pk)
    user.account_status = 'blocked'
    user.save()
    messages.warning(request, f'User {user.name} has been blocked.')
    return redirect('admin_dashboard')

@login_required
def confirm_purchase(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Access restricted to administrators.")
        return redirect('dashboard_redirect')
    purchase = get_object_or_404(PurchaseRequest, pk=pk)

    if purchase.request_status != 'payment_submitted':
        messages.error(request, 'Sale cannot be confirmed until the payment has been submitted by the buyer.')
        return redirect('admin_dashboard')

    purchase.request_status = 'confirmed'
    purchase.save()

    listing = purchase.listing
    listing.listing_status = 'sold'
    listing.save()

    # Send automated messages to Buyer and Seller
    message_content = f"System Notification: The purchase of {listing.manufacturer} {listing.vehicle_model} has been finalized and approved by the admin. Registration processing will begin shortly."
    
    # Message to Buyer
    if request.user != purchase.buyer:
        Message.objects.create(
            ev=listing,
            sender=request.user,  # Admin
            receiver=purchase.buyer,
            content=message_content
        )
        
    # Message to Seller
    if request.user != purchase.seller:
        Message.objects.create(
            ev=listing,
            sender=request.user,  # Admin
            receiver=purchase.seller,
            content=message_content
        )

    messages.success(request, f'Purchase confirmed! {listing.manufacturer} {listing.vehicle_model} is now marked as Sold. Notifications sent.')
    return redirect('admin_dashboard')

@login_required
def reject_purchase(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Access restricted to administrators.")
        return redirect('dashboard_redirect')
    purchase = get_object_or_404(PurchaseRequest, pk=pk)
    purchase.request_status = 'rejected'
    purchase.save()

    listing = purchase.listing
    listing.listing_status = 'approved'
    listing.save()

    # Notify Buyer
    Message.objects.create(
        sender=request.user,
        receiver=purchase.buyer,
        content=f"Administrative Notice: Your purchase request for {listing.display_name} has been rejected by the Administration. Please contact support if you have any questions.",
        ev=listing
    )

    messages.warning(request, f'Purchase request rejected. {listing.manufacturer} {listing.vehicle_model} is back to active listings.')
    return redirect('admin_dashboard')

# --- Advanced Purchase Workflow Views ---

@login_required
def admin_review_purchase(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard_redirect')
    purchase = get_object_or_404(PurchaseRequest, pk=pk)
    if purchase.request_status == 'seller_confirmed':
        purchase.request_status = 'under_review'
        purchase.save()
        messages.info(request, f"Purchase request for {purchase.listing.vehicle_model} is now under internal review.")
    return redirect('admin_dashboard')

@login_required
def admin_generate_invoice(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard_redirect')
    purchase = get_object_or_404(PurchaseRequest, pk=pk)
    if purchase.request_status == 'under_review':
        purchase.request_status = 'invoice_sent'
        purchase.save()
        
        # Notify Buyer
        Message.objects.create(
            sender=request.user,
            receiver=purchase.buyer,
            content=f"System Notification: An invoice has been generated and sent for your purchase of {purchase.listing.display_name}. Please proceed with the payment in your dashboard.",
            ev=purchase.listing
        )
        messages.success(request, f"Invoice generated for {purchase.buyer.name}. Notification sent.")
    return redirect('admin_dashboard')

@login_required
def admin_confirm_payment(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard_redirect')
    purchase = get_object_or_404(PurchaseRequest, pk=pk)
    if purchase.request_status == 'payment_submitted':
        # This will be finalized by the existing 'confirm_purchase' view
        # or we just move the status to something that 'confirm_purchase' expects.
        # Actually, let's just make this view move it to a specific status or just
        # allow 'confirm_purchase' to handle it.
        # Moving to payment_received status? No, let's just keep it simple:
        # confirmed is the final.
        pass
    return redirect('admin_dashboard')

@login_required
def buyer_submit_payment(request, pk):
    purchase = get_object_or_404(PurchaseRequest, pk=pk, buyer=request.user)
    if purchase.request_status == 'invoice_sent':
        purchase.request_status = 'payment_submitted'
        purchase.save()
        
        # Notify Admin
        admin_users = User.objects.filter(is_superuser=True)
        for admin in admin_users:
            Message.objects.create(
                sender=request.user,
                receiver=admin,
                content=f"System Notification: Buyer {request.user.name} has submitted payment for {purchase.listing.display_name}. Please verify and confirm the sale.",
                ev=purchase.listing
            )
        messages.success(request, "Payment successfully submitted! Administration will verify it shortly.")
    return redirect('buyer_dashboard')

@login_required
def battery_health_center(request):
    if request.user.role != 'buyer':
        return redirect('seller_dashboard')
    
    from django.db.models import OuterRef, Subquery

    all_listings = EVListing.objects.filter(listing_status='approved')
    
    # Get the latest prediction status for each EV
    latest_status_subquery = BatteryData.objects.filter(
        ev_id=OuterRef('pk')
    ).order_by('-upload_date').values('prediction_status')[:1]
    
    all_listings = all_listings.annotate(latest_status=Subquery(latest_status_subquery))
    
    pending_checks = all_listings.filter(latest_status='pending')
    verified_cars = all_listings.filter(latest_status='completed')
    awaiting_data = all_listings.filter(latest_status__isnull=True)

    context = {
        'pending_checks': pending_checks,
        'verified_cars': verified_cars,
        'awaiting_data': awaiting_data,
        'total_verified': verified_cars.count()
    }
    return render(request, 'marketplace/battery_health_center.html', context)
