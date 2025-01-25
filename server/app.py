#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
database = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code Challenge</h1>"

class Restaurants(Resource):
    def get(self):
        all_restaurants = Restaurant.query.all()
        return [restaurant.to_dict() for restaurant in all_restaurants], 200
    
class RestaurantById(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        
        data = restaurant.to_dict()
        data["restaurant_pizzas"] = [
            {**data}
            for rp in restaurant.restaurant_pizzas
        ]
        return data, 200


    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        return {"error": "Restaurant was not found!"}, 404

class Pizzas(Resource):
    def get(self):
        all_pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in all_pizzas], 200

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            price = data.get("price")
            pizza_id = data.get("pizza_id")
            restaurant_id = data.get("restaurant_id")

            if price is None or not (1 <= price <= 30):
                return {"errors": ["validation errors"]}, 400

            pizza = db.session.get(Pizza, pizza_id)
            restaurant = db.session.get(Restaurant, restaurant_id)

            if not pizza:
                return {"errors": ["validation errors"]}, 400
            if not restaurant:
                return {"errors": ["validation errors"]}, 400

            restaurant_pizza = RestaurantPizza(
                price=price, pizza_id=pizza_id, restaurant_id=restaurant_id
            )
            db.session.add(restaurant_pizza)
            db.session.commit()

            return restaurant_pizza.to_dict(), 201

        except Exception as e:
            return {"errors": ["validation errors"]}, 500

api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantById, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)