from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Ensure all models are imported when `models` is imported
from models.user import User
from models.tailor import Tailor
from models.measurement import Measurement
from models.order import Order
from models.message import Message
from models.review import Review
from models.location import State, District, Taluk, City, Town, Village, Locality
