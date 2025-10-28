from flask import Flask,request,jsonify,Blueprint
from models import restaurant,db
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import datetime
from routes.role_req import role_required
from routes.rate_limit import rate_limit
resturent_routes=Blueprint('resturent',__name__)

@resturent_routes.route('/',methods=['GET'])
def home():
    return jsonify({"message":"Welcome to the resturent API"}),200

@resturent_routes.route('/create_resturent',methods=['POST'])
@jwt_required()
@role_required(['owner','admin'])
@rate_limit("3 per minute")
def create_resturent():
    """
    Create restaurant
    ---
    tags:
      - Restaurants
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
        description: Restaurant created
    """
    data=request.get_json()
    name=data.get('name')
    description=data.get('description')
    location=data.get('location')
    rating=data.get('rating')
    price=data.get('price')
    resturent=restaurant(name=name,description=description,location=location,rating=rating,price=price)
    db.session.add(resturent)
    db.session.commit()
    return jsonify({"message":"Resturent created successfully"}),201

@resturent_routes.route('/get_resturent_by_id',methods=['GET'])
def get_resturent_by_id():
    """
    Get restaurant by ID
    ---
    tags:
      - Restaurants
    parameters:
      - name: resturent_id
        in: query
        type: integer
        required: true
    responses:
      200:
        description: Restaurant data
    """
    resturent_id=request.args.get('resturent_id')
    resturent=restaurant.query.filter_by(id=resturent_id).first()
    if not resturent:
        return jsonify({"error":"Resturent not found"}),404
    return jsonify({"resturent":resturent.to_dict()}),200

@resturent_routes.route('/get_all_resturents',methods=['GET'])
def get_all_resturents():
    """
    Get all restaurants
    ---
    tags:
      - Restaurants
    responses:
      200:
        description: List of restaurants
    """
    resturents=restaurant.query.all()
    return jsonify({"resturents": [resturent.to_dict() for resturent in resturents]}),200

@resturent_routes.route('/get_resturents_by_name',methods=['GET'])
def get_resturents_by_name():
    name=request.args.get('name')
    resturents=restaurant.query.filter_by(name=name).all()
    return jsonify({"resturents": [resturent.to_dict() for resturent in resturents]}),200

@resturent_routes.route('/get_resturents_by_location',methods=['GET'])
def get_resturents_by_location():
    location=request.args.get('location')
    resturents=restaurant.query.filter_by(location=location).all()          
    return jsonify({"resturents": [resturent.to_dict() for resturent in resturents]}),200

@resturent_routes.route('/get_resturents_by_rating',methods=['GET'])
def get_resturents_by_rating():
    rating=request.args.get('rating')
    resturents=restaurant.query.filter_by(rating=rating).all()
    return jsonify({"resturents": [resturent.to_dict() for resturent in resturents]}),200

@resturent_routes.route('/get_resturents_by_price',methods=['GET'])     

def get_resturents_by_price():
    price=request.args.get('price')
    resturents=restaurant.query.filter_by(price=price).all()
    return jsonify({"resturents": [resturent.to_dict() for resturent in resturents]}),200

@resturent_routes.route('/get_resturents_by_price_range',methods=['GET'])

def get_resturents_by_price_range():
    price_range=request.args.get('price_range')
    try:
        price_range=price_range.split('-')
        price_range=[int(price) for price in price_range]
        resturents=restaurant.query.filter(restaurant.price>=price_range[0],restaurant.price<=price_range[1]).all()
        return jsonify({"resturents": [resturent.to_dict() for resturent in resturents]}),200
    except ValueError:
        return jsonify({"error":"Invalid price range"}),400

@resturent_routes.route('/get_resturents_by_date',methods=['GET'])

def get_resturents_by_date():
    date=request.args.get('date')
    resturents=restaurant.query.filter_by(created_at=date).all()              
    return jsonify({"resturents": [resturent.to_dict() for resturent in resturents]}),200

@resturent_routes.route('/get_resturents_by_updated_at_range',methods=['GET'])

def get_resturents_by_updated_at_range():
    updated_at_range=request.args.get('updated_at_range')
    try:
        updated_at_range=updated_at_range.split('-')
        updated_at_range=[datetime.strptime(updated_at,'%Y-%m-%d') for updated_at in updated_at_range]
        resturents=restaurant.query.filter(restaurant.updated_at>=updated_at_range[0],restaurant.updated_at<=updated_at_range[1]).all()
        return jsonify({"resturents": [resturent.to_dict() for resturent in resturents]}),200
    except ValueError:
        return jsonify({"error":"Invalid updated at range"}),400

@resturent_routes.route('/get_resturents_by_rating_range',methods=['GET'])

def get_resturents_by_rating_range():
    rating_range=request.args.get('rating_range')
    try:
        rating_range=rating_range.split('-')
        rating_range=[int(rating) for rating in rating_range]
        resturents=restaurant.query.filter(restaurant.rating>=rating_range[0],restaurant.rating<=rating_range[1]).all() 
        return jsonify({"resturents": [resturent.to_dict() for resturent in resturents]}),200
    except ValueError:
        return jsonify({"error":"Invalid rating range"}),400

@resturent_routes.route('/update_resturent/<int:restaurant_id>', methods=['PUT'])
@jwt_required()
@role_required(['owner', 'admin'])
@rate_limit("3 per minute")
def update_resturent(restaurant_id):
    """
    Update restaurant
    ---
    tags:
      - Restaurants
    security:
      - Bearer: []
    parameters:
      - name: restaurant_id
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
        description: Restaurant updated
      404:
        description: Restaurant not found
    """
    try:
        restaurant_obj = restaurant.query.get(restaurant_id)
        if not restaurant_obj:
            return jsonify({"error": "Restaurant not found"}), 404
        
        data = request.get_json()
        
        if data.get('name'):
            restaurant_obj.name = data.get('name')
        if data.get('description'):
            restaurant_obj.description = data.get('description')
        if data.get('location'):
            restaurant_obj.location = data.get('location')
        if data.get('rating') is not None:
            restaurant_obj.rating = data.get('rating')
        if data.get('price') is not None:
            restaurant_obj.price = data.get('price')
        
        restaurant_obj.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"message": "Restaurant updated successfully", "restaurant": restaurant_obj.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@resturent_routes.route('/delete_resturent/<int:restaurant_id>', methods=['DELETE'])
@jwt_required()
@role_required(['owner', 'admin'])
@rate_limit("3 per minute")
def delete_resturent(restaurant_id):
    """
    Delete restaurant
    ---
    tags:
      - Restaurants
    security:
      - Bearer: []
    parameters:
      - name: restaurant_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Restaurant deleted
      404:
        description: Restaurant not found
    """
    try:
        restaurant_obj = restaurant.query.get(restaurant_id)
        if not restaurant_obj:
            return jsonify({"error": "Restaurant not found"}), 404
        
        db.session.delete(restaurant_obj)
        db.session.commit()
        
        return jsonify({"message": "Restaurant deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

