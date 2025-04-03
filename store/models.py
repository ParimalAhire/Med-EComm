#models.py for role based access and medicine mapping 
from django.db import models
from django.contrib.auth.models import User

# Customer Profile Model
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.user.username

# Seller Profile Model
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# Medicine Model
class Medicine(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE)  # Each medicine is listed by a seller
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='medicine_images/', null=True, blank=True)
    prescription_required = models.BooleanField(default=False)  # If True, user must upload a prescription
    active_ingredients = models.TextField(help_text="Comma-separated active ingredients")  # Used for mapping alternatives
    brand_name = models.CharField(max_length=255, null=True, blank=True)

    # ✅ Many-to-Many Relationship with Category
    categories = models.ManyToManyField(Category, blank=True,related_name="medicines")

    def get_alternative_medicines(self):
        """Fetches medicines with the same active ingredients but different brands."""
        return Medicine.objects.filter(active_ingredients=self.active_ingredients).exclude(id=self.id)

    def __str__(self):
        return f"{self.name} ({self.active_ingredients})"

# Order Model
class Order(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    delivery_instructions = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Renamed from total_amount
    payment_method = models.CharField(max_length=50, choices=[("COD", "Cash on Delivery"), ("Online", "Online Payment")])
    created_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    prescription = models.ImageField(upload_to='prescriptions/', null=True, blank=True)
    def __str__(self):
        return f"Order {self.pk} - {self.customer.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at purchase time

    def __str__(self):
        return f"{self.quantity} x {self.medicine.name} (Order {self.order.pk})"
    
# Prescription Upload Model
class PrescriptionUpload(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    prescription = models.ImageField(upload_to='prescriptions/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prescription by {self.customer.user.username}"
    
# Cart Model
class Cart(models.Model):
    customer = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE)  # One cart per customer
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        """Calculate total price of cart items."""
        return sum(item.get_total_price() for item in self.cartitem_set.all())

    def __str__(self):
        return f"Cart of {self.customer.user.username}"


# CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # Each item is linked to a cart
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)  # Medicine being added
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        """Total price of this item (medicine price * quantity)."""
        return self.medicine.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.medicine.name} in {self.cart.customer.user.username}'s cart"
