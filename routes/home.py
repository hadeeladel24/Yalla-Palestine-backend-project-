from flask import Blueprint,request,jsonify
# extensions.py
from authlib.integrations.flask_client import OAuth

auth = OAuth()
homes=Blueprint('home',__name__)

@homes.route('/',methods=['GET'])
def home():
    return jsonify({"message":"Welcome to the Home API"}),200
