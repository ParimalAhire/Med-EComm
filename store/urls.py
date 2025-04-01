from django.urls import path
from .views import (
    home,register, customer_register, seller_register, login_view, logout_view, 
    customer_dashboard, seller_dashboard, medicine_list, medicine_detail, add_medicine,edit_medicine, delete_medicine,
    upload_medicine, edit_seller_profile,edit_customer_profile, browse_medicines,view_cart, add_to_cart, 
    remove_from_cart, clear_cart, update_cart,checkout, order_success,education_articles,education_faqs,education_infographics,
    education_videos

)

urlpatterns = [
    # Home Page
    path('', home, name='home'),
    path('register',register, name='register'),

    # Authentication Routes
    path('register/customer/', customer_register, name='customer_register'),
    path('register/seller/', seller_register, name='seller_register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Dashboards
    path('dashboard/customer/', customer_dashboard, name='customer_dashboard'),
    path('dashboard/seller/', seller_dashboard, name='seller_dashboard'),

    # Medicine Routes
    path('medicines/', medicine_list, name='medicine_list'),
    path('medicines/<int:pk>/', medicine_detail, name='medicine_detail'),

    path('add-medicine/', add_medicine, name='add_medicine'),
    path('medicine/edit/<int:pk>/', edit_medicine, name='edit_medicine'),
    path('medicine/delete/<int:pk>/', delete_medicine, name='delete_medicine'),

    path('upload-medicine/', upload_medicine, name='upload_medicine'),

    #Edit profile
    path('edit-seller-profile/', edit_seller_profile, name='edit_seller_profile'),
    path('edit-customer-profile/', edit_customer_profile, name='edit_customer_profile'),
    
    #Medicine Browse
    path('browse/',browse_medicines, name='browse_medicines'),
    path('medicine/<int:pk>',medicine_detail, name='medicine_detail'),

    #Cart And Cart Item
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', clear_cart, name='clear_cart'),
    path('cart/update/<int:pk>/<str:action>/', update_cart, name='update_cart'),
    path('checkout/', checkout, name='checkout'),
    path('order-success/', order_success, name='order_success'),

    #Educational Resources
    path('education/articles/', education_articles, name='education_articles'),
    path('education/infographics/', education_infographics, name='education_infographics'),
    path('education/faqs/', education_faqs, name='education_faqs'),
    path('education/videos/', education_videos, name='education_videos'),

]