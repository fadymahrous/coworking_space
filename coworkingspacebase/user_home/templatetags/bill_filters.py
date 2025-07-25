from django import template

register = template.Library()

@register.filter
def calculate_order_total(order_items):
    """Calculate total for a group of order items"""
    total = 0
    for item in order_items:
        total += item.count * item.item_name.price
    return total