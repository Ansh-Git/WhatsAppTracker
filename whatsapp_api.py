import os
import requests
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

# WhatsApp Business API configurations
WHATSAPP_API_VERSION = "v16.0"  # Update as needed
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")
WHATSAPP_BASE_URL = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}"
WHATSAPP_WEBHOOK_VERIFY_TOKEN = os.environ.get("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "your_verify_token")

def send_message(to_phone_number, message_text):
    """
    Send a WhatsApp message using the WhatsApp Business API
    
    Args:
        to_phone_number (str): The recipient's phone number in international format without + (e.g., "1234567890")
        message_text (str): The message text to send
        
    Returns:
        dict: The API response
    """
    # Ensure phone number is in proper format
    if to_phone_number.startswith('+'):
        to_phone_number = to_phone_number[1:]
    
    # Endpoint for sending messages
    url = f"{WHATSAPP_BASE_URL}/messages"
    
    # Message payload
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone_number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message_text
        }
    }
    
    # Headers with authentication
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        raise

def verify_whatsapp_webhook(request):
    """
    Verify WhatsApp webhook endpoint as per their requirements
    
    Args:
        request: The Flask request object
        
    Returns:
        str: The challenge string if verification is successful
    """
    # WhatsApp sends these query parameters for verification
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    # Verify mode and token
    if mode == 'subscribe' and token == WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return challenge
    else:
        logger.warning(f"Webhook verification failed: mode={mode}, token={token}")
        return "Verification failed", 403

def get_media_url(media_id):
    """
    Get the URL for a media file (image, audio, etc.) sent via WhatsApp
    
    Args:
        media_id (str): The media ID from the WhatsApp API
        
    Returns:
        str: The URL to download the media file
    """
    url = f"{WHATSAPP_BASE_URL}/media/{media_id}"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('url')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting media URL: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        raise
