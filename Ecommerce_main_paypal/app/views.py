from django.shortcuts import redirect, render
from django.views import View
from .models import Customer,Product,Cart,OrderPlaced
from .forms import CustomerProfileForm, CustomerRegistrationForm,MyPasswordChangeForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

def home(request):
    mobiles = Product.objects.filter(category='M')
    laptops = Product.objects.filter(category='L')
    totalitem = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        for c in cart:
            totalitem += c.quantity
    return render(request, 'app/home.html',{'mobiles':mobiles,'laptops':laptops,'totalitem':totalitem})

def product_detail(request,pk):
    product = Product.objects.get(pk=pk)
    incart = 0
    totalitem = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        for c in cart:
            totalitem += c.quantity
            if c.product == product:
                incart = 1
    return render(request, 'app/productdetail.html',{'product':product, 'incart':incart,'totalitem':totalitem})

def mobile(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        for c in cart:
            totalitem += c.quantity
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'OPPO' or data == 'Samsung' or data == 'OnePlus' or data == 'Realme' or data == 'Redmi':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__lt = 10000)
    elif data == 'above':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__gt = 10000)
    return render(request, 'app/mobile.html',{'mobiles':mobiles,'totalitem':totalitem})

def laptop(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        for c in cart:
            totalitem += c.quantity
    if data == None:
        laptops = Product.objects.filter(category='L')
    elif data == 'ASUS' or data == 'HP' or data == 'DELL' or data == 'LENOVO':
        laptops = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'below':
        laptops = Product.objects.filter(category='L').filter(discounted_price__lt = 35000)
    elif data == 'above':
        laptops = Product.objects.filter(category='L').filter(discounted_price__gt = 35000)
    return render(request, 'app/laptop.html',{'laptops':laptops,'totalitem':totalitem})

class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form':form})
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Congratulations!!You have got registered successfully.')
            form.save()
        return render(request, 'app/customerregistration.html', {'form':form})

# for login, we have used views of auth.So,no need to create a view for login

# for changepassword, we have used views of auth.So,no need to create a view for changepassword

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self,request):
        totalitem = 0
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user)
            for c in cart:
                totalitem += c.quantity
        form = CustomerProfileForm()
        return render(request, 'app/profile.html',{'form':form,'totalitem':totalitem})
    def post(self,request):
        totalitem = 0
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user)
            for c in cart:
                totalitem += c.quantity
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            pincode = form.cleaned_data['pincode']
            cus = Customer(user=user,name=name,locality=locality,city=city,state=state,pincode=pincode)
            cus.save()
            messages.success(request, 'Your Profile has been Updated successfully!!')
        return render(request, 'app/profile.html',{'form':form,'totalitem':totalitem})

@login_required
def address(request):
    totalitem = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        for c in cart:
            totalitem += c.quantity
    usr_addresses = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'usr_addresses':usr_addresses,'totalitem':totalitem})

@login_required
def add_to_cart(request):
    user = request.user
    p_id = request.GET.get('p_id')
    product = Product.objects.get(id=p_id)
    Cart(user=user,product=product).save()
    return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        totalitem = 0
        user = request.user
        cart = Cart.objects.filter(user=user)
        for c in cart:
            totalitem += c.quantity
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        if cart:
            for c in cart:
                amount = amount + c.quantity*c.product.discounted_price
            total_amount = amount + shipping_amount
        else:
            shipping_amount = 0.0
            messages.success(request, 'Your cart is empty!!Please add product(s) to go further.')
        return render(request, 'app/addtocart.html', {'cart_objects':cart,'amount':amount,'total_amount':total_amount,'shipping_amount':shipping_amount,'totalitem':totalitem})

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        amount = 0.0
        shipping_amount = 70.0
        for c in cart_product:
            amount = amount + c.quantity*c.product.discounted_price
        
        data = {
            'quantity':c.quantity,
            'amount':amount,
            'shippingamount':shipping_amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)
    
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        amount = 0.0
        shipping_amount = 70.0
        if cart_product:
            for c in cart_product:
                amount = amount + c.quantity*c.product.discounted_price
        else:
            shipping_amount = 0.0
            messages.success(request, 'Your cart is empty!!Please add product(s) to go further.')
        
        data = {
            'quantity':c.quantity,
            'amount':amount,
            'shippingamount':shipping_amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        amount = 0.0
        shipping_amount = 70.0
        if cart_product:
            for c in cart_product:
                amount = amount + c.quantity*c.product.discounted_price
        else:
            shipping_amount = 0.0
            
        
        data = {
            'amount':amount,
            'shippingamount':shipping_amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)

@login_required
def checkout(request):
    totalitem = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        for c in cart:
            totalitem += c.quantity    
    user = request.user
    address = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for c in cart_product:
            amount = amount + c.quantity*c.product.discounted_price
        totalamount = amount + shipping_amount
    return render(request, 'app/checkout.html', {'address':address,'totalamount':totalamount,'cart_items':cart_items,'totalitem':totalitem})

@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('cust_id')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
        c.delete()
    return redirect("orders")

@login_required
def orders(request):
    totalitem = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        for c in cart:
            totalitem += c.quantity  
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed':op,'totalitem':totalitem})

@login_required
def buy_now(request):
    user = request.user
    p_id = request.GET.get('p_id')
    product = Product.objects.get(id=p_id)
    Cart(user=user,product=product).save()
    return redirect('/checkout')

