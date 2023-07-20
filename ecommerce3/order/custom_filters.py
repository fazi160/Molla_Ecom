from django import template

register = template.Library()

@register.filter
def calculate_total_price(order_item):
    return order_item.price * order_item.quantity * 1.18
