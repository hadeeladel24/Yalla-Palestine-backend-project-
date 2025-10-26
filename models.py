from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
import secrets
db=SQLAlchemy()

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True,nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(100),nullable=True)
    role = db.Column(db.String(20), default='user')  # user, owner, guest, admin
    provider = db.Column(db.String(50), nullable=True)  
    def set_password(self,password):
        self.password=generate_password_hash(password)
    def check_password(self,password):
        return check_password_hash(self.password,password)

    
    def to_dict(self):
        return {
            "id":self.id,
            "username":self.username,
            "email":self.email,
            "role":self.role
        }


class torist_place(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    description=db.Column(db.String(200),nullable=False)
    location=db.Column(db.String(100),nullable=False)
    rating=db.Column(db.Float,nullable=False)
    price=db.Column(db.Float,nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id":self.id,
            "name":self.name,
            "description":self.description,
            "location":self.location,
            "rating":self.rating,
            "price":self.price
        }
   



class hotel(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    description=db.Column(db.String(200),nullable=False)
    location=db.Column(db.String(100),nullable=False)
    rating=db.Column(db.Float,nullable=False)
    price=db.Column(db.Float,nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow)
    def to_dict(self):
        return {
            "id":self.id,
            "name":self.name,
            "description":self.description,
            "location":self.location,
            "rating":self.rating,
            "price":self.price
        }
   
   

class restaurant(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    description=db.Column(db.String(200),nullable=False)
    location=db.Column(db.String(100),nullable=False)
    rating=db.Column(db.Float,nullable=False)
    price=db.Column(db.Float,nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow)
    def to_dict(self):
        return {
            "id":self.id,   
            "name":self.name,
            "description":self.description,
            "location":self.location,
            "rating":self.rating,
            "price":self.price
        }
   
   
   

class booking(db.Model):
    """Booking model for hotel and restaurant reservations"""
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Booking Type
    booking_type = db.Column(db.String(20), nullable=False)  # 'hotel' or 'restaurant'
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=True)
    
    # Booking Details
    check_in_date = db.Column(db.DateTime)
    check_out_date = db.Column(db.DateTime)
    booking_date = db.Column(db.DateTime)  # For restaurant
    booking_time = db.Column(db.String(10))  # For restaurant (e.g., "19:00")
    number_of_guests = db.Column(db.Integer)
    number_of_rooms = db.Column(db.Integer)  # For hotels
    special_requests = db.Column(db.Text)
    
    # Pricing
    base_price = db.Column(db.Float)
    tax_amount = db.Column(db.Float, default=0.0)
    service_fee = db.Column(db.Float, default=0.0)
    total_price = db.Column(db.Float)
    currency = db.Column(db.String(3), default='USD')
    
    # Payment Information - Stripe
    payment_status = db.Column(db.String(20), default='pending')  # pending, processing, paid, failed, refunded
    payment_method = db.Column(db.String(50), default='stripe')
    stripe_payment_intent_id = db.Column(db.String(255), unique=True)  # Stripe Payment Intent ID
    stripe_charge_id = db.Column(db.String(255))  # Stripe Charge ID
    stripe_customer_id = db.Column(db.String(255))  # Stripe Customer ID
    payment_date = db.Column(db.DateTime)
    
    # Booking Status
    booking_status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    confirmation_code = db.Column(db.String(50), unique=True)
    
    # Cancellation
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    refund_amount = db.Column(db.Float)
    refund_status = db.Column(db.String(20))  # pending, processed, failed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='bookings')
    hotel = db.relationship('hotel', backref='bookings')
    restaurant = db.relationship('restaurant', backref='bookings')
    
    def __init__(self, **kwargs):
        super(booking, self).__init__(**kwargs)
        if not self.confirmation_code:
            self.confirmation_code = self.generate_confirmation_code()
    
    @staticmethod
    def generate_confirmation_code():
        """Generate unique confirmation code"""
        return f"YP{secrets.token_hex(4).upper()}"
    
    def calculate_total_price(self):
        """Calculate total price including tax and service fee"""
        if not self.base_price:
            return 0.0
        
        # Tax (0% by default, adjust as needed)
        self.tax_amount = self.base_price * 0.0
        
        # Service fee (5% by default)
        self.service_fee = self.base_price * 0.05
        
        # Total
        self.total_price = self.base_price + self.tax_amount + self.service_fee
        return self.total_price
    
    def to_dict(self):
        """Convert booking to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'booking_type': self.booking_type,
            'hotel_id': self.hotel_id,
            'restaurant_id': self.restaurant_id,
            'check_in_date': self.check_in_date.isoformat() if self.check_in_date else None,
            'check_out_date': self.check_out_date.isoformat() if self.check_out_date else None,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'booking_time': self.booking_time,
            'number_of_guests': self.number_of_guests,
            'number_of_rooms': self.number_of_rooms,
            'special_requests': self.special_requests,
            'base_price': self.base_price,
            'tax_amount': self.tax_amount,
            'service_fee': self.service_fee,
            'total_price': self.total_price,
            'currency': self.currency,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'stripe_payment_intent_id': self.stripe_payment_intent_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'booking_status': self.booking_status,
            'confirmation_code': self.confirmation_code,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancellation_reason': self.cancellation_reason,
            'refund_amount': self.refund_amount,
            'refund_status': self.refund_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
   
   
   
   
class review(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    torist_place_id=db.Column(db.Integer,db.ForeignKey('torist_place.id'),nullable=True)
    hotel_id=db.Column(db.Integer,db.ForeignKey('hotel.id'),nullable=True)
    restaurant_id=db.Column(db.Integer,db.ForeignKey('restaurant.id'),nullable=True)
    rating=db.Column(db.Float,nullable=False)
    comment=db.Column(db.String(200),nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow)
    def to_dict(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "torist_place_id":self.torist_place_id,
            "hotel_id":self.hotel_id,
            "restaurant_id":self.restaurant_id,
            "rating":self.rating,
            "comment":self.comment,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }
   
class trips(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    torist_place_id=db.Column(db.Integer,db.ForeignKey('torist_place.id'),nullable=True)
    hotel_id=db.Column(db.Integer,db.ForeignKey('hotel.id'),nullable=True)
    restaurant_id=db.Column(db.Integer,db.ForeignKey('restaurant.id'),nullable=True)
    start_date=db.Column(db.DateTime,nullable=False)
    end_date=db.Column(db.DateTime,nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow)
    def to_dict(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "torist_place_id":self.torist_place_id,
            "hotel_id":self.hotel_id,
            "restaurant_id":self.restaurant_id,
            "start_date":self.start_date,
            "end_date":self.end_date,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }
   
   
   
   
   
   