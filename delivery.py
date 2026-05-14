import math
import requests
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from data import db_session
from data.shop_info import ShopInfo

blueprint = Blueprint('delivery', __name__, template_folder='templates')

GEOCODER_API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
STATIC_API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"


def get_coordinates(address):
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": GEOCODER_API_KEY,
        "geocode": address,
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        features = data.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])
        if not features:
            return None, None
        
        coordinates = features[0]['GeoObject']['Point']['pos']
        lon, lat = map(float, coordinates.split())
        return lat, lon
    except Exception as e:
        print(f"Ошибка геокодирования {address}: {e}")
        return None, None


def calculate_distance(lat1, lon1, lat2, lon2):
    radius = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c

# Страница с расчетом цены доставки
@blueprint.route('/delivery')
def dostavka_page():
    db_sess = db_session.create_session()
    try:
        shop_info = db_sess.query(ShopInfo).first()
        
        map_url = None
        if shop_info and shop_info.shop_lat and shop_info.shop_lon:
            map_url = f"https://static-maps.yandex.ru/v1?ll={shop_info.shop_lon},{shop_info.shop_lat}&spn=0.05,0.05&apikey={STATIC_API_KEY}&pt={shop_info.shop_lon},{shop_info.shop_lat},pm2dgl"
        
        return render_template('delivery/calculate_delivery.html', shop_info=shop_info, map_url=map_url)
    finally:
        db_sess.close()

# Посчитать стоимость доставки
@blueprint.route('/api/delivery/calculate', methods=['POST'])
def calculate_delivery_api():
    data = request.get_json()
    city = data.get('city')
    
    if not city:
        return jsonify({'error': 'Город не указан'}), 400
    
    db_sess = db_session.create_session()
    try:
        shop_info = db_sess.query(ShopInfo).first()
        
        if not shop_info or not shop_info.shop_lat or not shop_info.shop_lon:
            return jsonify({'error': 'Координаты магазина не заданы'}), 400
        
        city_lat, city_lon = get_coordinates(city)
        if city_lat is None:
            return jsonify({'error': 'Не удалось определить координаты адреса'}), 400
        
        distance = calculate_distance(
            city_lat, city_lon,
            shop_info.shop_lat, shop_info.shop_lon
        )
        
        delivery_cost = int(distance * (shop_info.delivery_base_price or 50))
        
        return jsonify({
            'city': city,
            'distance_km': round(distance, 2),
            'delivery_cost': delivery_cost
        })
    except Exception as e:
        print(f"Ошибка расчёта доставки: {e}")
        return jsonify({'error': 'Ошибка при расчёте доставки'}), 500
    finally:
        db_sess.close()