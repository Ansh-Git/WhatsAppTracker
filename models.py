from datetime import datetime
from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    whatsapp_number = db.Column(db.String(20))
    whatsapp_verified = db.Column(db.Boolean, default=False)
    api_key = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='user', lazy='dynamic')
    automations = db.relationship('Automation', backref='user', lazy='dynamic')


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(120))
    profile_name = db.Column(db.String(120))
    first_interaction = db.Column(db.DateTime, default=datetime.utcnow)
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='contact', lazy='dynamic')


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(64), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    direction = db.Column(db.String(10))  # 'incoming' or 'outgoing'
    message_type = db.Column(db.String(20))  # 'text', 'image', 'video', etc.
    status = db.Column(db.String(20))  # 'sent', 'delivered', 'read', 'failed'
    message_metadata = db.Column(db.JSON)  # Changed from 'metadata' since it's a reserved keyword


class Automation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(120), nullable=False)
    trigger_type = db.Column(db.String(20))  # 'keyword', 'time', 'new_contact'
    trigger_value = db.Column(db.String(255))  # keyword or time value
    response_text = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_triggered = db.Column(db.DateTime)


class MessageStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, nullable=False)
    messages_received = db.Column(db.Integer, default=0)
    messages_sent = db.Column(db.Integer, default=0)
    unique_contacts = db.Column(db.Integer, default=0)
    response_time_avg = db.Column(db.Integer)  # in seconds
