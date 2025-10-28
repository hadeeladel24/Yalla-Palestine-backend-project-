from flask import Flask,request,jsonify,Blueprint
from models import torist_place,db
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import datetime
from routes.rate_limit import rate_limit
from routes.role_req import role_required
sites_routes=Blueprint('sites',__name__)

@sites_routes.route('/',methods=['GET'])
def home():
    return jsonify({"message":"Welcome to the sites API"}),200

@sites_routes.route('/create_site', methods=['POST'])
@jwt_required()
@role_required(['owner','admin'])
@rate_limit("3 per minute") 
def create_site():
    """
    Create tourist site
    ---
    tags:
      - Sites
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
        description: Site created
    """
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    location = data.get('location')
    rating = data.get('rating')
    price = data.get('price')

  
    if not all([name, description, location, rating, price]):
        return jsonify({"msg": "All fields are required"}), 400

    site = torist_place(
        name=name,
        description=description,
        location=location,
        rating=rating,
        price=price
    )

    db.session.add(site)
    db.session.commit()
    return jsonify({"message": "Site created successfully"}), 201


@sites_routes.route('/get_sites',methods=['GET'])
# @jwt_required()
def get_sites():
    """
    Get all sites
    ---
    tags:
      - Sites
    responses:
      200:
        description: List of sites
    """
    sites=torist_place.query.all()
    return jsonify({"sites": [site.to_dict() for site in sites]}),200

@sites_routes.route('/get_site_by_id',methods=['GET'])
# @jwt_required()
def get_site_by_id():
    """
    Get site by ID
    ---
    tags:
      - Sites
    parameters:
      - name: id
        in: query
        type: integer
        required: true
    responses:
      200:
        description: Site data
    """
    id=request.args.get('id')
    site=torist_place.query.filter_by(id=id).first()
    return jsonify({"site": site.to_dict()}),200

@sites_routes.route('/get_site_by_name',methods=['GET'])
# @jwt_required()
def get_site_by_name():
    name=request.args.get('name')
    site=torist_place.query.filter_by(name=name).first()
    return jsonify({"site": site.to_dict()}),200

@sites_routes.route('/get_site_by_location',methods=['GET'])
# @jwt_required()
def get_site_by_location():
    location=request.args.get('location')
    site=torist_place.query.filter_by(location=location).first()
    return jsonify({"site": site.to_dict()}),200

@sites_routes.route('/get_site_by_description',methods=['GET'])
# @jwt_required()
def get_site_by_description():
    description=request.args.get('description')
    site=torist_place.query.filter_by(description=description).first()
    return jsonify({"site": site.to_dict()}),200

@sites_routes.route('/get_site_by_created_at',methods=['GET'])
# @jwt_required()
def get_site_by_created_at():
    created_at=request.args.get('created_at')
    site=torist_place.query.filter_by(created_at=created_at).first()    
    return jsonify({"site": site.to_dict()}),200

@sites_routes.route('/get_site_by_updated_at',methods=['GET'])
# @jwt_required()
def get_site_by_updated_at():
    updated_at=request.args.get('updated_at')
    site=torist_place.query.filter_by(updated_at=updated_at).first()
    return jsonify({"site": site.to_dict()}),200

@sites_routes.route('/get_site_by_rating_range',methods=['GET'])
#@jwt_required()
def get_site_by_rating_range():
    rating_range=request.args.get('rating_range')
    try:
        rating_range=rating_range.split('-')
        rating_range=[int(rating) for rating in rating_range]
        sites=torist_place.query.filter(torist_place.rating>=rating_range[0],torist_place.rating<=rating_range[1]).all()
        return jsonify({"sites": [site.to_dict() for site in sites]}),200
    except ValueError:
        return jsonify({"error":"Invalid rating range"}),400

@sites_routes.route('/update_site/<int:site_id>', methods=['PUT'])
@jwt_required()
@role_required(['owner', 'admin'])
@rate_limit("3 per minute")
def update_site(site_id):
    """
    Update tourist site
    ---
    tags:
      - Sites
    security:
      - Bearer: []
    parameters:
      - name: site_id
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
        description: Site updated
      404:
        description: Site not found
    """
    try:
        site = torist_place.query.get(site_id)
        if not site:
            return jsonify({"error": "Site not found"}), 404
        
        data = request.get_json()
        
        if data.get('name'):
            site.name = data.get('name')
        if data.get('description'):
            site.description = data.get('description')
        if data.get('location'):
            site.location = data.get('location')
        if data.get('rating') is not None:
            site.rating = data.get('rating')
        if data.get('price') is not None:
            site.price = data.get('price')
        
        site.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"message": "Site updated successfully", "site": site.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@sites_routes.route('/delete_site/<int:site_id>', methods=['DELETE'])
@jwt_required()
@role_required(['owner', 'admin'])
@rate_limit("3 per minute")
def delete_site(site_id):
    """
    Delete tourist site
    ---
    tags:
      - Sites
    security:
      - Bearer: []
    parameters:
      - name: site_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Site deleted
      404:
        description: Site not found
    """
    try:
        site = torist_place.query.get(site_id)
        if not site:
            return jsonify({"error": "Site not found"}), 404
        
        db.session.delete(site)
        db.session.commit()
        
        return jsonify({"message": "Site deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

                                                            
