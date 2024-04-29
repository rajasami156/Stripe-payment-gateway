from flask import Flask, jsonify, request, abort
import os
import stripe
from flask_cors import CORS
from stripe import Webhook
from stripe.error import SignatureVerificationError

app = Flask(__name__)
CORS(app)
# Stripe secret key
stripe_key=os.getenv("STRIPE_API_KEY")
stripe.api_key = stripe_key

@app.route('/create_checkout_session', methods=['POST'])
def create_checkout_session():
    data = request.json
    email = data.get('email')
    amount = float(data.get('amount')) 
    planName = data.get('planName')

    try:
        if amount < 0.10:
            return jsonify({'error': 'Amount must be at least $0.10'}), 400

        amount_cents = int(amount * 100)
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': str(planName),
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                },
            ],
            customer_email=email,
            mode='payment',
            success_url='<URL FOR SUCCESSFUL PAYMENT> /paymentSuccessful',
            cancel_url='<URL FOR CANCELLED PAYMENT> /paymentCancelled',
        )

        return jsonify({'sessionId': checkout_session.id}), 200
    except stripe.error.StripeError as e:
        # Handle other Stripe errors
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # Handle general errors
        return jsonify({'error': str(e)}), 500

   
@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = 'whsec_*******' 

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        print('PaymentIntent was successful!')
        print("PaymentIntent: ", payment_intent)
        # Your code to handle successful payment intent goes here
        # ...

        # Return a response to acknowledge receipt of the event
        return jsonify({'message': 'Webhook received and processed'}), 200
    else:
        # Other event types can be handled here
        return jsonify({'message': 'Event type not handled'}), 200

        
# Run the app
app.run(port=5000)
