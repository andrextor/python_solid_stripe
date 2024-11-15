import os, stripe
from dotenv import load_dotenv
from stripe import ErrorObject
from pydantic.dataclasses import dataclass 
from stripe import Charge
from pydantic import BaseModel, validate_arguments
from typing import Optional

_ = load_dotenv()

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    
class UserData(BaseModel):
    name: str
    
class CustomerData(BaseModel):
    name: str
    contact_info: ContactInfo

class PaymentData(BaseModel):
    amount:int
    source:str

@dataclass
class StripePaymentProcesor:
    def process_transaction(self, customer_data: CustomerData, payment_data: PaymentData) -> Charge:
        stripe.api_key = os.getenv("STRIPE_API_KEY")

        try:
            charge = stripe.Charge.create(
                amount=payment_data.amount,
                currency="usd",
                source=payment_data.source,
                description="Charge for " + customer_data.name,
            )
            print("Payment successful")
        except ErrorObject as e:
            print("Payment failed:", e)
            raise e
        
        return charge


class CustomerValidator:
    def validate(self, customer_data: CustomerData):
        if not customer_data.name:
            raise ValueError('Invalid customer data: missing name')

        if not customer_data.contact_info:
            raise ValueError('Invalid customer data: missing contact info')
        
@dataclass
class PaymentValidator:
    def validate(self, payment_data: PaymentData):
        if not payment_data.source:
            raise ValueError('Invalid payment data')
        
@dataclass
class Notifier:
    def send(self, customer: ContactInfo):
        if customer.email:
            # import smtplib
            from email.mime.text import MIMEText

            msg = MIMEText("Thank you for your payment.")
            msg["Subject"] = "Payment Confirmation"
            msg["From"] = "no-reply@example.com"
            msg["To"] = customer.email

            # server = smtplib.SMTP("localhost")
            # server.send_message(msg)
            # server.quit()
            print("Email sent to", customer.email)

        elif "phone" in customer:
            phone_number = customer.phone
            sms_gateway = "the custom SMS Gateway"
            print(
                f"send the sms using {sms_gateway}: SMS sent to {phone_number}: Thank you for your payment."
            )

        else:
            print("No valid contact information for notification")
        
@dataclass
class Logger:
    def info(self, customer_data: CustomerData, payment_data: PaymentData, charge: Charge, file_name: str = 'transactions.log'):
          with open(file_name, "a") as log_file:
            log_file.write(
                f"info:{customer_data.name} paid {payment_data.amount}\n"
            )
            log_file.write(f"Payment status: {charge['status']}\n")
        

@dataclass
class PaymentServices:
    customer_validator = CustomerValidator()
    payment_validator = PaymentValidator()
    stripe_payment_process = StripePaymentProcesor()
    notifier = Notifier()
    logger = Logger()
    
    def process_transaction(self, customer_data: CustomerData, payment_data: PaymentData, logger_file_name: str = 'transactions.logs') -> Charge:
        self.customer_validator.validate(customer_data)
        self.payment_validator.validate(payment_data)
        charge = self.stripe_payment_process.process_transaction(customer_data, payment_data)
        self.notifier.send(customer_data.contact_info)
        self.logger.info(customer_data, payment_data, charge, logger_file_name)
        return charge

def main():
    payment_processor = PaymentServices()

    contac_info_data = ContactInfo(email='andres2@yopmail.com')
    customer_data = CustomerData(name='Andres', contact_info=contac_info_data)
    payment_data = PaymentData(amount=123, source="tok_mastercard")
    payment_processor.process_transaction(customer_data, payment_data)

if __name__ == "__main__":
    main()