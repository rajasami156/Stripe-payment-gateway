import json
import stripe
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Dict, Union,  Optional
import time
from pymongo.errors import PyMongoError
import random
import pickle
import hashlib
import math
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query, APIRouter, HTTPException, status, Depends, BackgroundTasks, Request, Body
from fastapi.responses import JSONResponse
import os
import tempfile
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient
import sys
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from bson.json_util import dumps
from fastapi.middleware.cors import CORSMiddleware
from stripe_payment import PaymentCheckoutSessionRequest, create_payment_checkout_session, verify_webhook
import base64
import logging
import pymongo 



app = FastAPI()
load_dotenv()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


# DATABASE SETUP

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_database("Api")
collection = db.get_collection("payment_tracking")




# STRIPE PAYMENT GATEWAY SETUP

stripe.api_key = os.getenv("STRIPE_API_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
logging.basicConfig(level=logging.INFO)

@app.post("/create_payment_checkout_session")
async def create_checkout_session(session_data: PaymentCheckoutSessionRequest):
    return create_payment_checkout_session(session_data)

@app.post("/stripe_webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    logging.info(f"Signature header: {sig_header}")
    logging.info(f"Endpoint secret: {endpoint_secret}")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        logging.error("Webhook error: Invalid payload")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logging.error(f"Webhook error: Invalid signature: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session['id']

        result = collection.update_one(
            {"session_id": session_id},
            {"$set": {"status": "confirmed", "updated_at": datetime.utcnow()}}
        )
        logging.info(f"Payment succeeded, updated document: {result.modified_count}")

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        session_id = payment_intent['id']
        result = collection.update_one(
            {"session_id": session_id},
            {"$set": {"status": "failed", "updated_at": datetime.utcnow()}}
        )
        logging.info(f"Payment failed, updated document: {result.modified_count}")

    elif event['type'] == 'payment_intent.canceled':
        payment_intent = event['data']['object']
        session_id = payment_intent['id']
        result = collection.update_one(
            {"session_id": session_id},
            {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
        )
        logging.info(f"Payment canceled, updated document: {result.modified_count}")

    return {"status": "success"}




# RETRIEVE STRIPE PAYMENT DATA OF A USER
@app.post("/retrieve_stripeUser_data")
async def stripe_payment_information_from_mongodb(email:str= Query(...)):
    try:
        document = collection.find_one({"email": email})
        if document is not None:
            return {
                "user_email": email, 
                "data": document.get("amount", "No data recorded"), 
                "status":document.get("status", "Payment status not mentioned"),
                "session_id":document.get("session_id", "Session ID isn't mentioned"),
                "created_at":document.get("created_at", "No Payment created"), 
                "updated_at":document.get("updated_at", "No Updates have been found")}                                                                                                                                                                 
        else:
            return {"error": "No record found for the given user email"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {str(e)}")




if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

