from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomerProfile, SellerProfile,Medicine, Category

# Customer Registration Form
class CustomerRegistrationForm(UserCreationForm):  
    phone_number = forms.CharField(
        max_length=15, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        required=True, 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone_number', 'address']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  
        
        if commit:
            user.save()
            CustomerProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address']
            )
        return user

# Seller Registration Form
class SellerRegistrationForm(UserCreationForm):  # Use UserCreationForm
    business_name = forms.CharField(max_length=255)
    phone_number = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2','business_name','phone_number']  # Use password1 and password2 for validation

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Ensure password is hashed
        if commit:
            user.save()
            SellerProfile.objects.create(
                user=user,
                business_name=self.cleaned_data['business_name'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user

# Medicine form
class MedicineForm(forms.ModelForm):
    category_input = forms.CharField(
        required=False,
        label="Categories (comma-separated)",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Medicine
        fields = ['name', 'description', 'price', 'stock', 'active_ingredients', 'brand_name', 'prescription_required', 'image']
        labels = {
            'name': 'Medicine Name',
            'description': 'Description',
            'price': 'Price (₹)',
            'stock': 'Stock Quantity',
            'active_ingredients': 'Active Ingredients (comma-separated)',
            'brand_name': 'Brand Name',
            'prescription_required': 'Requires Prescription?',
            'image': 'Upload Image',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'active_ingredients': forms.TextInput(attrs={'class': 'form-control'}),
            'brand_name': forms.TextInput(attrs={'class': 'form-control'}),
            'prescription_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_category_input(self):
        """Ensure the category input is a valid string and process it correctly."""
        category_data = self.cleaned_data.get('category_input', '')

        # ✅ Handle the case where category_input might be a list
        if isinstance(category_data, list):
            category_data = ', '.join(category_data)

        return category_data.strip()  # Return cleaned category text

    def save(self, commit=True):
        medicine = super().save(commit=False)

        category_text = self.cleaned_data.get('category_input', '')
        category_names = [c.strip() for c in category_text.split(',') if c.strip()]


        if commit:
            medicine.save()  

            medicine.categories.clear()  
            for cat_name in category_names:
                category, created = Category.objects.get_or_create(name=cat_name)
                medicine.categories.add(category)

        return medicine

# Login Form
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class MedicineUploadForm(forms.Form):
    file = forms.FileField()


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['business_name', 'phone_number']

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'address']

class ProfileEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        exclude = ['password']  # Exclude password field to avoid unnecessary updates

#Checkout Form
class CheckoutForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    city = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    pincode = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))

    alternate_phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    delivery_instructions = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

    payment_method = forms.ChoiceField(
        choices=[('cod', 'Cash on Delivery (COD)'), ('online', 'Online Payment')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    prescription = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))  # Add Prescription Upload Field