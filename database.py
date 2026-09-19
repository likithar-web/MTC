from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    description = db.Column(db.Text)

    price = db.Column(db.Float, nullable=False)

    offer_price = db.Column(db.Float)

    category = db.Column(db.String(100))

    meal = db.Column(db.String(50))

    image = db.Column(db.String(255))

    available = db.Column(db.Boolean, default=True)

    featured = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )