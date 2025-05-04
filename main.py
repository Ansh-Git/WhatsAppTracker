import os
from app import app  # noqa: F401
import datetime
import pytz
from flask import Response

# Add a middleware to check if the current time is within service hours
@app.before_request
def check_service_hours():
    # Get current time in IST
    ist_timezone = pytz.timezone('Asia/Kolkata')
    current_time = datetime.datetime.now(ist_timezone).time()
    
    # Check if current time is outside service hours (7 AM to 9 PM IST)
    if not (datetime.time(7, 0) <= current_time <= datetime.time(21, 0)):
        return Response(
            "Service is currently offline. Operating hours are 7 AM to 9 PM IST. "
            "Please try again during these hours.",
            status=503
        )
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
