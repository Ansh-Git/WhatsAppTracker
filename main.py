import os
from app import app  # noqa: F401
import routes  # noqa: F401

# Set up ngrok if the environment variable is set
USE_NGROK = os.environ.get('USE_NGROK', 'false').lower() in ('true', '1', 't')

if USE_NGROK:
    # Import and initialize ngrok settings
    from ngrok_setup import setup_ngrok
    
    # Get the port from environment or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Start ngrok tunnel when the app starts
    public_url = setup_ngrok(port)
    
    # Update any base URLs or webhook URLs to use the public ngrok URL

if __name__ == "__main__":
    # Get port from environment variable (Render sets this)
    # or use 5000 as default
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
