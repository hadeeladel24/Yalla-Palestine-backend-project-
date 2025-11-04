from flask import Flask,request,jsonify,Blueprint
from models import trips,db
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import datetime
from routes.role_req import role_required
from routes.rate_limit import rate_limit
from utils.validation import require_json, validate_fields, parse_date, ValidationError
trips_routes=Blueprint('trips',__name__)

@trips_routes.route('/',methods=['GET'])
def home():
    return jsonify({"message":"Welcome to the trips API"}),200

@trips_routes.route('/create_trip',methods=['POST'])
@jwt_required()
@role_required(['admin'])
@rate_limit("3 per minute")
def create_trip():
    """
    Create trip
    ---
    tags:
      - Trips
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            torist_place_id:
              type: integer
            hotel_id:
              type: integer
            restaurant_id:
              type: integer
            start_date:
              type: string
            end_date:
              type: string
    responses:
      201:
        description: Trip created
    """
    try:
        data = require_json(request.get_json())
        validate_fields(data, {
            'start_date': {'required': True, 'type': 'string'},
            'end_date': {'required': True, 'type': 'string'},
            'torist_place_id': {'required': False, 'type': 'integer'},
            'hotel_id': {'required': False, 'type': 'integer'},
            'restaurant_id': {'required': False, 'type': 'integer'}
        })

        start_date = parse_date(data.get('start_date'), 'start_date')
        end_date = parse_date(data.get('end_date'), 'end_date')
        if start_date >= end_date:
            raise ValidationError('end_date must be after start_date', 400)

        trip=trips(
            user_id=get_jwt_identity(),
            torist_place_id=data.get('torist_place_id'),
            hotel_id=data.get('hotel_id'),
            restaurant_id=data.get('restaurant_id'),
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(trip)
        db.session.commit()
        return jsonify({"message":"Trip created successfully", "trip": trip.to_dict()}),201
    except ValidationError as e:
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@trips_routes.route('/get_trips_by_user_id',methods=['GET'])
#@jwt_required()
def get_trips_by_user_id():
    user_id=get_jwt_identity()
    trip=trips.query.filter_by(user_id=user_id).all()
    return jsonify({"trips": [trip.to_dict() for trip in trip]}),200

@trips_routes.route('/get_trips_by_torist_place_id',methods=['GET'])
#@jwt_required()
def get_trips_by_torist_place_id():
    torist_place_id=request.args.get('torist_place_id')
    trip=trips.query.filter_by(torist_place_id=torist_place_id).all()
    return jsonify({"trips": [trip.to_dict() for trip in trip]}),200

@trips_routes.route('/get_trips_by_hotel_id',methods=['GET'])
#@jwt_required()
def get_trips_by_hotel_id():
    hotel_id=request.args.get('hotel_id')
    trip=trips.query.filter_by(hotel_id=hotel_id).all()
    return jsonify({"trips": [trip.to_dict() for trip in trip]}),200

@trips_routes.route('/get_trips_by_restaurant_id',methods=['GET'])
#@jwt_required()
def get_trips_by_restaurant_id():
    restaurant_id=request.args.get('restaurant_id')
    trip=trips.query.filter_by(restaurant_id=restaurant_id).all()
    return jsonify({"trips": [trip.to_dict() for trip in trip]}),200

@trips_routes.route('/get_trips_by_start_date',methods=['GET'])
#@jwt_required()
def get_trips_by_start_date():
    start_date=request.args.get('start_date')
    trip=trips.query.filter_by(start_date=start_date).all()
    return jsonify({"trips": [trip.to_dict() for trip in trip]}),200

@trips_routes.route('/get_trips_by_end_date',methods=['GET'])
#@jwt_required()
def get_trips_by_end_date():
    end_date=request.args.get('end_date')
    trip=trips.query.filter_by(end_date=end_date).all()
    return jsonify({"trips": [trip.to_dict() for trip in trip]}),200

@trips_routes.route('/get_trips_by_created_at',methods=['GET'])
#@jwt_required()
def get_trips_by_created_at():
    created_at=request.args.get('created_at')
    trip=trips.query.filter_by(created_at=created_at).all()
    return jsonify({"trips": [trip.to_dict() for trip in trip]}),200

@trips_routes.route('/get_trips_by_updated_at',methods=['GET'])
#@jwt_required()
def get_trips_by_updated_at():
    updated_at=request.args.get('updated_at')
    trip=trips.query.filter_by(updated_at=updated_at).all()
    return jsonify({"trips": [trip.to_dict() for trip in trip]}),200

@trips_routes.route('/get_trips_by_created_at_range',methods=['GET'])
#@jwt_required()
def get_trips_by_created_at_range():
    created_at_range=request.args.get('created_at_range')
    try:
        created_at_range=created_at_range.split('-')
        created_at_range=[datetime.strptime(created_at,'%Y-%m-%d') for created_at in created_at_range]
        trip=trips.query.filter(trips.created_at>=created_at_range[0],trips.created_at<=created_at_range[1]).all()
        return jsonify({"trips": [trip.to_dict() for trip in trip]}),200
    except ValueError:
        return jsonify({"error":"Invalid created at range"}),400

@trips_routes.route('/get_all_trips',methods=['GET'])
#@jwt_required()
def get_all_trips():
    """
    Get all trips
    ---
    tags:
      - Trips
    responses:
      200:
        description: List of trips
    """
    trip=trips.query.all()
    return jsonify({"trips": [trip.to_dict() for trip in trip]}),200

@trips_routes.route('/update_trip/<int:trip_id>', methods=['PUT'])
@jwt_required()
@role_required(['user', 'admin'])
@rate_limit("3 per minute")
def update_trip(trip_id):
    """
    Update trip
    ---
    tags:
      - Trips
    security:
      - Bearer: []
    parameters:
      - name: trip_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            torist_place_id:
              type: integer
            hotel_id:
              type: integer
            restaurant_id:
              type: integer
            start_date:
              type: string
            end_date:
              type: string
    responses:
      200:
        description: Trip updated
      404:
        description: Trip not found
    """
    try:
        trip_obj = trips.query.get(trip_id)
        if not trip_obj:
            return jsonify({"error": "Trip not found"}), 404
        
        user_id = get_jwt_identity()
        
        # Check if user owns this trip
        if str(trip_obj.user_id) != user_id:
            return jsonify({"error": "Unauthorized"}), 403
        
        data = request.get_json()
        
        if data.get('torist_place_id') is not None:
            trip_obj.torist_place_id = data.get('torist_place_id')
        if data.get('hotel_id') is not None:
            trip_obj.hotel_id = data.get('hotel_id')
        if data.get('restaurant_id') is not None:
            trip_obj.restaurant_id = data.get('restaurant_id')
        if data.get('start_date'):
            trip_obj.start_date = datetime.strptime(data.get('start_date'), "%Y-%m-%d")
        if data.get('end_date'):
            trip_obj.end_date = datetime.strptime(data.get('end_date'), "%Y-%m-%d")
        
        trip_obj.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"message": "Trip updated successfully", "trip": trip_obj.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@trips_routes.route('/delete_trip/<int:trip_id>', methods=['DELETE'])
@jwt_required()
@role_required(['user', 'admin'])
@rate_limit("3 per minute")
def delete_trip(trip_id):
    """
    Delete trip
    ---
    tags:
      - Trips
    security:
      - Bearer: []
    parameters:
      - name: trip_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Trip deleted
      404:
        description: Trip not found
    """
    try:
        trip_obj = trips.query.get(trip_id)
        if not trip_obj:
            return jsonify({"error": "Trip not found"}), 404
        
        user_id = get_jwt_identity()
        
        # Check if user owns this trip
        if str(trip_obj.user_id) != user_id:
            return jsonify({"error": "Unauthorized"}), 403
        
        db.session.delete(trip_obj)
        db.session.commit()
        
        return jsonify({"message": "Trip deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500