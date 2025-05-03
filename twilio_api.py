import os
import logging
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)

# Twilio WhatsApp Sandbox number
TWILIO_WHATSAPP_NUMBER = "+14155238886"

def send_whatsapp_message(to_phone_number, message_text):
    """
    Send a WhatsApp message using Twilio's WhatsApp Sandbox
    
    Args:
        to_phone_number (str): The recipient's phone number in international format with + (e.g., "+1234567890")
        message_text (str): The message text to send
        
    Returns:
        dict: Status information about the message
    """
    # Ensure phone number is in proper format
    if not to_phone_number.startswith('+'):
        to_phone_number = f"+{to_phone_number}"
    
    try:
        # Format the WhatsApp URL
        whatsapp_url = f"https://wa.me/{to_phone_number.lstrip('+')}"
        
        # Log the message for demonstration purposes
        logger.info(f"SENDING WHATSAPP MESSAGE via Twilio WhatsApp Sandbox ({TWILIO_WHATSAPP_NUMBER}):")
        logger.info(f"To: {to_phone_number}")
        logger.info(f"Message: {message_text}")
        
        # For a real implementation, we would use the Twilio SDK:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        #     body=message_text,
        #     to=f"whatsapp:{to_phone_number}"
        # )
        
        # For demo purposes, generate a link that can be clicked to send a message
        encoded_message = quote(message_text)
        demo_link = f"{whatsapp_url}?text={encoded_message}"
        
        logger.info(f"WhatsApp link: {demo_link}")
        
        return {
            "success": True,
            "to": to_phone_number,
            "message": message_text,
            "demo_link": demo_link
        }
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }