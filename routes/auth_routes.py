from datetime import timedelta
from flask import Blueprint, redirect,request,jsonify
from models import User,db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token,create_refresh_token, get_jwt,jwt_required,get_jwt_identity
import os
import dotenv
import jwt
from routes.role_req import role_required
from routes.rate_limit import rate_limit
from flask import url_for


from routes.home import auth
dotenv.load_dotenv()
 
ACCESS_TOKEN_EXPIRES=timedelta(hours=1) 
REFRESH_TOKEN_EXPIRES= timedelta(days=30)

auth_routes=Blueprint('auth',__name__)

google = auth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v3/',
     server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
    redirect_uri='http://127.0.0.1:5000/auth/authorize/google'
)




@auth_routes.route('/',methods=['GET'])
def home():
    return jsonify({"message":"Welcome to the auth API"}),200

@auth_routes.route('/register',methods=['POST'])
def register():
    """
    Register user
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
            role:
              type: string
    responses:
      201:
        description: User registered
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role') 

    hashed_password = generate_password_hash(password=password)

    user = User(username=username, email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_routes.route('/login/google')
def login_google():
    redirect_uri = url_for('auth.authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_routes.route('/authorize/google')
def authorize_google():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')  # Google عادةً يعطي userinfo هنا
    email = user_info.get('email')
    name = user_info.get('name', 'Unknown')

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=name, email=email, provider='google', role='user')
        db.session.add(user)
        db.session.commit()

    jwt_token = create_access_token(identity=user.id)
    return jsonify({
        "message": "Logged in with Google successfully",
        "token": jwt_token,
        "email": user.email
    }), 200





@auth_routes.route('/login', methods=['POST'])
@rate_limit("3 per minute")
def login():
    """
    Login user
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    try:
        # Check if JSON data exists
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
       
        email = data.get('email')
        if not email:
            return jsonify({
                "success": False,
                "message": "Email is required"
            }), 400
        
        # Get and validate password
        password = data.get('password')
        if not password:
            return jsonify({
                "success": False,
                "message": "Password is required"
            }), 400
        
        # Clean email (remove spaces, lowercase)
        email = email.strip().lower()
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check user exists and password is correct
        if not user or not user.check_password(password=password):
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401
        
        # Generate tokens
        access_token = create_access_token(identity=str(user.id),additional_claims={"role": user.role})
        refresh_token = create_refresh_token(identity=str(user.id),additional_claims={"role": user.role})
        
        # Return success response
        return jsonify({
            "success": True,
            "message": "Logged in successfully",
            "user": user.to_dict(),  # Add user info
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200
        
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({
            "success": False,
            "message": f"Login failed: {str(e)}"
        }), 500

@auth_routes.route('/refresh',methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh token
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: Token refreshed
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    new_access_token = create_access_token(identity=identity, additional_claims={"role": claims["role"]})
    return jsonify({"access_token": new_access_token}), 200

@auth_routes.route('/logout',methods=['POST'])
def logout():
    data=request.get_json() #refresh token is in the request body so we need to get it from the request body              
    refresh_token=data.get('refresh_token')
    return jsonify({"message":"Logged out successfully"}),200

@auth_routes.route('/verify_token',methods=['POST'])
def verify_token():
    data=request.get_json()
    access_token=data.get('access_token')
    return jsonify({"message":"Token verified successfully"}),200

@auth_routes.route('/get_user',methods=['GET'])
@jwt_required()
def get_user():
    """
    Get current user
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: User data
    """
    user_id=get_jwt_identity()
    user=User.query.get(user_id)
    return jsonify({"user":user.to_dict()}),200


@auth_routes.route('/get_all_users',methods=['GET'])
@jwt_required()
@role_required(['admin'])
def get_all_users():
    """
    Get all users (Admin only)
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: List of users
    """
    users=User.query.all()
    return jsonify({"users": [user.to_dict() for user in users]}),200

@auth_routes.route('/get_user_by_id',methods=['GET'])
@jwt_required()
@role_required(['admin'])
def get_user_by_id():
    user_id=request.args.get('user_id')
    user=User.query.get(user_id)
    return jsonify({"user":user.to_dict()}),200

 