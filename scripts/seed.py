from datetime import datetime, timedelta
import os
import random
import sys

# Ensure project root is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app
from models import db, User, torist_place, hotel, restaurant, booking, review, trips


def get_or_create_user(username: str, email: str, role: str = 'user', password: str = 'Password@123') -> User:
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def create_hotels() -> list:
    samples = [
        {"name": "Bethlehem Suites", "description": "Cozy stay near Nativity Church", "location": "Bethlehem", "rating": 4.5, "price": 120.0},
        {"name": "Jerusalem View Hotel", "description": "Panoramic city views", "location": "Jerusalem", "rating": 4.7, "price": 180.0},
        {"name": "Ramallah Residence", "description": "Business-friendly rooms", "location": "Ramallah", "rating": 4.2, "price": 90.0},
    ]
    created = []
    for s in samples:
        existing = hotel.query.filter_by(name=s["name"]).first()
        if existing:
            created.append(existing)
            continue
        h = hotel(**s)
        db.session.add(h)
        created.append(h)
    db.session.commit()
    return created


def create_restaurants() -> list:
    samples = [
        {"name": "Falafel House", "description": "Best falafel in town", "location": "Jerusalem", "rating": 4.6, "price": 10.0},
        {"name": "Olive Tree Diner", "description": "Traditional Palestinian dishes", "location": "Bethlehem", "rating": 4.4, "price": 15.0},
        {"name": "Cedar Garden", "description": "Family-friendly meals", "location": "Ramallah", "rating": 4.1, "price": 12.0},
    ]
    created = []
    for s in samples:
        existing = restaurant.query.filter_by(name=s["name"]).first()
        if existing:
            created.append(existing)
            continue
        r = restaurant(**s)
        db.session.add(r)
        created.append(r)
    db.session.commit()
    return created


def create_sites() -> list:
    samples = [
        {"name": "Nativity Church", "description": "Historic basilica", "location": "Bethlehem", "rating": 4.8, "price": 25.0},
        {"name": "Al-Aqsa Mosque", "description": "Iconic holy site", "location": "Jerusalem", "rating": 4.9, "price": 30.0},
        {"name": "Old City Market", "description": "Traditional souks", "location": "Jerusalem", "rating": 4.5, "price": 0.0},
    ]
    created = []
    for s in samples:
        existing = torist_place.query.filter_by(name=s["name"]).first()
        if existing:
            created.append(existing)
            continue
        t = torist_place(**s)
        db.session.add(t)
        created.append(t)
    db.session.commit()
    return created


def create_bookings(user: User, hotels: list, restaurants: list) -> list:
    created = []
    # Hotel booking
    h = hotels[0]
    check_in = datetime.utcnow().date() + timedelta(days=7)
    check_out = check_in + timedelta(days=3)
    base_price = h.price * 1 * 3
    b1 = booking(
        user_id=user.id,
        booking_type='hotel',
        hotel_id=h.id,
        check_in_date=datetime(check_in.year, check_in.month, check_in.day),
        check_out_date=datetime(check_out.year, check_out.month, check_out.day),
        number_of_rooms=1,
        number_of_guests=2,
        base_price=base_price,
        currency='USD',
        booking_status='pending',
        payment_status='pending',
    )
    b1.calculate_total_price()
    db.session.add(b1)
    created.append(b1)

    # Restaurant booking
    r = restaurants[0]
    b_date = datetime.utcnow().date() + timedelta(days=2)
    b2 = booking(
        user_id=user.id,
        booking_type='restaurant',
        restaurant_id=r.id,
        booking_date=datetime(b_date.year, b_date.month, b_date.day),
        booking_time='19:00',
        number_of_guests=3,
        base_price=10.0 * 3,
        currency='USD',
        booking_status='pending',
        payment_status='pending',
    )
    b2.calculate_total_price()
    db.session.add(b2)
    created.append(b2)

    db.session.commit()
    return created


def create_reviews(user: User, sites: list, hotels: list, restaurants: list) -> list:
    created = []
    items = [
        {"torist_place_id": sites[0].id, "rating": 5.0, "comment": "Amazing experience"},
        {"hotel_id": hotels[0].id, "rating": 4.0, "comment": "Very comfortable"},
        {"restaurant_id": restaurants[0].id, "rating": 4.5, "comment": "Delicious food"},
    ]
    for it in items:
        rv = review(user_id=user.id, **it)
        db.session.add(rv)
        created.append(rv)
    db.session.commit()
    return created


def create_trips(user: User, sites: list, hotels: list, restaurants: list) -> list:
    created = []
    start_date = datetime.utcnow().date() + timedelta(days=10)
    end_date = start_date + timedelta(days=5)
    tr = trips(
        user_id=user.id,
        torist_place_id=sites[0].id,
        hotel_id=hotels[0].id,
        restaurant_id=restaurants[0].id,
        start_date=datetime(start_date.year, start_date.month, start_date.day),
        end_date=datetime(end_date.year, end_date.month, end_date.day)
    )
    db.session.add(tr)
    created.append(tr)
    db.session.commit()
    return created


def main():
    with app.app_context():
        # Ensure tables exist
        db.create_all()

        admin = get_or_create_user('admin', 'admin@example.com', 'admin')
        owner = get_or_create_user('owner', 'owner@example.com', 'owner')
        user = get_or_create_user('john', 'john@example.com', 'user')

        hotels = create_hotels()
        restaurants = create_restaurants()
        sites = create_sites()

        create_bookings(user, hotels, restaurants)
        create_reviews(user, sites, hotels, restaurants)
        create_trips(user, sites, hotels, restaurants)

        print('Seeding completed successfully.')


if __name__ == '__main__':
    main()


