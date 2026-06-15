from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
import razorpay
from django.conf import settings

from .models import Product, Cart, Order


def home(request):
    return render(request, "home.html")


def shop(request):

    products = Product.objects.all()

    search = request.GET.get('search')
    category = request.GET.get('category')

    if search:
        products = products.filter(
            name__icontains=search
        )

    if category and category != "All":
        products = products.filter(
            category=category
        )

    return render(request, 'shop.html', {
        'products': products
    })


def product(request, id):

    product = Product.objects.get(id=id)

    return render(request, 'product.html', {
        'product': product
    })

def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def cart(request):

    if not request.user.is_authenticated:
        return redirect("login")

    cart_items = Cart.objects.filter(user=request.user)

    total = 0

    for item in cart_items:
        total += item.product.price * item.quantity

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total
    })
def add_to_cart(request, id):

    print("ADD TO CART HIT")
    print(request.POST)

    if not request.user.is_authenticated:
        return redirect("login")

    product = Product.objects.get(id=id)

    size = request.POST.get("size")
    print("SIZE =", size)

    cart_item = Cart.objects.create(
        user=request.user,
        product=product,
        quantity=1,
        size=size
    )

    return redirect("cart")

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            auth_login(request, user)
            return redirect("home")

    return render(request, "login.html")


def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 == password2:

            User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )

            return redirect("login")

    return render(request, "register.html")


def logout_view(request):
    logout(request)
    return redirect("login")

def remove_from_cart(request, id):

    if not request.user.is_authenticated:
        return redirect("login")

    cart_item = Cart.objects.get(id=id)

    if cart_item.user == request.user:
        cart_item.delete()

    return redirect("cart")


def increase_quantity(request, id):
    cart_item = Cart.objects.get(id=id)

    if cart_item.user == request.user:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


def decrease_quantity(request, id):
    cart_item = Cart.objects.get(id=id)

    if cart_item.user == request.user:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect("cart")



def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    total = 0

    for item in cart_items:
        total += item.product.price * item.quantity

    if request.method == "POST":

        Order.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            address=request.POST.get("address"),
            total_amount=total
        )

        cart_items.delete()

        return render(request, "success.html")

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    payment = client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "payment": payment,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })

def buy_now(request, id):

    product = Product.objects.get(id=id)

    Cart.objects.create(
        user=request.user,
        product=product,
        quantity=1,
        size=request.POST.get("size")
    )

    return redirect("checkout")

def orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "orders.html",
        {"orders": orders}
    )


def dashboard(request):

    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()

    total_revenue = 0

    for order in Order.objects.all():
        total_revenue += order.total_amount

    return render(request, "dashboard.html", {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_revenue": total_revenue
    })