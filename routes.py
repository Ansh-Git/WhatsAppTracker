import logging
import json
import os
from datetime import datetime, timedelta
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from sqlalchemy import func
from app import app, db
from models import User, Contact, Message, Automation, MessageStats
from whatsapp_api import send_message, verify_whatsapp_webhook

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Get message statistics for the last 7 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    # This would be filtered by user_id in a real multi-user application
    daily_stats = db.session.query(
        func.date(Message.timestamp).label('date'),
        func.count(Message.id).filter(Message.direction == 'incoming').label('received'),
        func.count(Message.id).filter(Message.direction == 'outgoing').label('sent')
    ).filter(
        func.date(Message.timestamp) >= start_date,
        func.date(Message.timestamp) <= end_date
    ).group_by(
        func.date(Message.timestamp)
    ).all()
    
    # Convert query result to dict for easier handling in template
    stats_by_date = {}
    for date, received, sent in daily_stats:
        stats_by_date[date.strftime('%Y-%m-%d')] = {'received': received, 'sent': sent}
    
    # Ensure all dates in range are represented
    date_labels = []
    received_data = []
    sent_data = []
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        date_labels.append(date_str)
        
        stats = stats_by_date.get(date_str, {'received': 0, 'sent': 0})
        received_data.append(stats['received'])
        sent_data.append(stats['sent'])
        
        current_date += timedelta(days=1)
    
    # Get contact statistics
    total_contacts = Contact.query.count()
    active_contacts = Contact.query.filter(
        Contact.last_interaction >= datetime.now() - timedelta(days=7)
    ).count()
    
    # Get message statistics
    total_messages = Message.query.count()
    incoming_messages = Message.query.filter_by(direction='incoming').count()
    outgoing_messages = Message.query.filter_by(direction='outgoing').count()
    
    return render_template(
        'dashboard.html',
        date_labels=json.dumps(date_labels),
        received_data=json.dumps(received_data),
        sent_data=json.dumps(sent_data),
        total_contacts=total_contacts,
        active_contacts=active_contacts,
        total_messages=total_messages,
        incoming_messages=incoming_messages,
        outgoing_messages=outgoing_messages
    )

@app.route('/messages')
def messages():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    messages = Message.query.order_by(Message.timestamp.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('messages.html', messages=messages)

@app.route('/automations')
def automations():
    automations = Automation.query.all()
    return render_template('automations.html', automations=automations)

@app.route('/settings')
def settings():
    # In a real app, this would get the current user's settings
    return render_template('settings.html')

# API Endpoints

@app.route('/api/messages', methods=['GET'])
def api_messages():
    limit = request.args.get('limit', 5, type=int)
    messages = Message.query.order_by(Message.timestamp.desc()).limit(limit).all()
    
    result = []
    for message in messages:
        result.append({
            'id': message.id,
            'phone_number': message.contact.phone_number,
            'contact_name': message.contact.name,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'direction': message.direction,
            'message_type': message.message_type,
            'status': message.status
        })
    
    return jsonify(result)

@app.route('/api/send_message', methods=['POST'])
def api_send_message():
    data = request.json
    if not data or 'phone' not in data or 'message' not in data:
        return jsonify({'error': 'Missing phone or message parameter'}), 400
    
    try:
        result = send_message(data['phone'], data['message'])
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/automations', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_automations():
    if request.method == 'GET':
        automations = Automation.query.all()
        return jsonify([{
            'id': a.id,
            'name': a.name,
            'trigger_type': a.trigger_type,
            'trigger_value': a.trigger_value,
            'response_text': a.response_text,
            'is_active': a.is_active
        } for a in automations])
    
    elif request.method == 'POST':
        data = request.json
        try:
            automation = Automation(
                name=data['name'],
                trigger_type=data['trigger_type'],
                trigger_value=data['trigger_value'],
                response_text=data['response_text'],
                is_active=data.get('is_active', True)
            )
            db.session.add(automation)
            db.session.commit()
            return jsonify({'success': True, 'id': automation.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        data = request.json
        try:
            automation = Automation.query.get(data['id'])
            if not automation:
                return jsonify({'error': 'Automation not found'}), 404
            
            automation.name = data.get('name', automation.name)
            automation.trigger_type = data.get('trigger_type', automation.trigger_type)
            automation.trigger_value = data.get('trigger_value', automation.trigger_value)
            automation.response_text = data.get('response_text', automation.response_text)
            automation.is_active = data.get('is_active', automation.is_active)
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        automation_id = request.args.get('id')
        try:
            automation = Automation.query.get(automation_id)
            if not automation:
                return jsonify({'error': 'Automation not found'}), 404
            
            db.session.delete(automation)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# Settings API Endpoints
@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    if request.method == 'GET':
        # In a real app, this would get settings from a database
        # Here we're just returning the environment variables
        return jsonify({
            'phone_number_id': os.environ.get('WHATSAPP_PHONE_NUMBER_ID', ''),
            'verify_token': os.environ.get('WHATSAPP_WEBHOOK_VERIFY_TOKEN', '')
        })
    
    elif request.method == 'POST':
        data = request.json
        # In a real app, this would save to a database
        # Here we're just returning success
        # Note: In a production app, you would not update env vars like this
        return jsonify({'success': True})

@app.route('/api/export/messages', methods=['GET'])
def api_export_messages():
    # In a real app, this would export messages to a CSV file
    # Here we're just returning a dummy response
    return jsonify({'success': False, 'error': 'Export feature not implemented yet'}), 501

@app.route('/api/cleanup', methods=['POST'])
def api_cleanup():
    days = request.args.get('days', 30, type=int)
    # In a real app, this would delete old messages
    # Here we're just returning a dummy response
    return jsonify({'success': False, 'error': 'Cleanup feature not implemented yet'}), 501

# WhatsApp Webhook Endpoint
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Webhook verification
        return verify_whatsapp_webhook(request)
    
    elif request.method == 'POST':
        # Process incoming webhook data
        try:
            data = request.json
            logger.debug(f"Received webhook data: {data}")
            
            # Process the incoming message
            process_incoming_message(data)
            
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return jsonify({'error': str(e)}), 500

def process_incoming_message(data):
    """Process incoming WhatsApp message from webhook data"""
    try:
        # Extract message data from webhook payload
        # This structure will vary based on the WhatsApp Business API format
        if 'entry' not in data:
            logger.warning("No 'entry' in webhook data")
            return
        
        for entry in data['entry']:
            if 'changes' not in entry:
                continue
            
            for change in entry['changes']:
                if change.get('field') != 'messages':
                    continue
                
                value = change.get('value', {})
                if 'messages' not in value:
                    continue
                
                for msg in value['messages']:
                    # Extract message details
                    message_id = msg.get('id')
                    from_number = msg.get('from')
                    timestamp = datetime.fromtimestamp(int(msg.get('timestamp', 0)))
                    message_type = msg.get('type', 'text')
                    
                    # Get message content based on type
                    content = ""
                    if message_type == 'text':
                        content = msg.get('text', {}).get('body', '')
                    elif message_type == 'image':
                        content = "[Image]"  # In a real app, you'd process the image URL
                    # Add more message types as needed
                    
                    # Find or create contact
                    contact = Contact.query.filter_by(phone_number=from_number).first()
                    if not contact:
                        contact = Contact(
                            phone_number=from_number,
                            first_interaction=timestamp,
                            last_interaction=timestamp
                        )
                        db.session.add(contact)
                    else:
                        contact.last_interaction = timestamp
                    
                    # Create message record
                    message = Message(
                        message_id=message_id,
                        contact=contact,
                        content=content,
                        timestamp=timestamp,
                        direction='incoming',
                        message_type=message_type,
                        status='received',
                        message_metadata=msg
                    )
                    db.session.add(message)
                    db.session.commit()
                    
                    # Check for tracking commands
                    if content.strip().upper().startswith('TRACK '):
                        process_tracking_command(contact, content)
                    else:
                        # Process automations for non-tracking messages
                        check_automations(contact, content)
                    
                    # Update statistics
                    update_stats(contact, 'incoming')
                    
                    logger.info(f"Processed incoming message {message_id} from {from_number}")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing message: {str(e)}")
        raise

def check_automations(contact, message_content):
    """Check if any automations should be triggered by this message"""
    # Get all active keyword automations
    keyword_automations = Automation.query.filter_by(
        trigger_type='keyword',
        is_active=True
    ).all()
    
    for automation in keyword_automations:
        keywords = [k.strip().lower() for k in automation.trigger_value.split(',')]
        if any(keyword in message_content.lower() for keyword in keywords):
            # Trigger automation
            try:
                send_message(contact.phone_number, automation.response_text)
                
                # Update automation last triggered time
                automation.last_triggered = datetime.utcnow()
                db.session.commit()
                
                # Log outgoing message
                message = Message(
                    contact=contact,
                    content=automation.response_text,
                    direction='outgoing',
                    message_type='text',
                    status='sent'
                )
                db.session.add(message)
                db.session.commit()
                
                # Update statistics
                update_stats(contact, 'outgoing')
                
                logger.info(f"Triggered automation '{automation.name}' for contact {contact.phone_number}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error triggering automation: {str(e)}")

def process_tracking_command(contact, message_content):
    """Process a tracking command from a WhatsApp message"""
    try:
        # Extract the tracking number from the message
        tracking_parts = message_content.strip().split(' ', 1)
        if len(tracking_parts) < 2 or not tracking_parts[1].strip():
            # No tracking number provided
            response = "⚠️ Please provide a tracking number. Example: TRACK 1234567890"
        else:
            tracking_number = tracking_parts[1].strip()
            
            # Import the tracking function
            from acpl_tracker import track_acpl_cargo, format_tracking_result
            
            # Get tracking information
            logger.info(f"Tracking ACPL cargo number: {tracking_number}")
            tracking_result = track_acpl_cargo(tracking_number)
            
            # Format the response
            response = format_tracking_result(tracking_result)
        
        # Send the response
        send_message(contact.phone_number, response)
        
        # Log the outgoing message
        message = Message(
            contact=contact,
            content=response,
            direction='outgoing',
            message_type='text',
            status='sent'
        )
        db.session.add(message)
        db.session.commit()
        
        # Update statistics
        update_stats(contact, 'outgoing')
        
        logger.info(f"Sent tracking response to {contact.phone_number}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing tracking command: {str(e)}")
        
        # Send error message
        try:
            error_message = f"❌ Error processing tracking request: {str(e)}"
            send_message(contact.phone_number, error_message)
        except:
            logger.error("Failed to send error message to user")

def update_stats(contact, direction):
    """Update message statistics"""
    today = datetime.utcnow().date()
    
    # Find or create stats for today
    stats = MessageStats.query.filter_by(date=today).first()
    if not stats:
        stats = MessageStats(date=today, messages_received=0, messages_sent=0, unique_contacts=0)
        db.session.add(stats)
    
    # Update message counts
    if direction == 'incoming':
        stats.messages_received += 1
    else:
        stats.messages_sent += 1
    
    # Update unique contacts count
    # In a real implementation, this would be more complex to accurately track daily unique contacts
    
    db.session.commit()
