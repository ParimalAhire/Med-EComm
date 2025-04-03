from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import CustomerProfile, SellerProfile, Medicine, Order, OrderItem, PrescriptionUpload, Cart, CartItem, Category

# Inline Profile for Customers
class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = "Customer Profiles"

# Inline Profile for Sellers
class SellerProfileInline(admin.StackedInline):
    model = SellerProfile
    can_delete = False
    verbose_name_plural = "Seller Profiles"

# Extend User Admin to Show Profiles
class CustomUserAdmin(UserAdmin):
    inlines = [CustomerProfileInline, SellerProfileInline]

# Unregister Default User Admin and Register Custom One
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register CustomerProfile Separately
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'phone_number')

# Register SellerProfile Separately
@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'phone_number')
    search_fields = ('user__username', 'business_name')

# ✅ Register Category Model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register Medicine Model
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'seller', 'prescription_required')
    search_fields = ('name', 'active_ingredients', 'brand_name')
    list_filter = ('seller', 'prescription_required','categories')
    ordering = ('name',)

# Register Order Model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__user__username',)
    ordering = ('-created_at',)

# Register OrderItem Model
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'medicine', 'quantity')
    search_fields = ('order__customeruserusername', 'medicine__name')

# Register PrescriptionUpload Model
@admin.register(PrescriptionUpload)
class PrescriptionUploadAdmin(admin.ModelAdmin):
    list_display = ('customer', 'uploaded_at')
    search_fields = ('customer__user__username',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'created_at')
    search_fields = ('customer__user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'medicine', 'quantity')
    search_fields = ('cart__customeruserusername', 'medicine__name')

# Register all models in Django admin
admin.site.site_header = "GenericMediCare Admin"
admin.site.site_title = "GenericMediCare Admin Panel"
admin.site.index_title = "Welcome to GenericMediCare Administration"