# ACPL Cargo WhatsApp Tracking Bot

A WhatsApp bot that allows users to track ACPL cargo shipments by sending tracking commands via WhatsApp.

## Features

- Track ACPL cargo shipments by sending "TRACK [tracking number]" via WhatsApp
- Automated response system for keywords
- WhatsApp integration using Twilio's API
- Tracking history and message statistics
- Test interface for tracking without WhatsApp

## Setup Instructions

### 1. Environment Variables

The following environment variables need to be set:

- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
- `TWILIO_PHONE_NUMBER`: Your Twilio WhatsApp number (with the format `+1234567890`)

### 2. Twilio WhatsApp Sandbox Setup

1. Create a Twilio account at [twilio.com](https://www.twilio.com/)
2. Go to the WhatsApp Sandbox in the Twilio Console
3. Set up the WhatsApp Sandbox and connect your WhatsApp to it by following Twilio's instructions
4. Set the webhook URL for incoming messages to `https://your-server.com/webhook`
5. Make sure the webhook is configured to receive POST requests

### 3. Usage

Once the bot is set up, users can interact with it through WhatsApp by:

1. Sending `HELP` to get information about available commands
2. Sending `TRACK [tracking number]` to track an ACPL cargo shipment

Example:
```
TRACK 2504500644
```

## Testing Locally

You can test the tracking functionality without WhatsApp by using the test interface:

1. Visit `/test` in your browser
2. Enter a tracking number
3. Click "Track Shipment" to see the tracking results

## Technical Implementation

- Flask web framework
- SQLAlchemy ORM for database operations
- BeautifulSoup for web scraping the ACPL website
- Twilio API for WhatsApp messaging
- Python requests for HTTP requests

## Database Schema

- **User**: User authentication and profile information
- **Contact**: WhatsApp contact information
- **Message**: Record of incoming and outgoing messages
- **Automation**: Keyword-based automated responses
- **MessageStats**: Message statistics for the dashboard

## Deployment on Render

This application can be easily deployed on Render's free tier:

### Using the Deploy to Render Button

The easiest way to deploy this application is to click the "Deploy to Render" button below:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/whatsapp-tracking-bot)

1. Fork this repository to your GitHub account
2. Update the Deploy to Render button URL in your README.md with your GitHub username
3. Click the button and follow the instructions on Render to set up your application

### Manual Deployment Steps

1. Create a new account on [Render](https://render.com/) if you don't have one
2. Fork this repository to your GitHub account
3. Create a new Web Service in Render and connect it to your GitHub repository
4. Use the following settings:
   - Environment: Python
   - Build Command: `pip install -r render-requirements.txt`
   - Start Command: `gunicorn main:app`
5. Set the following environment variables in Render:
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
   - `TWILIO_PHONE_NUMBER`: Your Twilio WhatsApp number
   - `SESSION_SECRET`: A random string for session security
6. Create a PostgreSQL database in Render:
   - Go to Dashboard > New > PostgreSQL
   - Connect it to your web service
7. Once deployed, set up your Twilio webhook URL to point to:
   `https://your-render-app.onrender.com/webhook`

### Important Notes for Render Deployment

1. Render's free tier PostgreSQL databases are automatically deleted after 90 days
2. The free tier web service will spin down after periods of inactivity, which may cause a slight delay on the first request
3. Your application will be publicly accessible at `https://your-app-name.onrender.com`

## License

This project is provided as is, without warranty of any kind.