from .models import Cart

def cart_total(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(customer__user=request.user).first()
        if cart:
            unique_items_count = cart.cartitem_set.count()  # Count unique medicines
            return {'cart_count': unique_items_count}
    return {'cart_count': 0}