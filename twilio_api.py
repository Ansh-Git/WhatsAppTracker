import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from urllib.parse import quote

logger = logging.getLogger(__name__)

# Get Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '+14155238886')  # Default Twilio WhatsApp Sandbox number

def send_whatsapp_message(to_phone_number, message_text):
    """
    Send a WhatsApp message using Twilio's WhatsApp API
    
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
        # Check if we have Twilio credentials
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            # If no credentials, fall back to generating a WhatsApp URL
            logger.warning("Twilio credentials not found. Generating WhatsApp URL instead.")
            return generate_whatsapp_url(to_phone_number, message_text)
        
        # Log the message
        logger.info(f"SENDING WHATSAPP MESSAGE via Twilio:")
        logger.info(f"From: {TWILIO_PHONE_NUMBER}")
        logger.info(f"To: {to_phone_number}")
        logger.info(f"Message: {message_text}")
        
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Prepend 'whatsapp:' to both phone numbers
        from_whatsapp = f"whatsapp:{TWILIO_PHONE_NUMBER}"
        to_whatsapp = f"whatsapp:{to_phone_number}"
        
        # Send the message
        message = client.messages.create(
            from_=from_whatsapp,
            body=message_text,
            to=to_whatsapp
        )
        
        logger.info(f"WhatsApp message sent with SID: {message.sid}")
        
        # Return message details
        return {
            "success": True,
            "message_sid": message.sid,
            "to": to_phone_number,
            "status": message.status
        }
    
    except TwilioRestException as e:
        logger.error(f"Twilio API error: {str(e)}")
        return {
            "success": False,
            "error": f"Twilio API error: {str(e)}",
            "error_code": e.code
        }
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def generate_whatsapp_url(to_phone_number, message_text):
    """
    Generate a URL that can be used to send a WhatsApp message
    
    Args:
        to_phone_number (str): The recipient's phone number in international format with + (e.g., "+1234567890")
        message_text (str): The message text to send
        
    Returns:
        dict: Information including the WhatsApp URL
    """
    try:
        # Format the WhatsApp URL
        whatsapp_url = f"https://wa.me/{to_phone_number.lstrip('+')}"
        
        # Encode the message
        encoded_message = quote(message_text)
        demo_link = f"{whatsapp_url}?text={encoded_message}"
        
        logger.info(f"Generated WhatsApp URL: {demo_link}")
        
        return {
            "success": True,
            "to": to_phone_number,
            "message": message_text,
            "whatsapp_url": demo_link,
            "note": "This is a fallback URL. Configure Twilio credentials for proper API integration."
        }
    except Exception as e:
        logger.error(f"Error generating WhatsApp URL: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def verify_twilio_webhook_signature(request):
    """
    Verify that the incoming webhook request is from Twilio
    
    Args:
        request: The Flask request object
        
    Returns:
        bool: True if the request signature is valid, False otherwise
    """
    # This function would normally verify the X-Twilio-Signature header
    # For simplicity, we're skipping this in the demo
    # In a production environment, you should use:
    # from twilio.request_validator import RequestValidator
    # validator = RequestValidator(TWILIO_AUTH_TOKEN)
    # url = request.url
    # signature = request.headers.get('X-Twilio-Signature', '')
    # return validator.validate(url, request.form, signature)
    
    return True  # Always return True for demo purposes