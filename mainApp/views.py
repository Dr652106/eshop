from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from random import randrange
from django.conf import settings
from django.core.mail import send_mail
from eshop.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
import razorpay


from .models import *


def home(Request):
    data = Product.objects.all().order_by('id').reverse()[:8]
    return render(Request, "index.html", {'data': data})


def shop(Request, mc, sc, br):
    if (mc == 'All' and sc == 'All' and br == 'All'):
        data = Product.objects.all().order_by('id').reverse()
    elif (mc != 'All' and sc == 'All' and br == 'All'):
        data = Product.objects.filter(
            maincategory=Maincategory.objects.get(name=mc)).order_by('id').reverse()
    elif (mc == 'All' and sc != 'All' and br == 'All'):
        data = Product.objects.filter(
            subcategory=Subcategory.objects.get(name=sc)).order_by('id').reverse()
    elif (mc == 'All' and sc == 'All' and br != 'All'):
        data = Product.objects.filter(
            brand=Brand.objects.get(name=br)).order_by('id').reverse()
    elif (mc != 'All' and sc != 'All' and br == 'All'):
        data = Product.objects.filter(maincategory=Maincategory.objects.get(
            name=mc), subcategory=Subcategory.objects.get(name=sc)).order_by('id').reverse()
    elif (mc != 'All' and sc == 'All' and br != 'All'):
        data = Product.objects.filter(maincategory=Maincategory.objects.get(
            name=mc), brand=Brand.objects.get(name=br)).order_by('id').reverse()
    elif (mc == 'All' and sc != 'All' and br != 'All'):
        data = Product.objects.filter(brand=Brand.objects.get(
            name=br), subcategory=Subcategory.objects.get(name=sc)).order_by('id').reverse()
    else:
        data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc), brand=Brand.objects.get(
            name=br), subcategory=Subcategory.objects.get(name=sc)).order_by('id').reverse()
    maincategory = Maincategory.objects.all()
    subcategory = Subcategory.objects.all()
    brand = Brand.objects.all()
    return render(Request, "shop.html", {'data': data, 'maincategory': maincategory, 'subcategory': subcategory, 'brand': brand, 'mc': mc, 'sc': sc, 'br': br})


def singleProduct(Request, id):
    data = Product.objects.get(id=id)
    return render(Request, "single-product.html", {'data': data})


def loginPage(Request):
    if (Request.method == "POST"):
        username = Request.POST.get("username")
        password = Request.POST.get("password")
        user = authenticate(username=username, password=password)
        if (user is not None):
            login(Request, user)
            if (user.is_superuser):
                return redirect("/admin")
            else:
                return redirect("/profile")
        else:
            messages.error(Request, "Invalid username or password")
    return render(Request, "login.html")


def logoutPage(Request):
    logout(Request)
    return redirect("/login")


def signupPage(Request):
    if (Request.method == "POST"):
        p = Request.POST.get("password")
        cp = Request.POST.get("cpassword")
        if (p == cp):
            b = Buyer()
            b.name = Request.POST.get("name")
            b.username = Request.POST.get("username")
            b.phone = Request.POST.get("phone")
            b.email = Request.POST.get("email")
            user = User(username=b.username, email=b.email)
            if (user):
                user.set_password(p)
                user.save()
                b.save()
                subject = 'Your Account is created : Team Eshop'
                message = "hello "+b.name + \
                    "\nThanks to create a Buyer Account with us \n now yor can buy the latest products\nTeam Eshop"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [b.email, ]
                send_mail(subject, message, email_from, recipient_list)
                return redirect("/login/")
            else:
                messages.error(Request, "Username Already Taken!!!!!!")
        else:
            messages.error(
                Request, "Password And Confirm Password Doesn't Matched!!!")
    return render(Request, "signup.html")


@login_required(login_url='/login/')
def profilePage(Request):
    user = User.objects.get(username=Request.user)
    if (user.is_superuser):
        return redirect("/admin")
    else:
        buyer = Buyer.objects.get(username=user.username)
        wishlist = Wishlist.objects.filter(user=buyer)
        orders = Checkout.objects.filter(user=buyer)
    return render(Request, "profile.html", {'user': buyer, 'wishlist': wishlist, 'orders': orders})


@login_required(login_url='/login/')
def updateProfilePage(Request):
    user = User.objects.get(username=Request.user)
    if (user.is_superuser):
        return redirect("/admin")
    else:
        buyer = Buyer.objects.get(username=user.username)
        if (Request.method == "POST"):
            buyer.name = Request.POST.get("name")
            buyer.email = Request.POST.get("email")
            buyer.phone = Request.POST.get("phone")
            buyer.addressline1 = Request.POST.get("addressline1")
            buyer.addressline2 = Request.POST.get("addressline2")
            buyer.addressline3 = Request.POST.get("addressline3")
            buyer.pin = Request.POST.get("pin")
            buyer.city = Request.POST.get("city")
            buyer.state = Request.POST.get("state")
            if (Request.FILES.get("pic") != ""):
                buyer.pic = Request.FILES.get("pic")
            buyer.save()
            return redirect("/profile")
    return render(Request, "update-profile.html", {'user': buyer})


@login_required(login_url='/login/')
def addToCart(Request, id):
    cart = Request.session.get('cart', None)
    p = Product.objects.get(id=id)
    if (cart is None):
        cart = {str(p.id): {'pid': p.id, 'pic': p.pic1.url, 'name': p.name, 'color': p.color, 'size': p.size, 'price': p.finalprice, 'qty': 1,
                            'total': p.finalprice, 'maincategory': p.maincategory.name, 'subcategory': p.subcategory.name, 'brand': p.brand.name}}
    else:
        if (str(p.id) in cart):
            item = cart[str(p.id)]
            item['qty'] = item['qty']+1
            item['total'] = item['total']+item['price']
            cart[str(p.id)] = item
        else:
            cart.setdefault(str(p.id), {'pid': p.id, 'pic': p.pic1.url, 'name': p.name, 'color': p.color, 'size': p.size, 'price': p.finalprice, 'qty': 1,
                                        'total': p.finalprice, 'maincategory': p.maincategory.name, 'subcategory': p.subcategory.name, 'brand': p.brand.name})

    Request.session['cart'] = cart
    Request.session.set_expiry(60*60*24*45)
    return redirect("/cart")


@login_required(login_url='/login/')
def cartPage(Request):
    cart = Request.session.get('cart', None)
    c = []
    total = 0
    shipping = 0
    if (cart is not None):
        for value in cart.values():
            total = total + value['total']
            c.append(value)
        if (total < 1000 and total > 0):
            shipping = 150
    final = total+shipping
    return render(Request, "cart.html", {'cart': c, 'total': total, 'shipping': shipping, 'final': final})


@login_required(login_url='/login/')
def deleteCart(Request, pid):
    cart = Request.session.get('cart', None)
    if (cart):
        for key in cart.keys():
            if (str(pid) == key):
                del cart[key]
                break
        Request.session['cart'] = cart
    return redirect("/cart")


@login_required(login_url='/login/')
def updateCart(Request, pid, op):
    cart = Request.session.get('cart', None)
    if (cart):
        for key, value in cart.items():
            if (str(pid) == key):
                if (op == "inc"):
                    value['qty'] = value['qty']+1
                    value['total'] = value['total']+value['price']
                elif (op == 'dec' and value['qty'] > 1):
                    value['qty'] = value['qty']-1
                    value['total'] = value['total']-value['price']
                cart[key] = value
                break
        Request.session['cart'] = cart
    return redirect("/cart")


@login_required(login_url='/login/')
def addToWishlist(Request, pid):
    try:
        user = Buyer.objects.get(username=Request.user.username)
        p = Product.objects.get(id=pid)
        try:
            w = Wishlist.objects.get(user=user, product=p)
        except:
            w = Wishlist()
            w.user = user
            w.product = p
            w.save()
        return redirect("/profile")
    except:
        return redirect("/admin")


@login_required(login_url='/login/')
def deleteWishlist(Request, pid):
    try:
        user = Buyer.objects.get(username=Request.user.username)
        p = Product.objects.get(id=pid)
        try:
            w = Wishlist.objects.get(user=user, product=p)
            w.delete()
        except:
            pass
    except:
        pass
    return redirect("/profile")


@login_required(login_url='/login/')
def checkoutPage(Request):
    try:
        buyer = Buyer.objects.get(username=Request.user)
        cart = Request.session.get('cart', None)
        c = []
        total = 0
        shipping = 0
        if (cart is not None):
            for value in cart.values():
                total = total + value['total']
                c.append(value)
            if (total < 1000 and total > 0):
                shipping = 150
        final = total+shipping
        return render(Request, "checkout.html", {'user': buyer, 'cart': c, 'total': total, 'shipping': shipping, 'final': final})
    except:
        return redirect("/admin")


client = razorpay.Client(auth=(RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY))
@login_required(login_url='/login/')
def orderPage(Request):
    if(Request.method=="POST"):
        mode = Request.POST.get("mode")
        user = Buyer.objects.get(username=Request.user.username)
        cart = Request.session.get('cart',None)
        if(cart is None):
            return redirect("/cart")
        else:
            check = Checkout()
            check.user = user
            total = 0
            shipping = 0
            for value in cart.values():
                total = total + value['total']
            if (total < 1000 and total > 0):
                shipping = 150
            final = total+shipping
            check.total = total
            check.shipping = shipping
            check.final=final
            check.save()
            for value in cart.values():
                cp = CheckoutProducts()
                cp.checkout = check
                cp.p = Product.objects.get(id=value['pid'])
                cp.qty = value['qty']
                cp.total = value['total']
                cp.save()
            Request.session['cart']={}
            subject = 'Your Order has been Placed : Team Eshop'
            message =   "Thanks to Shop With Us\nYou Has has been placed\nNow You Can Tract Your Orders in Profile Page\nTeam Eshop"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail( subject, message, email_from, recipient_list )
            if(mode=="COD"):
                return redirect("/confirmation")
            else:
                orderAmount = check.final*100
                orderCurrency = "INR"
                paymentOrder = client.order.create(dict(amount=orderAmount,currency=orderCurrency,payment_capture=1))
                paymentId = paymentOrder['id']
                check.mode="Net Banking"
                check.save()
                return render(Request,"pay.html",{
                    "amount":orderAmount,
                    "api_key":RAZORPAY_API_KEY,
                    "order_id":paymentId,
                    "User":user
                })
    else:
        return redirect("/checkout")

@login_required(login_url='/login/')
def paymentSuccess(request, rppid, rpoid, rpsid):
    buyer = Buyer.objects.get(username=request.user)
    check = Checkout.objects.filter(buyer=buyer)
    check = check[::-1]
    check = check[0]
    check.rppid = rppid
    # check.rpoid=rpoid
    # check.rpsid=rpsid
    check.paymentstatus = 1
    check.save()
    return redirect('/confirmation/')


@login_required(login_url='/login/')
def confirmationPage(Request):
    return render(Request, 'confirmation.html')


def contactPage(Request):
    if (Request.method == "POST"):
        c = Contact()
        c.name = Request.POST.get("name")
        c.email = Request.POST.get("email")
        c.phone = Request.POST.get("phone")
        c.subject = Request.POST.get("subject")
        c.message = Request.POST.get("message")
        c.save()
        messages.success(
            Request, "Thanks to share your query with us!! Our team will contact you")
    return render(Request, "contact.html")


def searchPage(Request):
    search = Request.POST.get('search')
    data = Product.objects.filter(Q(name__icontains=search) | Q(color__icontains=search) | Q(
        size__icontains=search) | Q(description__icontains=search) | Q(stock__icontains=search))
    maincategory = Maincategory.objects.all()
    subcategory = Subcategory.objects.all()
    brand = Brand.objects.all()
    return render(Request, "shop.html", {'data': data, 'maincategory': maincategory, 'subcategory': subcategory, 'brand': brand, 'mc': 'All', 'sc': 'All', 'br': 'All'})


def forgetUsername(Request):
    if (Request.method == "POST"):
        username = Request.POST.get("username")
        try:
            user = User.objects.get(username=username)
            if (user.is_superuser):
                return redirect("/admin")
            else:
                buyer = Buyer.objects.get(username=username)
                otp = randrange(10000, 999999)
                buyer.otp = otp
                buyer.save()
                subject = 'OTP for Password Reset : Team Eshop'
                message = "OTP for Password Reset is "+str(otp)+"\nTeam Eshop"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [buyer.email, ]
                send_mail(subject, message, email_from, recipient_list)
                Request.session['resetuser'] = username
                return redirect("/forget-otp")
        except:
            messages.error(Request, "invalid username !!!!")
    return render(Request, "forget-username.html")


def forgetOTP(Request):
    if (Request.method == "POST"):
        otp = Request.POST.get('otp')
        username = Request.session.get('resetuser', None)
        if (username):
            buyer = Buyer.objects.get(username=username)
            if otp is not None and int(otp) == buyer.otp:
                return redirect("/forget-password")
            else:
                messages.error(Request, "Invalid OTP")
        else:
            messages.error(Request, "UnAuthorized")
    return render(Request, "forget-otp.html")


def forgetPassword(Request):
    if (Request.method == "POST"):
        password = Request.POST.get('password')
        cpassword = Request.POST.get('cpassword')
        username = Request.session.get('resetuser', None)
        if (username):
            if (password == cpassword):
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                return redirect("/login")
            else:
                messages.error(
                    Request, "Password and Confirm password doestnot matched")
        else:
            messages.error(Request, "UnAuthorizedddd")
    return render(Request, "forget-password.html")
