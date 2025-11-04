from datetime import datetime
from flask import Blueprint,request,jsonify
from models import booking,db
from flask_jwt_extended import jwt_required,get_jwt_identity
from routes.rate_limit import rate_limit
from routes.role_req import role_required
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, booking, hotel, restaurant, User
from services.stripe_service import StripeService
from datetime import datetime
import os

booking_routes = Blueprint('booking', __name__)


@booking_routes.route('/hotel', methods=['POST'])
@jwt_required()
def create_hotel_booking():
    """
    Create hotel booking
    ---
    tags:
      - Bookings
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            hotel_id:
              type: integer
            check_in_date:
              type: string
            check_out_date:
              type: string
            number_of_rooms:
              type: integer
            number_of_guests:
              type: integer
    responses:
      201:
        description: Booking created
      400:
        description: Bad request
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        required_fields = ['hotel_id', 'check_in_date', 'check_out_date', 'number_of_rooms', 'number_of_guests']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'{field} is required'}), 400

        # Get hotel from DB
        hotels = hotel.query.get(data['hotel_id'])
        if not hotels:
            return jsonify({'success': False, 'message': 'Hotel not found'}), 404

        # Parse dates
        check_in_date = datetime.strptime(data['check_in_date'], '%Y-%m-%d')
        check_out_date = datetime.strptime(data['check_out_date'], '%Y-%m-%d')

        # Validate dates
        if check_in_date >= check_out_date:
            return jsonify({'success': False, 'message': 'Check-out date must be after check-in date'}), 400
        if check_in_date < datetime.now():
            return jsonify({'success': False, 'message': 'Check-in date must be in the future'}), 400

        # Calculate nights and base price
        nights = (check_out_date - check_in_date).days
        base_price = hotels.price * data['number_of_rooms'] * nights

        # Create booking instance
        bookings = booking(
            user_id=user_id,
            booking_type='hotel',
            hotel_id=hotels.id, 
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            number_of_rooms=data['number_of_rooms'],
            number_of_guests=data['number_of_guests'],
            special_requests=data.get('special_requests', ''),
            base_price=base_price,
            currency=os.getenv('CURRENCY', 'USD'),
            booking_status='pending',
            payment_status='pending'
        )

        
        bookings.calculate_total_price()

       
        db.session.add(bookings)
        db.session.commit()

     
        payment_result = StripeService.create_payment_intent(
            amount=bookings.total_price,  
            currency=bookings.currency.lower(),
            metadata={
                'booking_id': bookings.id,
                'booking_type': 'hotel',
                'hotel_id': hotels.id,
                'user_id': user_id,
                'confirmation_code': bookings.confirmation_code
            }
        )

        if not payment_result['success']:
           
            db.session.delete(bookings)
            db.session.commit()
            return jsonify({'success': False, 'message': 'Failed to create payment', 'error': payment_result.get('message')}), 500

        
        bookings.stripe_payment_intent_id = payment_result['payment_intent_id']
        bookings.payment_status = 'processing'
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Booking created successfully',
            'booking': bookings.to_dict(),
            'hotel': hotels.to_dict(),
            'payment': {
                'client_secret': payment_result['client_secret'],
                'payment_intent_id': payment_result['payment_intent_id'],
                'amount': bookings.total_price,
                'currency': bookings.currency
            },
            'stripe_public_key': os.getenv('STRIPE_PUBLIC_KEY')
        }), 201

    except ValueError as e:
        return jsonify({'success': False, 'message': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to create booking: {str(e)}'}), 500

@booking_routes.route('/restaurant', methods=['POST'])
@jwt_required()
def create_restaurant_booking():
    """
    Create restaurant booking
    ---
    tags:
      - Bookings
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            restaurant_id:
              type: integer
            booking_date:
              type: string
            booking_time:
              type: string
            number_of_guests:
              type: integer
    responses:
      201:
        description: Booking created
      400:
        description: Bad request
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['restaurant_id', 'booking_date', 'booking_time', 'number_of_guests']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400
        
        # Get restaurant
        restaurants = restaurant.query.get(data['restaurant_id'])
        if not restaurants:
            return jsonify({
                'success': False,
                'message': 'Restaurant not found'
            }), 404
        
        # Parse booking date
        booking_date = datetime.strptime(data['booking_date'], '%Y-%m-%d')
        
        # Validate date
        if booking_date < datetime.now():
            return jsonify({
                'success': False,
                'message': 'Booking date must be in the future'
            }), 400
        
        # Calculate base price
        base_price = 10.0 * float(data['number_of_guests'])
        
        # Create booking
        bookings = booking(
            user_id=user_id,
            booking_type='restaurant',
            restaurant_id=restaurants.id,
            booking_date=booking_date,
            booking_time=data['booking_time'],
            number_of_guests=data['number_of_guests'],
            special_requests=data.get('special_requests', ''),
            base_price=base_price,
            currency=os.getenv('CURRENCY', 'USD'),
            booking_status='pending',
            payment_status='pending'
        )
        
        # Calculate total price
        bookings.calculate_total_price()
        
        # Save booking
        db.session.add(bookings)
        db.session.commit()
        
        # Create Stripe Payment Intent
        payment_result = StripeService.create_payment_intent(
            amount=bookings.total_price,
            currency=bookings.currency.lower(),
            metadata={
                'booking_id': bookings.id,
                'booking_type': 'restaurant',
                'restaurant_id': restaurants.id,
                'user_id': user_id,
                'confirmation_code': bookings.confirmation_code
            }
        )
        
        if not payment_result['success']:
            db.session.delete(bookings)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'message': 'Failed to create payment',
                'error': payment_result.get('message')
            }), 500
        
        # Update booking with payment intent
        bookings.stripe_payment_intent_id = payment_result['payment_intent_id']
        bookings.payment_status = 'processing'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Restaurant booking created successfully',
            'booking': bookings.to_dict(),
            'restaurant': restaurants.to_dict(),
            'payment': {
                'client_secret': payment_result['client_secret'],
                'payment_intent_id': payment_result['payment_intent_id'],
                'amount': bookings.total_price,
                'currency': bookings.currency
            },
            'stripe_public_key': os.getenv('STRIPE_PUBLIC_KEY')
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create booking: {str(e)}'
        }), 500



@booking_routes.route('/<int:booking_id>/confirm-payment', methods=['POST'])
@jwt_required()
def confirm_payment(booking_id):
    """
    Confirm payment
    ---
    tags:
      - Bookings
    security:
      - Bearer: []
    parameters:
      - name: booking_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Payment confirmed
      404:
        description: Booking not found
    """
    try:
        user_id = get_jwt_identity()
        
        # Get booking
        bookings = booking.query.get(booking_id)
        if not bookings:
            return jsonify({
                'success': False,
                'message': 'Booking not found'
            }), 404
        
        # Check if user owns this booking
        if bookings.user_id != int(user_id):
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 403
        
        # Verify payment with Stripe
        payment_result = StripeService.retrieve_payment_intent(bookings.stripe_payment_intent_id)
        
        if not payment_result['success']:
            return jsonify({
                'success': False,
                'message': 'Failed to verify payment'
            }), 500
        
        # Check if payment succeeded
        if payment_result['status'] == 'succeeded':
            bookings.payment_status = 'paid'
            bookings.booking_status = 'confirmed'
            bookings.payment_date = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Payment confirmed successfully',
                'booking': bookings.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'Payment not completed. Status: {payment_result["status"]}'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to confirm payment: {str(e)}'
        }), 500


@booking_routes.route('/my', methods=['GET'])
@jwt_required()
def get_my_bookings():
    """
    List current user's bookings
    ---
    tags:
      - Bookings
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        
        required: false
      - name: per_page
        in: query
        type: integer
        required: false
      - name: booking_type
        in: query
        type: string
        required: false
        description: filter by 'hotel' or 'restaurant'
    responses:
      200:
        description: List of user's bookings
    """
    try:
        user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        btype = request.args.get('booking_type')

        query = booking.query.filter_by(user_id=int(user_id))
        if btype in ('hotel', 'restaurant'):
            query = query.filter_by(booking_type=btype)

        pagination = query.order_by(booking.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        items = [b.to_dict() for b in pagination.items]
        return jsonify({
            'success': True,
            'bookings': items,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
