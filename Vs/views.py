from pyexpat.errors import messages

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
import razorpay
from django.conf import settings
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import  staff_member_required
from urllib3 import request


from .models import Product, Cart, Order,Notification


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




    paginator = Paginator(products, 6)



    page_number = request.GET.get('page')



    products = paginator.get_page(page_number)



    return render(
        request,
        'shop.html',
        {
            'products': products
        }
    )

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

    if not request.user.is_authenticated:
        return redirect("login")

    product = Product.objects.get(id=id)

    size = request.POST.get("size")
    quantity = int(request.POST.get("quantity", 1))

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        size=size,
        defaults={"quantity": quantity}
    )

    if not created:
        cart_item.quantity += quantity
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
            request.session.set_expiry(0)  # Browser close aana logout
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")

from django.contrib import messages

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        messages.success(request, "Registration successful! Please login.")
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


def buy_now(request, id):

    if not request.user.is_authenticated:
        return redirect("login")

    product = Product.objects.get(id=id)

    size = request.POST.get("size")
    quantity = int(request.POST.get("quantity", 1))

    Cart.objects.create(
        user=request.user,
        product=product,
        quantity=quantity,
        size=size
    )

    return redirect("checkout")


@login_required
def orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "orders.html",
        {"orders": orders}
    )

@staff_member_required
def dashboard(request):

    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()

    products = Product.objects.all().order_by('-id')

    # orders display
    orders = Order.objects.all().order_by('-id')

    total_revenue = 0

    notifications = Notification.objects.filter(
        is_read=False
    ).count()


    for order in orders:
        total_revenue += order.total_amount


    return render(request, "dashboard.html", {

        "total_products": total_products,

        "total_orders": total_orders,

        "total_users": total_users,

        "total_revenue": total_revenue,

        "products": products,

        "orders": orders,

        "notification": notifications

    })

def edit_product(request, id):

    product = Product.objects.get(id=id)

    if request.method == "POST":

        product.name = request.POST["name"]
        product.price = request.POST["price"]
        product.category = request.POST["category"]
        product.description = request.POST["description"]

        if request.FILES.get("image"):
            product.image = request.FILES["image"]

        product.save()

        return redirect("dashboard")

    return render(request, "edit_product.html", {
        "product": product
    })
def delete_product(request, id):

    product = Product.objects.get(id=id)
    product.delete()

    return redirect("dashboard")

def add_product(request):

    if request.method == "POST":

        Product.objects.create(
            name=request.POST.get("name"),
            price=request.POST.get("price"),
            category=request.POST.get("category"),
            description=request.POST.get("description"),
            image=request.FILES.get("image")
        )

        return redirect("dashboard")

    return render(request, "add_product.html")




def mens(request):
    products = Product.objects.filter(category='Men')
    return render(request, 'mens.html', {'products': products})

def womens(request):
    products = Product.objects.filter(category='Women')
    return render(request, 'womens.html', {'products': products})

def kids(request):
    products = Product.objects.filter(category='kids')
    return render(request, 'kids.html', {'products': products})

def new_arrivals(request):
    products = Product.objects.filter(category='New Arrivals')
    return render(request, 'new_arrivals.html', {'products': products})



def checkout(request):

    if not request.user.is_authenticated:
        return redirect("login")

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

        send_mail(
            subject="New Order Received - VS Fashions",
            message=f"""
Customer: {request.user.username}

Email: {request.user.email}

Total Amount: ₹{total}
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["vsfashionin@gmail.com"],
            fail_silently=False,
        )

        customer_email = request.POST.get("email")
        email = EmailMultiAlternatives(
            "Order Confirmation - VS Fashions",
            "",
            settings.EMAIL_HOST_USER,
            [customer_email],
        )

        email.attach_alternative(
            f"""
            <h2>Thank You for Shopping with VS Fashions ❤️</h2>
            <p>Hello {request.user.username},</p>
            <p>Your order has been placed successfully.</p>
            <p><strong>Total Amount:</strong> ₹{total}</p>
            """,
            "text/html"
        )

        email.send()

        cart_items.delete()

        return render(request, "success.html")

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total
    })






