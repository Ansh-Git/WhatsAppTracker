import os
import sys
import logging
import time
from pyngrok import ngrok, conf
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ngrok_url():
    """Get the ngrok URL without starting the Flask app"""
    # Set up ngrok on port 5000 (or from environment)
    port = int(os.environ.get("PORT", 5000))
    
    # Set ngrok auth token if available
    auth_token = os.environ.get("NGROK_AUTH_TOKEN")
    if auth_token:
        logger.info("Setting ngrok auth token...")
        conf.get_default().auth_token = auth_token
    
    # Disconnect any existing tunnels
    try:
        tunnels = ngrok.get_tunnels()
        for tunnel in tunnels:
            logger.info(f"Closing existing tunnel: {tunnel.public_url}")
            ngrok.disconnect(tunnel.public_url)
    except Exception as e:
        logger.warning(f"Error closing existing tunnels: {e}")
    
    # Start ngrok tunnel with http protocol
    logger.info(f"Starting ngrok tunnel to port {port}...")
    http_tunnel = ngrok.connect(port, "http")
    public_url = http_tunnel.public_url
    
    # Print the URLs for easy access
    print("\n" + "=" * 60)
    print(f"NGROK PUBLIC URL: {public_url}")
    print(f"WEBHOOK URL: {public_url}/webhook")
    print(f"WEBHOOK SIMULATOR: {public_url}/webhook-simulator")
    print("=" * 60)
    
    # Test if the tunnel is working
    try:
        logger.info("Testing if the tunnel is working...")
        response = requests.get(f"{public_url}/")
        if response.status_code == 200:
            logger.info(f"Tunnel is working! Status code: {response.status_code}")
        else:
            logger.warning(f"Tunnel returned status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error testing tunnel: {e}")
    
    print("\nTo configure WhatsApp with Twilio:")
    print("1. Go to the Twilio Console -> Messaging -> Try it out -> Send a WhatsApp message")
    print("2. Set the Webhook URL to: " + f"{public_url}/webhook")
    print("3. Test with the webhook simulator: " + f"{public_url}/webhook-simulator")
    
    return public_url

if __name__ == "__main__":
    # If no arguments provided, just get and print the URL
    get_ngrok_url()
    
    # Keep the script running to maintain the tunnel
    print("\nPress Ctrl+C to close the ngrok tunnel and exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing ngrok tunnel...")
        ngrok.kill()