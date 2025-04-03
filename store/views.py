from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.db.models import Q
import pandas as pd
import io
from .forms import CustomerRegistrationForm, SellerRegistrationForm, LoginForm, MedicineForm,MedicineUploadForm, ProfileEditForm,SellerProfileForm, CustomerProfileForm
from .forms import CheckoutForm
from .models import Medicine, Order, OrderItem,CustomerProfile, Cart, CartItem,User,Category

# 🏠 Home Page
def home(request):
    return render(request, 'home.html')

def register(request):
    return render(request, 'register.html')

# Customer Registration View
def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()  # This already creates CustomerProfile
            login(request, user)
            return redirect('customer_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")  
    else:
        form = CustomerRegistrationForm()

    return render(request, 'register_customer.html', {'form': form})

# Seller Registration View
def seller_register(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('seller_dashboard')
        else:
            messages.error(request, "Error in form submission!")  # Display error message
    else:
        form = SellerRegistrationForm()
    return render(request, 'register_seller.html', {'form': form})

# 🔑 Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                # Redirect based on user role
                if hasattr(user, 'customerprofile'):
                    return redirect('customer_dashboard')
                elif hasattr(user, 'sellerprofile'):
                    return redirect('seller_dashboard')
                else:
                    return redirect('home')
            else:
                # Check if username exists
                if not User.objects.filter(username=username).exists():
                    messages.error(request, "Username not found.")
                else:
                    messages.error(request, "Incorrect password.")
                    
    else:
        form = LoginForm()

    return render(request, 'login.html',{'form':form})

# 🚪 Logout View
def logout_view(request):
    logout(request)
    return redirect('home')

# 🏠 Customer Dashboard (Only for Customers)
@login_required
def customer_dashboard(request):
    if not hasattr(request.user, 'customerprofile'):
        return redirect('home')  # Prevent unauthorized access

    customer = request.user.customerprofile  # Get the customer profile
    medicines = Medicine.objects.all()
    orders = Order.objects.filter(customer=request.user.customerprofile)
    cart_items = CartItem.objects.filter(cart__customer=customer)  # Get cart items for this customer

    return render(request, 'customer_dashboard.html', {
        'medicines': medicines,
        'orders': orders,
        'cart_items': cart_items
    })

# 🏪 Seller Dashboard (Only for Sellers)
@login_required
def seller_dashboard(request):
    if not hasattr(request.user, 'sellerprofile'):
        return redirect('home')  # Prevent unauthorized access

    seller_profile = request.user.sellerprofile  # Get the seller profile

    # Get all medicines listed by the seller
    medicines = Medicine.objects.filter(seller=seller_profile)

    # Get all order items where medicine is sold by this seller
    order_items = OrderItem.objects.filter(medicine__in=medicines)

    # Get all orders that contain these order items
    orders = Order.objects.filter(orderitem__in=order_items).distinct()

    return render(request, 'seller_dashboard.html', {
        'medicines': medicines,
        'orders': orders,  # Orders specific to this seller
        })

# 💊 Medicine List (Available to All)
def medicine_list(request):
    medicines = Medicine.objects.all()
    return render(request, 'medicine_list.html', {'medicines': medicines})

# 🔍 Medicine Detail View
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    return render(request, 'medicine_detail.html', {'medicine': medicine})

# 🏪 Add Medicine (Only for Sellers)
@login_required
def add_medicine(request):
    if not hasattr(request.user, 'sellerprofile'):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    if request.method == "POST":
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.seller = request.user.sellerprofile
            medicine.save()

            category_text = form.cleaned_data.get('category_input', '')
            category_names = [c.strip() for c in category_text.split(',') if c.strip()]

            for cat_name in category_names:
                category, _ = Category.objects.get_or_create(name=cat_name)
                medicine.categories.add(category)

            medicine.save()
            form.save_m2m()  

            messages.success(request, "✅ Medicine added successfully!")
            return redirect('seller_dashboard')
        else:
            messages.error(request, "⚠ Please correct the errors below.")
    else:
        form = MedicineForm()

    return render(request, 'medicine_form.html', {'form': form})

# ✏️ Edit Medicine
@login_required
def edit_medicine(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)

    # Restrict access to the seller who added the medicine
    if medicine.seller != request.user.sellerprofile:
        messages.error(request, "⚠ Unauthorized action.")
        return redirect('seller_dashboard')

    if request.method == "POST":
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Medicine updated successfully!")
            return redirect('seller_dashboard')
        else:
            messages.error(request, "⚠ Please correct the errors below.")
    else:
        # Populate category field as a comma-separated string
        initial_data = {
            'category_input': ', '.join(medicine.categories.values_list('name', flat=True))
        }
        form = MedicineForm(instance=medicine, initial=initial_data)

    return render(request, 'medicine_form.html', {'form': form, 'medicine': medicine})

#delete medicine
@login_required
def delete_medicine(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, seller=request.user.sellerprofile)

    if request.method == 'POST':
        medicine.delete()
        messages.success(request, "Medicine deleted successfully!")
        return redirect('seller_dashboard')

    return render(request, 'medicine_form.html', {'medicine': medicine, 'delete': True})

# Medicine Upload (Bulk Upload)
@login_required
def upload_medicine(request):
    if not hasattr(request.user, 'sellerprofile'):
        return redirect('home')  # Prevent unauthorized access

    errors = []  # Store errors here

    if request.method == 'POST':
        form = MedicineUploadForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_name = uploaded_file.name.lower()

            try:
                # Read file based on extension
                if file_name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                elif file_name.endswith('.csv'):
                    df = pd.read_csv(io.StringIO(uploaded_file.read().decode('utf-8')))
                else:
                    errors.append("Unsupported file format. Please upload a CSV or Excel (.xlsx) file.")
                    return render(request, 'upload_medicine.html', {'form': form, 'errors': errors})

                # Convert column names to lowercase for uniformity
                df.columns = df.columns.str.strip().str.lower()

                # Required columns
                required_columns = {'name', 'description', 'price', 'stock', 'active_ingredients', 'brand_name', 'prescription_required', 'categories'}

                # Check for missing columns
                missing_columns = required_columns - set(df.columns)
                if missing_columns:
                    errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                    return render(request, 'upload_medicine.html', {'form': form, 'errors': errors})

                # Process "prescription_required" as boolean
                df['prescription_required'] = df['prescription_required'].astype(str).str.strip().str.lower()
                df['prescription_required'] = df['prescription_required'].map({'yes': True, 'no': False})

                # Validate and save medicines
                for index, row in df.iterrows():
                    if pd.isnull(row['name']) or pd.isnull(row['price']) or pd.isnull(row['stock']):
                        errors.append(f"Row {index + 2}: 'name', 'price', and 'stock' cannot be empty.")
                        continue

                    if not isinstance(row['price'], (int, float)) or row['price'] <= 0:
                        errors.append(f"Row {index + 2}: Invalid price value.")
                        continue

                    if not isinstance(row['stock'], int) or row['stock'] < 0:
                        errors.append(f"Row {index + 2}: Stock should be a positive integer.")
                        continue

                    if pd.isnull(row['prescription_required']):
                        errors.append(f"Row {index + 2}: 'prescription_required' must be 'Yes' or 'No'.")
                        continue

                    # Check for duplicate medicine (same name and seller)
                    existing_medicine = Medicine.objects.filter(name=row['name'], seller=request.user.sellerprofile).first()
                    if existing_medicine:
                        errors.append(f"Row {index + 2}: Medicine '{row['name']}' already exists.")
                        continue  # Skip adding duplicate

                    # Save new medicine
                    medicine = Medicine.objects.create(
                        seller=request.user.sellerprofile,
                        name=row['name'],
                        description=row.get('description', ''),
                        price=row['price'],
                        stock=row['stock'],
                        active_ingredients=row.get('active_ingredients', ''),
                        brand_name=row.get('brand_name', ''),
                        prescription_required=row['prescription_required']
                    )

                    # ✅ Process categories from file
                    if not pd.isnull(row.get('categories')):  # Check if categories column is not empty
                        category_names = [c.strip() for c in row['categories'].split(',')]  # Split by comma
                        existing_categories = Category.objects.filter(name__in=category_names)  # Get matching categories

                        # Assign categories to medicine
                        if existing_categories.exists():
                            medicine.categories.set(existing_categories)  # Assign matched categories

                # If errors exist, return with messages
                if errors:
                    return render(request, 'upload_medicine.html', {'form': form, 'errors': errors})

                messages.success(request, "✅ Medicines uploaded successfully!")
                return redirect('seller_dashboard')

            except Exception as e:
                errors.append(f"Error processing file: {e}")

    else:
        form = MedicineUploadForm()

    return render(request, 'upload_medicine.html', {'form': form, 'errors': errors})

# Edit Seller Profile (Only for Sellers)
@login_required
def edit_seller_profile(request):
    if not hasattr(request.user, 'sellerprofile'):
        return redirect('home')  # Prevent unauthorized access

    user = request.user
    seller = user.sellerprofile

    if request.method == "POST":
        user_form = ProfileEditForm(request.POST, instance=user)
        profile_form = SellerProfileForm(request.POST, instance=seller)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('seller_dashboard')

    else:
        user_form = ProfileEditForm(instance=user)
        profile_form = SellerProfileForm(instance=seller)

    return render(request, 'register_seller.html', {
        'form': user_form,
        'profile_form': profile_form,
        'editing': True
    })

#Edit Customer Profile (Only for Customers)

@login_required
def edit_customer_profile(request):
    """Allows customers to edit their profile."""
    if not hasattr(request.user, 'customerprofile'):
        messages.error(request, "You are not registered as a customer.")
        return redirect('home')

    customer_profile = request.user.customerprofile

    if request.method == "POST":
        user_form = ProfileEditForm(request.POST, instance=request.user)
        profile_form = CustomerProfileForm(request.POST, instance=customer_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('customer_dashboard')
        else:
            messages.error(request, "Error updating profile. Please check the details.")
    else:
        user_form = ProfileEditForm(instance=request.user)
        profile_form = CustomerProfileForm(instance=customer_profile)

    return render(request, 'register_customer.html', {
        'form': user_form,
        'profile_form': profile_form,
        'editing': True  # Indicate that we are in editing mode
    })

#Browse Medicines (Available to All)
def browse_medicines(request):
    # Restrict Access to sellers
    if request.user.is_authenticated and hasattr(request.user, 'sellerprofile'):
        return redirect('seller_dashboard')
    
    medicines = Medicine.objects.all()
    categories = Category.objects.all()  # ✅ Fetch available categories

    # Get filter parameters from request
    query = request.GET.get('q', '')  # Search query
    category_id = request.GET.get('category')  # ✅ Fetch selected category
    brand = request.GET.get('brand')
    stock = request.GET.get('stock')
    sort = request.GET.get('sort')

    # Apply search filter
    if query:
        medicines = medicines.filter(
            Q(name__icontains=query) | Q(active_ingredients__icontains=query)
        )

    # Apply category filter ✅
    if category_id:
        medicines = medicines.filter(categories__id=category_id)

    # Apply additional filters
    if brand:
        medicines = medicines.filter(brand_name=brand)
    if stock == 'in_stock':
        medicines = medicines.filter(stock__gt=0)
    elif stock == 'out_of_stock':
        medicines = medicines.filter(stock=0)
    
    # Sorting logic
    if sort == 'name_asc':
        medicines = medicines.order_by('name')
    elif sort == 'name_desc':
        medicines = medicines.order_by('-name')
    elif sort == 'newest':
        medicines = medicines.order_by('-id')  # Assuming ID represents order of addition

    # Get distinct filter options for dropdowns
    brands = Medicine.objects.values_list('brand_name', flat=True).distinct()

    return render(request, 'browse_medicines.html', {
        'medicines': medicines,
        'brands': brands,
        'categories': categories,  # ✅ Pass categories to template
        'query': query,  
        'selected_category': category_id,  # ✅ Pass selected category to retain selection
    })


# Medicine Detail View with Alternatives
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    alternatives = medicine.get_alternative_medicines().order_by('price')
    
    return render(request, 'medicine_detail.html', {
        'medicine': medicine,
        'alternatives': alternatives,
    })


#Cart and CartItem
# Ensure customer has a cart
def get_or_create_cart(user):
    customer, _ = CustomerProfile.objects.get_or_create(user=user)
    cart, _ = Cart.objects.get_or_create(customer=customer)
    return cart

# Add to Cart
@login_required
def add_to_cart(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    cart = get_or_create_cart(request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, medicine=medicine)
    
    if not created:
        cart_item.quantity += 1  # If already in cart, increase quantity
    cart_item.save()

    return redirect('view_cart')

# Remove from Cart
@login_required
def remove_from_cart(request, pk):
    cart = get_or_create_cart(request.user)
    cart_item = CartItem.objects.filter(cart=cart, medicine_id=pk).first()
    
    if cart_item:
        cart_item.delete()

    return redirect('view_cart')

# Update Cart (Increase/Decrease Quantity)
@login_required
def update_cart(request, pk, action):
    cart = get_or_create_cart(request.user)
    cart_item = CartItem.objects.filter(cart=cart, medicine_id=pk).first()

    if cart_item:
        if action == "increase":
            cart_item.quantity += 1
        elif action == "decrease" and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()
    
    return redirect('view_cart')

# View Cart
@login_required
def view_cart(request):
    cart = get_or_create_cart(request.user)
    cart_items = cart.cartitem_set.all()
    total_price = cart.get_total()
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

# Clear Cart
@login_required
def clear_cart(request):
    cart = get_or_create_cart(request.user)
    cart.cartitem_set.all().delete()
    
    return redirect('view_cart')

# Checkout View
@login_required
def checkout(request):
    cart = get_or_create_cart(request.user)
    cart_items = cart.cartitem_set.all()
    total_price = cart.get_total()

    customer = request.user.customerprofile
    full_name = request.user.get_full_name() or request.user.username
    email = request.user.email
    phone = customer.phone_number

    # Check if any medicine in the cart requires a prescription
    prescription_required = any(item.medicine.prescription_required for item in cart_items)

    if request.method == "POST":
        form = CheckoutForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            # Ensure prescription is uploaded if required
            if prescription_required and 'prescription' not in request.FILES:
                messages.error(request, "A prescription is required for some medicines in your cart.")
                return redirect('checkout')

            # Create Order
            order = Order.objects.create(
                customer=customer,
                full_name=full_name,
                email=email,
                phone=phone,
                alternate_phone=form.cleaned_data.get('alternate_phone', ''),
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                pincode=form.cleaned_data['pincode'],
                delivery_instructions=form.cleaned_data.get('delivery_instructions', ''),
                total_price=total_price,
                payment_method=form.cleaned_data['payment_method'],
                status='Pending',
                prescription=form.cleaned_data.get('prescription') if prescription_required else None  # Save prescription only if required
            )

            # Move cart items to order and reduce stock
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    medicine=item.medicine,
                    quantity=item.quantity,
                    price=item.medicine.price,
                )
                item.medicine.stock -= item.quantity
                item.medicine.save()

            # Clear the cart
            cart.cartitem_set.all().delete()

            messages.success(request, "Your order has been placed successfully!")
            return redirect('order_success')

    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
        'full_name': full_name,
        'email': email,
        'phone': phone,
        'prescription_required': prescription_required  # Pass to template
    })


# Order Success View
@login_required
def order_success(request):
    return render(request, 'order_success.html')

#Education Tab
def education_articles(request):
    return render(request, 'education_articles.html')

def education_infographics(request):
    return render(request, 'education_infographics.html')

def education_faqs(request):
    return render(request, 'education_faqs.html')

def education_videos(request):
    return render(request, 'education_videos.html')