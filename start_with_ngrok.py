import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set the environment variables for running with ngrok"""
    # Enable ngrok
    os.environ["USE_NGROK"] = "true"
    
    # Check for auth token in environment
    if not os.environ.get("NGROK_AUTH_TOKEN"):
        logger.warning("NGROK_AUTH_TOKEN environment variable not set.")
        logger.warning("The ngrok tunnel will expire after 2 hours.")
        logger.warning("Get a free auth token at https://ngrok.com")
        
        # Ask if the user wants to input an auth token
        token = input("Enter your ngrok auth token (or press Enter to skip): ").strip()
        if token:
            os.environ["NGROK_AUTH_TOKEN"] = token
            print(f"Auth token set: {token[:5]}...{token[-5:]}")

def main():
    # Set up environment variables
    setup_environment()
    
    # Start the application
    print("Starting application with ngrok tunnel...")
    
    # Use the workflow command if available, otherwise fall back to gunicorn
    try:
        subprocess.run(["gunicorn", "--bind", "0.0.0.0:5000", "--reload", "main:app"])
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()