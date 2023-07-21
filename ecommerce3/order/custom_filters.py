# from django import template

# register = template.Library()

# @register.filter
# def calculate_total_price(order_item):
#     return order_item.price * order_item.quantity * 1.18



from django import template

register = template.Library()

@register.filter
def calculate_total_price(order_item):
    total_price = order_item.product.product_price * order_item.quantity * 1.18
    return round(total_price, 2)