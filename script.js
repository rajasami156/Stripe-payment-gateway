// This assumes that you've already included Stripe.js in your HTML as shown above

// Set your publishable API key here
var stripe = Stripe('<ENTER THE API KEY NEEDED FOR FRONT-END ALSO KNOWN AS PUBLIC KEY IN STRIPE>');

// Get references to the form and its elements
var form = document.getElementById('payment-form');
var emailInput = document.getElementById('email');
var amountInput = document.getElementById('amount');
var planNameInput = document.getElementById('plan-name');

form.addEventListener('submit', function(e) {
  e.preventDefault();

  // Create a new checkout session from the backend
  fetch('http://example.com:5000/create_checkout_session', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: emailInput.value,
      amount: amountInput.value,
      planName: planNameInput.value
    })
  }).then(function(response) {
    return response.json();
  }).then(function(session) {
    return stripe.redirectToCheckout({ sessionId: session.sessionId });
  }).then(function(result) {
    if (result.error) {
      alert(result.error.message);
    }
  }).catch(function(error) {
    console.error('Error:', error);
  });
});
