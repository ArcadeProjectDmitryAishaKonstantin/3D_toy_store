import math


def format_price(price):
    return f"{price:,}".replace(',', ' ')


def calculate_delivery_cost(distance_km, base_price_per_km=50):
    return int(distance_km * base_price_per_km)


def get_cart_count(cart_items):
    return sum(item.quantity for item in cart_items)