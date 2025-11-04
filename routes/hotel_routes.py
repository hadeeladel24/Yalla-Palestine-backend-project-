from flask import Blueprint,request,jsonify
from models import hotel,db
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import datetime
from routes.rate_limit import rate_limit
from routes.role_req import role_required
from utils.validation import require_json, validate_fields
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
    try:
        data = require_json(request.get_json())
        validate_fields(data, {
            'name': {'required': True, 'type': 'string', 'min_length': 2, 'max_length': 100},
            'description': {'required': True, 'type': 'string', 'min_length': 5, 'max_length': 200},
            'location': {'required': True, 'type': 'string', 'min_length': 2, 'max_length': 100},
            'rating': {'required': True, 'type': 'number', 'min': 0, 'max': 5},
            'price': {'required': True, 'type': 'number', 'min': 0}
        })

        new_hotel=hotel(
            name=data.get('name').strip(),
            description=data.get('description').strip(),
            location=data.get('location').strip(),
            rating=data.get('rating'),
            price=data.get('price')
        )
        db.session.add(new_hotel)
        db.session.commit()
        return jsonify({"message":"Hotel created successfully", "hotel": new_hotel.to_dict()}),201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

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
    hotel_obj=hotel.query.filter_by(id=hotel_id).first()
    if not hotel_obj:
        return jsonify({"error":"Hotel not found"}),404
    return jsonify({"hotel":hotel_obj.to_dict()}),200

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
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        pagination = hotel.query.paginate(page=page, per_page=per_page, error_out=False)
        items = [h.to_dict() for h in pagination.items]
        return jsonify({
            "hotels": items,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages
            }
        }),200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@hotel_routes.route('/get_hotels_by_name',methods=['GET'])
def get_hotels_by_name():
    """
    Get hotels by name
    ---
    tags:
      - Hotels
    parameters:
      - name: name
        in: query
        type: string
        required: true
    responses:
      200:
        description: List of hotels
    """
    name=request.args.get('name')
    hotels=hotel.query.filter_by(name=name).all()
    return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200

@hotel_routes.route('/get_hotels_by_location',methods=['GET'])
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
def get_hotels_by_rating():
    """
    Get hotels by rating
    ---
    tags:
      - Hotels
    parameters:
      - name: rating
        in: query
        type: number
        required: true
    responses:
      200:
        description: List of hotels
    """
    rating=request.args.get('rating')
    hotels=hotel.query.filter_by(rating=rating).all()
    return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200       

@hotel_routes.route('/get_hotels_by_price',methods=['GET'])
def get_hotels_by_price():
    """
    Get hotels by exact price
    ---
    tags:
      - Hotels
    parameters:
      - name: price
        in: query
        type: number
        required: true
    responses:
      200:
        description: List of hotels
    """
    price=request.args.get('price')
    hotels=hotel.query.filter_by(price=price).all()
    return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200

@hotel_routes.route('/get_hotels_by_price_range',methods=['GET'])
def get_hotels_by_price_range():
    """
    Get hotels by price range
    ---
    tags:
      - Hotels
    parameters:
      - name: price_range
        in: query
        type: string
        required: true
        description: "min-max"
    responses:
      200:
        description: List of hotels
      400:
        description: Invalid range
    """
    price_range=request.args.get('price_range')
    try:
        price_range=price_range.split('-')
        price_range=[int(price) for price in price_range]
        hotels=hotel.query.filter(hotel.price>=price_range[0],hotel.price<=price_range[1]).all()
        return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200
    except ValueError:
        return jsonify({"error":"Invalid price range"}),400

@hotel_routes.route('/get_hotels_by_date',methods=['GET'])
def get_hotels_by_date():
    """
    Get hotels by created date
    ---
    tags:
      - Hotels
    parameters:
      - name: date
        in: query
        type: string
        required: true
        description: YYYY-MM-DD
    responses:
      200:
        description: List of hotels
    """
    date=request.args.get('date')
    hotels=hotel.query.filter_by(date=date).all()   
    return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200
   

@hotel_routes.route('/get_hotels_by_date_range',methods=['GET'])
def get_hotels_by_date_range():
    """
    Get hotels by created date range
    ---
    tags:
      - Hotels
    parameters:
      - name: date_range
        in: query
        type: string
        required: true
        description: "YYYY-MM-DD-YYYY-MM-DD"
    responses:
      200:
        description: List of hotels
      400:
        description: Invalid range
    """
    date_range=request.args.get('date_range')
    try:
        date_range=date_range.split('-')
        date_range=[datetime.strptime(date,'%Y-%m-%d') for date in date_range]
        hotels=hotel.query.filter(hotel.created_at>=date_range[0],hotel.created_at<=date_range[1]).all()
        return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200
    except ValueError:
        return jsonify({"error":"Invalid date range"}),400

@hotel_routes.route('/get_hotels_by_updated_at_range',methods=['GET'])
def get_hotels_by_updated_at_range():
    """
    Get hotels by updated date range
    ---
    tags:
      - Hotels
    parameters:
      - name: updated_at_range
        in: query
        type: string
        required: true
        description: "YYYY-MM-DD-YYYY-MM-DD"
    responses:
      200:
        description: List of hotels
      400:
        description: Invalid range
    """
    updated_at_range=request.args.get('updated_at_range')
    try:
        updated_at_range=updated_at_range.split('-')
        updated_at_range=[datetime.strptime(updated_at,'%Y-%m-%d') for updated_at in updated_at_range]
        hotels=hotel.query.filter(hotel.updated_at>=updated_at_range[0],hotel.updated_at<=updated_at_range[1]).all()
        return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200
    except ValueError:
        return jsonify({"error":"Invalid updated at range"}),400

@hotel_routes.route('/get_hotels_by_rating_range',methods=['GET'])
def get_hotels_by_rating_range():
    """
    Get hotels by rating range
    ---
    tags:
      - Hotels
    parameters:
      - name: rating_range
        in: query
        type: string
        required: true
        description: "min-max"
    responses:
      200:
        description: List of hotels
      400:
        description: Invalid range
    """
    rating_range=request.args.get('rating_range')
    try:
        rating_range=rating_range.split('-')
        rating_range=[int(rating) for rating in rating_range]
        hotels=hotel.query.filter(hotel.rating>=rating_range[0],hotel.rating<=rating_range[1]).all()
        return jsonify({"hotels": [hotel.to_dict() for hotel in hotels]}),200
    except ValueError:
        return jsonify({"error":"Invalid rating range"}),400

@hotel_routes.route('/update_hotel/<int:hotel_id>', methods=['PUT'])
@jwt_required()
@role_required(['owner', 'admin'])
@rate_limit("3 per minute")
def update_hotel(hotel_id):
    """
    Update hotel
    ---
    tags:
      - Hotels
    security:
      - Bearer: []
    parameters:
      - name: hotel_id
        in: path
        type: integer
        required: true
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
      200:
        description: Hotel updated
      404:
        description: Hotel not found
    """
    try:
        hotel_obj = hotel.query.get(hotel_id)
        if not hotel_obj:
            return jsonify({"error": "Hotel not found"}), 404
        
        data = request.get_json()
        
        if data.get('name'):
            hotel_obj.name = data.get('name')
        if data.get('description'):
            hotel_obj.description = data.get('description')
        if data.get('location'):
            hotel_obj.location = data.get('location')
        if data.get('rating') is not None:
            hotel_obj.rating = data.get('rating')
        if data.get('price') is not None:
            hotel_obj.price = data.get('price')
        
        hotel_obj.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"message": "Hotel updated successfully", "hotel": hotel_obj.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@hotel_routes.route('/delete_hotel/<int:hotel_id>', methods=['DELETE'])
@jwt_required()
@role_required(['owner', 'admin'])
@rate_limit("3 per minute")
def delete_hotel(hotel_id):
    """
    Delete hotel
    ---
    tags:
      - Hotels
    security:
      - Bearer: []
    parameters:
      - name: hotel_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Hotel deleted
      404:
        description: Hotel not found
    """
    try:
        hotel_obj = hotel.query.get(hotel_id)
        if not hotel_obj:
            return jsonify({"error": "Hotel not found"}), 404
        
        db.session.delete(hotel_obj)
        db.session.commit()
        
        return jsonify({"message": "Hotel deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500