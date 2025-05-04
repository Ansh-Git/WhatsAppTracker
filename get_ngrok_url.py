import os
import sys
import logging
from ngrok_setup import setup_ngrok

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ngrok_url():
    """Get the ngrok URL without starting the Flask app"""
    # Set up ngrok on port 5000 (or from environment)
    port = int(os.environ.get("PORT", 5000))
    
    # Start ngrok tunnel
    public_url = setup_ngrok(port)
    
    # Print the URLs for easy access
    print("\n" + "=" * 60)
    print(f"NGROK PUBLIC URL: {public_url}")
    print(f"WEBHOOK URL: {public_url}/webhook")
    print(f"WEBHOOK SIMULATOR: {public_url}/webhook-simulator")
    print("=" * 60)
    print("\nTo configure WhatsApp with Twilio:")
    print("1. Go to the Twilio Console -> Messaging -> Try it out -> Send a WhatsApp message")
    print("2. Set the Webhook URL to: " + f"{public_url}/webhook")
    print("3. Test with the webhook simulator: " + f"{public_url}/webhook-simulator")
    
    return public_url

if __name__ == "__main__":
    # If no arguments provided, just get and print the URL
    get_ngrok_url()