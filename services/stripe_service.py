import stripe
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class StripeService:
    """Service class for handling Stripe payments"""
    
    @staticmethod
    def create_payment_intent(amount, currency='usd', metadata=None):
        """
        Create a Stripe Payment Intent
        
        Args:
            amount: Amount in smallest currency unit (cents for USD)
            currency: Currency code (default: 'usd')
            metadata: Additional data to attach to payment
        
        Returns:
            Payment Intent object
        """
        try:
            # Convert amount to cents (Stripe requires smallest unit)
            amount_cents = int(amount * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': amount,
                'currency': currency,
                'status': payment_intent.status
            }
            
        except stripe.error.CardError as e:
            return {
                'success': False,
                'error': 'card_error',
                'message': str(e.user_message)
            }
        except stripe.error.InvalidRequestError as e:
            return {
                'success': False,
                'error': 'invalid_request',
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'unknown_error',
                'message': str(e)
            }
    
    @staticmethod
    def confirm_payment_intent(payment_intent_id):
        """
        Confirm a payment intent
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
        
        Returns:
            Payment Intent confirmation result
        """
        try:
            payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'status': payment_intent.status,
                'amount': payment_intent.amount / 100,
                'currency': payment_intent.currency
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id):
        """
        Retrieve payment intent details
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
        
        Returns:
            Payment Intent details
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'status': payment_intent.status,
                'amount': payment_intent.amount / 100,
                'currency': payment_intent.currency,
                'payment_method': payment_intent.payment_method,
                'created': payment_intent.created
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def cancel_payment_intent(payment_intent_id):
        """
        Cancel a payment intent
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
        
        Returns:
            Cancellation result
        """
        try:
            payment_intent = stripe.PaymentIntent.cancel(payment_intent_id)
            
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'status': payment_intent.status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def create_refund(payment_intent_id, amount=None, reason=None):
        """
        Create a refund for a payment
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
            amount: Amount to refund (None for full refund)
            reason: Reason for refund (optional)
        
        Returns:
            Refund result
        """
        try:
            refund_data = {'payment_intent': payment_intent_id}
            
            if amount:
                refund_data['amount'] = int(amount * 100)
            
            if reason:
                refund_data['reason'] = reason
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                'success': True,
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'currency': refund.currency,
                'status': refund.status,
                'reason': refund.reason
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def create_customer(email, name=None, metadata=None):
        """
        Create a Stripe customer
        
        Args:
            email: Customer email
            name: Customer name (optional)
            metadata: Additional customer data (optional)
        
        Returns:
            Customer object
        """
        try:
            customer_data = {'email': email}
            
            if name:
                customer_data['name'] = name
            
            if metadata:
                customer_data['metadata'] = metadata
            
            customer = stripe.Customer.create(**customer_data)
            
            return {
                'success': True,
                'customer_id': customer.id,
                'email': customer.email,
                'name': customer.name
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def verify_webhook_signature(payload, signature, webhook_secret):
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Request body
            signature: Stripe-Signature header
            webhook_secret: Webhook secret from Stripe
        
        Returns:
            Event object if valid, None if invalid
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return event
        except ValueError:
            return None
        except stripe.error.SignatureVerificationError:
            return None