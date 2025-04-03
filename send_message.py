import os

from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")


def send_twilio_message(to_phone_number: str, message: str) -> None:
    """
    Send an SMS message using Twilio.
    
    Args:
        to_phone_number (str): The recipient's phone number
        message (str): The message to send
        
    Raises:
        ValueError: If Twilio credentials are not set
        Exception: If there's an error sending the message
    """
    # Check if Twilio credentials are set
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        raise ValueError(
            "Twilio credentials not set. Please provide TWILIO_ACCOUNT_SID, "
            "TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables."
        )
    
    # Initialize Twilio client
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # Sending the SMS message
    message = client.messages.create(
        body=message, from_=TWILIO_PHONE_NUMBER, to=to_phone_number
    )

    print(f"Message sent with SID: {message.sid}")
    return message.sid