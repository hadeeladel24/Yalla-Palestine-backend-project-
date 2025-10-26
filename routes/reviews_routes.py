from flask import Flask,request,jsonify,Blueprint
from models import review,db
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import datetime
from routes.role_req import role_required
reviews_routes=Blueprint('reviews',__name__)

@reviews_routes.route('/',methods=['GET'])
def home():
    return jsonify({"message":"Welcome to the reviews API"}),200

@reviews_routes.route('/create_review',methods=['POST'])
@jwt_required()
@role_required(['user'])
def create_review():
    """
    Create review
    ---
    tags:
      - Reviews
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
            rating:
              type: number
            comment:
              type: string
    responses:
      201:
        description: Review created
    """
    data=request.get_json()
    review=review(
        user_id=get_jwt_identity(),
        torist_place_id=data.get('torist_place_id'),
        hotel_id=data.get('hotel_id'),
        restaurant_id=data.get('restaurant_id'),
        rating=data.get('rating'),
        comment=data.get('comment')
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"message":"Review created successfully"}),201

@reviews_routes.route('/get_reviews_by_user_id',methods=['GET'])
@jwt_required()
def get_reviews_by_user_id():
    """
    Get reviews by user ID
    ---
    tags:
      - Reviews
    security:
      - Bearer: []
    responses:
      200:
        description: List of reviews
    """
    user_id=get_jwt_identity()
    reviews=review.query.filter_by(user_id=user_id).all()               
    return jsonify({"reviews": [review.to_dict() for review in reviews]}),200

@reviews_routes.route('/get_reviews_by_torist_place_id',methods=['GET'])

def get_reviews_by_torist_place_id():
    torist_place_id=request.args.get('torist_place_id')
    reviews=review.query.filter_by(torist_place_id=torist_place_id).all()               
    return jsonify({"reviews": [review.to_dict() for review in reviews]}),200

@reviews_routes.route('/get_reviews_by_hotel_id',methods=['GET'])
def get_reviews_by_hotel_id():
    hotel_id=request.args.get('hotel_id')
    reviews=review.query.filter_by(hotel_id=hotel_id).all()               
    return jsonify({"reviews": [review.to_dict() for review in reviews]}),200

@reviews_routes.route('/get_reviews_by_restaurant_id',methods=['GET'])

def get_reviews_by_restaurant_id():
    restaurant_id=request.args.get('restaurant_id')
    reviews=review.query.filter_by(restaurant_id=restaurant_id).all()               

@reviews_routes.route('/get_reviews_by_rating',methods=['GET'])

def get_reviews_by_rating():
    rating=request.args.get('rating')
    reviews=review.query.filter_by(rating=rating).all()               
    return jsonify({"reviews": [review.to_dict() for review in reviews]}),200

@reviews_routes.route('/get_reviews_by_comment',methods=['GET'])

def get_reviews_by_comment():
    comment=request.args.get('comment')
    reviews=review.query.filter_by(comment=comment).all()                       
    return jsonify({"reviews": [review.to_dict() for review in reviews]}),200

@reviews_routes.route('/get_reviews_by_created_at',methods=['GET'])
def get_reviews_by_created_at():
    created_at=request.args.get('created_at')
    reviews=review.query.filter_by(created_at=created_at).all()                       
    return jsonify({"reviews": [review.to_dict() for review in reviews]}),200

@reviews_routes.route('/get_reviews_by_updated_at',methods=['GET'])
def get_reviews_by_updated_at():
    updated_at=request.args.get('updated_at')
    reviews=review.query.filter_by(updated_at=updated_at).all()                       

@reviews_routes.route('/get_reviews_by_rating_range',methods=['GET'])
def get_reviews_by_rating_range():
    rating_range=request.args.get('rating_range')
    try:
        rating_range=rating_range.split('-')
        rating_range=[int(rating) for rating in rating_range]
        reviews=review.query.filter(review.rating>=rating_range[0],review.rating<=rating_range[1]).all()
        return jsonify({"reviews": [review.to_dict() for review in reviews]}),200
    except ValueError:
        return jsonify({"error":"Invalid rating range"}),400

@reviews_routes.route('/get_reviews_by_comment_range',methods=['GET'])
def get_reviews_by_comment_range():
    comment_range=request.args.get('comment_range')
    try:
        comment_range=comment_range.split('-')
        comment_range=[int(comment) for comment in comment_range]
        reviews=review.query.filter(review.comment>=comment_range[0],review.comment<=comment_range[1]).all()
        return jsonify({"reviews": [review.to_dict() for review in reviews]}),200
    except ValueError:
        return jsonify({"error":"Invalid comment range"}),400

@reviews_routes.route('/get_reviews_by_created_at_range',methods=['GET'])
def get_reviews_by_created_at_range():
    created_at_range=request.args.get('created_at_range')
    try:
        created_at_range=created_at_range.split('-')
        created_at_range=[datetime.strptime(created_at,'%Y-%m-%d') for created_at in created_at_range]
        reviews=review.query.filter(review.created_at>=created_at_range[0],review.created_at<=created_at_range[1]).all()
        return jsonify({"reviews": [review.to_dict() for review in reviews]}),200
    except ValueError:
        return jsonify({"error":"Invalid created at range"}),400

@reviews_routes.route('/get_reviews_by_updated_at_range',methods=['GET'])
def get_reviews_by_updated_at_range():
    updated_at_range=request.args.get('updated_at_range')
    try:
        updated_at_range=updated_at_range.split('-')
        updated_at_range=[datetime.strptime(updated_at,'%Y-%m-%d') for updated_at in updated_at_range]
        reviews=review.query.filter(review.updated_at>=updated_at_range[0],review.updated_at<=updated_at_range[1]).all()
        return jsonify({"reviews": [review.to_dict() for review in reviews]}),200
    except ValueError:
        return jsonify({"error":"Invalid updated at range"}),40