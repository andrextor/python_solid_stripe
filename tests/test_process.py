import unittest, json
from unittest.mock import patch
from src.process import PaymentProcessor

class ProcessTest(unittest.TestCase):

    def setUp(self) -> None:
        self.customer =  {"name": "Andres test", "contact_info": {"email": "andres2@yopmail.com"}}
        self.payment_data = {"amount": 120, "source": "tok_mastercard", "cvv": 123}

    @patch('src.process.stripe.Charge.create')
    def test_true_example(self, mock_stripe_create):
        mock_stripe_create.return_value.status_code = 200
        
        mock_response = ''
        with open('tests/support/stripe/succeeded.json', 'r') as f:
            mock_response = json.load(f)

        mock_stripe_create.return_value = mock_response

        process = PaymentProcessor()
        charge = process.process_transaction(customer_data=self.customer, payment_data=self.payment_data)
        print(charge)
        assert True