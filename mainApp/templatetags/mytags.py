from django import template
from mainApp.models import Checkout, CheckoutProducts,Product
register = template.Library()


@register.filter(name='checkoutProducts')
def checkoutProducts(checkoutid):
    checkout = Checkout.objects.get(id=checkoutid)
    cp = CheckoutProducts.objects.filter(checkout=checkout)
    c = []
    for item in cp:
        x = {'name': item.p.name, 'maincategory': item.p.maincategory, 'subcategory': item.p.subcategory, 'brand': item.p.brand,
             'color': item.p.color, 'size': item.p.size, 'price': item.p.finalprice, 'qty': item.qty, 'total': item.total, 'pic': item.p.pic1.url}
        c.append(x)
    return c


@register.filter(name='paymentStatus')
def paymentStatus(op):
    if(op==0):
        return "Pending"
    else:
        return "Done"
    
@register.filter(name='paymentMode')
def paymentMode(op):
    if(op==0):
        return "COD"
    else:
        return "Net Banking"
    
@register.filter(name='orderStatus')
def orderStatus(op):
    if(op==0):
        return "order placed"
    elif(op==1):
        return "not packed"
    elif(op==2):
        return "packed"
    elif(op==3):
        return "ready to ship"
    elif(op==4):
        return "shipped"
    elif(op==5):
        return "out for delivery"
    elif(op==6):
        return "delivered"
    else:
        return "Cancelled"
          