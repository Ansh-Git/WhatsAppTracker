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

This application is configured for one-click deployment on Render's free tier:

### Option A: One-Click Deployment (Recommended)

The easiest way to deploy this application is to click the "Deploy to Render" button below:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Ansh-Git/WhatsAppTracker.git)

**Step-by-Step Instructions:**

1. Click the button above (after pushing your code to GitHub)
2. Connect your GitHub account if prompted
3. Select the repository containing this code
4. Render will automatically detect the `render.yaml` file and set up:
   - A web service for your application
   - A PostgreSQL database
   - All necessary environment variables (except Twilio credentials)
5. On the final setup page, you'll need to add your Twilio credentials:
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID 
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
   - `TWILIO_PHONE_NUMBER`: Your Twilio WhatsApp number with the '+' prefix
6. Click "Apply" to begin the deployment
7. Wait for deployment to complete (typically 5-10 minutes)
8. Once deployed, your app will be available at `https://whatsapp-tracking-bot.onrender.com`
9. Visit your deployed app and click "Render Deployment Setup" for instructions to configure your Twilio webhook

### Option B: Manual Deployment

If you prefer to deploy manually:

1. Create a Render account at [render.com](https://render.com/)
2. From your Render dashboard, click "New +" and select "Blueprint"
3. Connect your GitHub repository
4. Render will detect the `render.yaml` file and set up all services
5. Set the following environment variables:
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
   - `TWILIO_PHONE_NUMBER`: Your Twilio WhatsApp number
6. Once deployed, set up your Twilio webhook URL to point to:
   `https://whatsapp-tracking-bot.onrender.com/webhook`

### After Deployment: Configure Twilio

1. Log in to your [Twilio Console](https://www.twilio.com/console)
2. Go to Messaging → Settings → WhatsApp Sandbox
3. Set the webhook URL for "When a message comes in" to:
   `https://whatsapp-tracking-bot.onrender.com/webhook`
4. Set the HTTP Method to POST
5. Save your changes
6. Test by sending "TRACK 2504500644" to your Twilio WhatsApp number

### Important Notes for Render Deployment

1. Free tier apps go to sleep after periods of inactivity, causing a slight delay on the first request
2. The first connection might take up to 30 seconds as your app "wakes up"
3. To prevent this, upgrade to a paid tier or set up a ping service to keep your app active
4. The application includes a dashboard to monitor messages and configure automations at:
   `https://whatsapp-tracking-bot.onrender.com/dashboard`
5. Webhook testing is available at:
   `https://whatsapp-tracking-bot.onrender.com/webhook-simulator`

## License

This project is provided as is, without warranty of any kind.