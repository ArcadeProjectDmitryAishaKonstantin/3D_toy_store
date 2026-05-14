from flask import jsonify, request
from flask_restful import Resource
from data import db_session
from data.shop_info import ShopInfo
from blueprints.delivery import get_coordinates, calculate_distance

# Калькулятор стоимости доставки
class DeliveryCalculateResource(Resource):
    def post(self):
        data = request.get_json()
        city = data.get('city')

        if not city:
            return jsonify({'error': 'City is required'}), 400

        session = db_session.create_session()
        try:
            shop_informacia = session.query(ShopInfo).first()

            if not shop_informacia or not shop_informacia.shop_lat or not shop_informacia.shop_lon:
                return jsonify({'error': 'Shop coordinates not set'}), 400

            city_lat, city_lon = get_coordinates(city)
            if city_lat is None:
                return jsonify({'error': 'Could not determine city coordinates'}), 400

            distance = calculate_distance(
                city_lat, city_lon,
                shop_informacia.shop_lat, shop_informacia.shop_lon
            )

            dostavka_price = int(distance * (shop_informacia.delivery_base_price or 50))

            return jsonify({
                'city': city,
                'distance_km': round(distance, 2),
                'delivery_cost': dostavka_price
            })
        finally:
            session.close()