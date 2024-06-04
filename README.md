# 💳 Stripe Payment Integration with Fastapi
### This project is a Flask application that integrates Stripe for processing payments. It provides functionalities for creating checkout sessions and handling Stripe webhooks.

## Setup
To set up and run this project:

Clone the repository to your local machine.
Install the required Python packages using pip. 
Replace <URL FOR SUCCESSFUL PAYMENT> and <URL FOR CANCELLED PAYMENT> in app.py with your actual URLs for successful and cancelled payments.

#### Create a .env file in the root directory and add your Stripe API key as:

STRIPE_API_KEY = sk_test_51oW151XH2ssDZJqtzh

SECRET_KEY = 3862e19431fe0b

## Usage

Start the Fastapi application by running uvicorn main:app --reload.
Access the provided endpoints:
Create Checkout Session: Send a POST request to http://localhost:5000/create_checkout_session with JSON data containing email, amount, and planName to create a new checkout session for payment processing.
Stripe Webhook: Configure your Stripe account's webhook endpoint to http://localhost:5000/stripe_webhook to handle events like successful payment intents.
Dependencies
Flask: Web framework for Python.
Stripe: Python library for Stripe API integration.
Flask-CORS: Extension for handling Cross-Origin Resource Sharing.
Configuration
Ensure that your Stripe account is correctly set up with the necessary products and plans. Update the endpoint_secret variable in app.py with your actual webhook secret key (whsec_*******).

## Contributing
Contributions to this project are welcome. Feel free to open issues or submit pull requests to enhance its functionality or fix any issues.

License
This project is licensed under the MIT License. See the LICENSE.md file for details.
