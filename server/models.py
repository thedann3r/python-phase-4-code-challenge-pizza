from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship(
        "RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan"
    )

    serialize_rules = ("-restaurant_pizzas",)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship(
        "RestaurantPizza", back_populates="pizza", cascade="all, delete-orphan"
    )

    serialize_rules = ("-restaurant_pizzas",)

    def __repr__(self):
        return f"<Pizza {self.name}>"


class RestaurantPizza(db.Model, SerializerMixin):
    _tablename_ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)

    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")

    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas")
    
    @validates("price")
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30.")
        return value