import os, stripe
from dotenv import load_dotenv
from stripe import ErrorObject
from dataclasses import dataclass
from stripe import Charge

_ = load_dotenv()

@dataclass
class StripePaymentProcesor:
    def process_transaction(self, customer_data, payment_data) -> Charge:
        stripe.api_key = os.getenv("STRIPE_API_KEY")

        try:
            charge = stripe.Charge.create(
                amount=payment_data["amount"],
                currency="usd",
                source=payment_data["source"],
                description="Charge for " + customer_data["name"],
            )
            print("Payment successful")
        except ErrorObject as e:
            print("Payment failed:", e)
            raise e
        
        return charge

@dataclass
class CustomerValidator:
    def validate(self, customer_data):
        if not customer_data.get("name"):
            raise ValueError('Invalid customer data: missing name')

        if not customer_data.get("contact_info"):
            raise ValueError('Invalid customer data: missing contact info')
        
@dataclass
class PaymentValidator:
    def validate(self, payment_data):
        if not payment_data.get("source"):
            raise ValueError('Invalid payment data')
        
@dataclass
class Notifier:
    def send(self, customer):
        if "email" in customer:
            # import smtplib
            from email.mime.text import MIMEText

            msg = MIMEText("Thank you for your payment.")
            msg["Subject"] = "Payment Confirmation"
            msg["From"] = "no-reply@example.com"
            msg["To"] = customer["email"]

            # server = smtplib.SMTP("localhost")
            # server.send_message(msg)
            # server.quit()
            print("Email sent to", customer["email"])

        elif "phone" in customer:
            phone_number = customer["phone"]
            sms_gateway = "the custom SMS Gateway"
            print(
                f"send the sms using {sms_gateway}: SMS sent to {phone_number}: Thank you for your payment."
            )

        else:
            print("No valid contact information for notification")
        
@dataclass
class Logger:
    def info(self, customer_data, payment_data, charge: Charge, file_name: str = 'transactions.log'):
          with open(file_name, "a") as log_file:
            log_file.write(
                f"info:{customer_data['name']} paid {payment_data['amount']}\n"
            )
            log_file.write(f"Payment status: {charge['status']}\n")
        

@dataclass
class PaymentServices:
    customer_validator = CustomerValidator()
    payment_validator = PaymentValidator()
    stripe_payment_process = StripePaymentProcesor()
    notifier = Notifier()
    logger = Logger()
    
    def process_transaction(self, customer_data, payment_data, logger_file_name: str = 'transactions.logs') -> Charge:
        self.customer_validator.validate(customer_data)
        self.payment_validator.validate(payment_data)
        charge = self.stripe_payment_process.process_transaction(customer_data, payment_data)
        self.notifier.send(customer_data['contact_info'])
        self.logger.info(customer_data, payment_data, charge, logger_file_name)
        return charge


if __name__ == "__main__":
    payment_processor = PaymentServices()

    customer_data_with_email = {
        "name": "Andres test",
        "contact_info": {"email": "andres2@yopmail.com"},
    }
    customer_data_with_phone = {
        "name": "Platzi Python",
        "contact_info": {"phone": "1234567890"},
    }

    payment_data = {"amount": 130, "source": "tok_mastercard", "cvv": 123}

    payment_processor.process_transaction(customer_data_with_email, payment_data)
    """   payment_processor.process_transaction(
        customer_data_with_phone, payment_data
    ) """