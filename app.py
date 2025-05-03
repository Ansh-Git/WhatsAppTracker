import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models so their tables will be created
    import models  # noqa: F401
    from models import Automation

    db.create_all()
    logger.info("Database tables created")
    
    # Create default automations if they don't exist
    if Automation.query.filter_by(trigger_type='keyword', trigger_value='help').count() == 0:
        help_automation = Automation(
            name="Help Command",
            trigger_type="keyword",
            trigger_value="help",
            response_text=(
                "📱 *WhatsApp Tracking Bot Help*\n\n"
                "Here are commands you can use:\n\n"
                "*TRACK <number>* - Track an ACPL cargo shipment\n"
                "Example: TRACK 1234567890\n\n"
                "*HELP* - Show this help message\n\n"
                "Need more assistance? Contact support."
            ),
            is_active=True
        )
        db.session.add(help_automation)
        db.session.commit()
        logger.info("Created default HELP automation")
