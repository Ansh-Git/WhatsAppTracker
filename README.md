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

## License

This project is provided as is, without warranty of any kind.