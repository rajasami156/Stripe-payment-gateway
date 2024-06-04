import os
import stripe
from fastapi import HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_database("Api")

# Initialize Stripe with the secret key from environment variables
stripe.api_key = os.getenv("STRIPE_API_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

# Define a request model using Pydantic
class PaymentCheckoutSessionRequest(BaseModel):
    email: str
    amount: float
    planName: str
    base_url: str

# Function to create a Stripe checkout session
def create_payment_checkout_session(session_data: PaymentCheckoutSessionRequest):
    email = session_data.email
    amount = session_data.amount
    plan_name = session_data.planName
    base_url = session_data.base_url

    if amount < 0.10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be at least $0.10"
        )

    # Convert amount to cents for Stripe API
    amount_cents = int(amount * 100)

    try:
        # Create a Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': str(plan_name),
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                },
            ],
            customer_email=email,
            mode='payment',
            success_url=f"{base_url}/paymentSuccessful",
            cancel_url=f"{base_url}/paymentCancelled",
        )

        db.payment_tracking.insert_one({
            "email": session_data.email,
            "amount": session_data.amount,
            "status": "pending",
            "session_id": checkout_session.id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        return {"sessionId": checkout_session.id}

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Function to verify Stripe webhook
def verify_webhook(payload, sig_header, endpoint_secret):
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        return event
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
