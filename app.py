from functools import wraps
from flask import Flask,request,jsonify
from models import db,User,torist_place,hotel,restaurant,booking,review,trips
from routes.auth_routes import auth_routes
from routes.booking_routes import booking_routes
from routes.hotel_routes import hotel_routes
from routes.resturent_routes import resturent_routes
from routes.reviews_routes import reviews_routes
from routes.sites_routes import sites_routes
from routes.trips_routes import trips_routes
import os
import dotenv
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth
from routes.home import auth,homes
from flasgger import Swagger
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, NotFound, MethodNotAllowed, UnprocessableEntity, TooManyRequests
from utils.validation import ValidationError
from routes.rate_limit import L
dotenv.load_dotenv()
app=Flask(__name__)

app.config['SECRET_KEY']=os.getenv('SECRET_KEY')  
app.config['JWT_SECRET_KEY']=os.getenv('JWT_SECRET_KEY') 
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
auth.init_app(app)
L.init_app(app)
jwt=JWTManager(app)

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Yalla Palestine API",
        "description": "Tourism booking API for Palestine",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using Bearer scheme"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)


app.register_blueprint(auth_routes,url_prefix='/auth')
app.register_blueprint(booking_routes,url_prefix='/booking')
app.register_blueprint(hotel_routes,url_prefix='/hotel')
app.register_blueprint(resturent_routes,url_prefix='/resturent')
app.register_blueprint(reviews_routes,url_prefix='/reviews')
app.register_blueprint(sites_routes,url_prefix='/sites')
app.register_blueprint(trips_routes,url_prefix='/trips')
app.register_blueprint(homes,url_prefix='/')


# Global error handlers returning consistent JSON
@app.errorhandler(ValidationError)
def handle_validation_error(err: ValidationError):
    return jsonify({"success": False, "error": err.message}), err.status_code


@app.errorhandler(BadRequest)
def handle_bad_request(err):
    return jsonify({"success": False, "error": "Bad request"}), 400


@app.errorhandler(Unauthorized)
def handle_unauthorized(err):
    return jsonify({"success": False, "error": "Unauthorized"}), 401


@app.errorhandler(Forbidden)
def handle_forbidden(err):
    return jsonify({"success": False, "error": "Forbidden"}), 403


@app.errorhandler(NotFound)
def handle_not_found(err):
    return jsonify({"success": False, "error": "Not found"}), 404


@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(err):
    return jsonify({"success": False, "error": "Method not allowed"}), 405


@app.errorhandler(UnprocessableEntity)
def handle_unprocessable(err):
    return jsonify({"success": False, "error": "Unprocessable entity"}), 422


@app.errorhandler(TooManyRequests)
def handle_too_many(err):
    return jsonify({"success": False, "error": "Too many requests"}), 429


@app.errorhandler(Exception)
def handle_generic_error(err):
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__=="__main__":
   with app.app_context():
   #  db.drop_all()
    db.create_all()
    app.run(debug=True) 

