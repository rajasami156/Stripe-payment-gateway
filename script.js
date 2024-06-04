// Set your publishable API key here
var stripe = Stripe('pk_test_51P8Va151dGGYesBMzWd');

// Get references to the form and its elements
var form = document.getElementById('payment-form');
var emailInput = document.getElementById('email');
var amountInput = document.getElementById('amount');
var planNameInput = document.getElementById('plan-name');
var baseUrlInput = document.getElementById('base-url');

form.addEventListener('submit', function(e) {
  e.preventDefault();

  // Create a new checkout session from the backend
  var data = {
    email: emailInput.value,
    amount: parseFloat(amountInput.value),
    planName: planNameInput.value,
    base_url: baseUrlInput.value
  };

  console.log('Data being sent:', data); // Debugging log

  fetch('https://3fa-54-138-20.ngrok-free.app/create_payment_checkout_session', //CHANGE THIS WITH YOUR OWN NGROK LINK
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  }).then(function(response) {
    if (!response.ok) {
      return response.json().then(function(error) {
        throw new Error(error.detail);
      });
    }
    return response.json();
  }).then(function(session) {
    return stripe.redirectToCheckout({ sessionId: session.sessionId });
  }).then(function(result) {
    if (result.error) {
      alert(result.error.message);
    }
  }).catch(function(error) {
    console.error('Error:', error);
    alert(error.message);
  });
});
