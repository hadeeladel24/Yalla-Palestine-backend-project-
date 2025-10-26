from flask import Blueprint,request,jsonify
from models import hotel,db
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import datetime
from routes.rate_limit import rate_limit
from routes.role_req import role_required
hotel_routes=Blueprint('hotel',__name__)

@hotel_routes.route('/',methods=['GET'])
def home():
    return jsonify({"message":"Welcome to the hotel API"}),200

@hotel_routes.route('/create_hotel',methods=['POST'])
@jwt_required()
@role_required(['owner','admin'])
@rate_limit("3 per minute")
def create_hotel():
    """
    Create hotel
    ---
    tags:
      - Hotels
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            location:
              type: string
            rating:
              type: number
            price:
              type: number
    responses:
      201:
        description: Hotel created
    """
    data=request.get_json()
    name=data.get('name')
    description=data.get('description')
    location=data.get('location')
    rating=data.get('rating')
    price=data.get('price')
    new_hotel=hotel(name=name,description=description,location=location,rating=rating,price=price)
    db.session.add(new_hotel)
    db.session.commit()
    return jsonify({"message":"Hotel created successfully"}),201

@hotel_routes.route('/get_hotel_by_id',methods=['GET'])
@jwt_required()
def get_hotel_by_id():
    """
    Get hotel by ID
    ---
    tags:
      - Hotels
    security:
      - Bearer: []
    parameters:
      - name: hotel_id
        in: query
        type: integer
        required: true
    responses:
      200:
        description: Hotel data
    """
    hotel_id=request.args.get('hotel_id')
    hotel=hotel.query.filter_by(id=hotel_id).first()
    if not hotel:
        return jsonify({"error":"Hotel not found"}),404
    return jsonify({"hotel":hotel.to_dict()}),200

@hotel_routes.route('/get_all_hotels',methods=['GET'])
def get_all_hotels():
    """
    Get all hotels
    ---
    tags:
      - Hotels
    responses:
      200:
        description: List of hotels
    """
    hotels=hotel.query.all()
    return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200

@hotel_routes.route('/get_hotels_by_name',methods=['GET'])
# @jwt_required()
def get_hotels_by_name():
    name=request.args.get('name')
    hotels=hotel.query.filter_by(name=name).all()
    return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200

@hotel_routes.route('/get_hotels_by_location',methods=['GET'])
# @jwt_required()
def get_hotels_by_location():
    """
    Get hotels by location
    ---
    tags:
      - Hotels
    parameters:
      - name: location
        in: query
        type: string
        required: true
    responses:
      200:
        description: List of hotels
    """
    location=request.args.get('location')
    hotels=hotel.query.filter_by(location=location).all()
    return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200

@hotel_routes.route('/get_hotels_by_rating',methods=['GET'])
# @jwt_required()
def get_hotels_by_rating():
    rating=request.args.get('rating')
    hotels=hotel.query.filter_by(rating=rating).all()
    return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200       

@hotel_routes.route('/get_hotels_by_price',methods=['GET'])
# @jwt_required()
def get_hotels_by_price():
    price=request.args.get('price')
    hotels=hotel.query.filter_by(price=price).all()
    return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200

@hotel_routes.route('/get_hotels_by_price_range',methods=['GET'])
# @jwt_required()
def get_hotels_by_price_range():
    price_range=request.args.get('price_range')
    try:
        price_range=price_range.split('-')
        price_range=[int(price) for price in price_range]
        hotels=hotel.query.filter(hotel.price>=price_range[0],hotel.price<=price_range[1]).all()
        return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200
    except ValueError:
        return jsonify({"error":"Invalid price range"}),400

@hotel_routes.route('/get_hotels_by_date',methods=['GET'])
# @jwt_required()
def get_hotels_by_date():
    date=request.args.get('date')
    hotels=hotel.query.filter_by(date=date).all()   
    return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200
   

@hotel_routes.route('/get_hotels_by_date_range',methods=['GET'])
# @jwt_required()
def get_hotels_by_date_range():
    date_range=request.args.get('date_range')
    try:
        date_range=date_range.split('-')
        date_range=[datetime.strptime(date,'%Y-%m-%d') for date in date_range]
        hotels=hotel.query.filter(hotel.created_at>=date_range[0],hotel.created_at<=date_range[1]).all()
        return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200
    except ValueError:
        return jsonify({"error":"Invalid date range"}),400

@hotel_routes.route('/get_hotels_by_updated_at_range',methods=['GET'])
# @jwt_required()
def get_hotels_by_updated_at_range():
    updated_at_range=request.args.get('updated_at_range')
    try:
        updated_at_range=updated_at_range.split('-')
        updated_at_range=[datetime.strptime(updated_at,'%Y-%m-%d') for updated_at in updated_at_range]
        hotels=hotel.query.filter(hotel.updated_at>=updated_at_range[0],hotel.updated_at<=updated_at_range[1]).all()
        return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200
    except ValueError:
        return jsonify({"error":"Invalid updated at range"}),400

@hotel_routes.route('/get_hotels_by_rating_range',methods=['GET'])
# @jwt_required()
def get_hotels_by_rating_range():
    rating_range=request.args.get('rating_range')
    try:
        rating_range=rating_range.split('-')
        rating_range=[int(rating) for rating in rating_range]
        hotels=hotel.query.filter(hotel.rating>=rating_range[0],hotel.rating<=rating_range[1]).all()
        return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200
    except ValueError:
        return jsonify({"error":"Invalid rating range"}),400
