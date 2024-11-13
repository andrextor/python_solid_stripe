import unittest, json, os
from unittest.mock import patch
from src.process import PaymentServices

class ProcessTest(unittest.TestCase):

    def setUp(self) -> None:
        self.customer =  {"name": "Andres test", "contact_info": {"email": "andres3@yopmail.com"}}
        self.payment_data = {"amount": 110, "source": "tok_mastercard", "cvv": 123}
        self.logger_file_name = 'test_transactions.log'
        
    def tearDown(self) -> None:        
        if self.logger_file_name and os.path.exists(self.logger_file_name):
            os.remove(self.logger_file_name)

    @patch('src.process.stripe.Charge.create')
    def test_process_transaction_payment_succeeded(self, mock_stripe_create):
        mock_stripe_create.return_value.status_code = 200
        mock_response = ''
        with open('tests/support/stripe/succeeded.json', 'r') as f:
            mock_response = json.load(f)

        mock_stripe_create.return_value = mock_response

        process = PaymentServices()
        charge = process.process_transaction(self.customer, self.payment_data, self.logger_file_name)
        assert charge['status'] == 'succeeded'
        assert charge['description'] == 'Charge for Andres test'
        assert charge['amount'] == 110