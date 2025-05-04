import os
import logging
from pyngrok import ngrok, conf

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_ngrok(port, authtoken=None):
    """
    Set up an ngrok tunnel to the specified port
    
    Args:
        port (int): The local port to expose
        authtoken (str, optional): Your ngrok authtoken. If not provided, tries to use env var.
    
    Returns:
        str: The public ngrok URL
    """
    # Check for authtoken in environment or provided argument
    token = authtoken or os.environ.get("NGROK_AUTH_TOKEN")
    
    if token:
        # Set the auth token in the ngrok config
        logger.info("Setting ngrok auth token...")
        conf.get_default().auth_token = token
    else:
        logger.warning("No ngrok auth token found. Ngrok tunnel may expire after 2 hours.")
        logger.warning("Get a free auth token at https://ngrok.com and set it as NGROK_AUTH_TOKEN env variable")
    
    # Start ngrok tunnel
    logger.info(f"Starting ngrok tunnel to port {port}...")
    public_url = ngrok.connect(port).public_url
    
    # Determine if it's HTTP or HTTPS
    if public_url.startswith("https://"):
        protocol = "https"
    else:
        protocol = "http"
    public_url = public_url.replace("http://", "").replace("https://", "")
    logger.info(f"ngrok tunnel established: {protocol}://{public_url}")
    logger.info(f"Webhook URL: {protocol}://{public_url}/webhook")
    
    return f"{protocol}://{public_url}"

if __name__ == "__main__":
    # If run directly, set up ngrok on port 5000 (Flask default)
    port = int(os.environ.get("PORT", 5000))
    public_url = setup_ngrok(port)
    
    print("\n" + "=" * 50)
    print(f"Public URL: {public_url}")
    print(f"Webhook URL: {public_url}/webhook")
    print(f"Webhook Simulator: {public_url}/webhook-simulator")
    print("=" * 50)
    print("\nUse this Webhook URL in your Twilio WhatsApp settings.")
    print("Note: Without an authtoken, this URL will expire after 2 hours.")
    print("Set the NGROK_AUTH_TOKEN environment variable for a permanent URL.")