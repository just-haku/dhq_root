# app/__init__.py
from flask import Flask, redirect, url_for
from flask_apscheduler import APScheduler
import json
import threading
import time
# Import your blueprints
from app.cogs.auth import auth_bp
from app.cogs.user import user_bp
from app.cogs.operator import operator_bp
from app.models import get_global_api_settings
from app.cogs.landing import landing_bp
# Import your interval-based order-checking function
from app.orders import check_and_send_orders
# Import the mail fetcher function
from app.mail_fetcher import fetch_collab_emails_for_all_users


class Config:
    SCHEDULER_API_ENABLED = True

def create_app():
    app = Flask(__name__)
    app.secret_key = "your_secret_key_here"  # Change to a secure key in production
    app.config.from_object(Config)

    # Register Blueprints
    app.register_blueprint(auth_bp)                 # /login, /logout, etc.
    app.register_blueprint(user_bp, url_prefix="/user") 
    app.register_blueprint(operator_bp, url_prefix="/operator")

    app.register_blueprint(landing_bp)

    # Initialize and start APScheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    # Schedule the order-checking function to run every 5 minutes
    scheduler.add_job(
        id='order_scheduler',
        func=check_and_send_orders,
        trigger='interval',
        minutes=5,
        max_instances=1
    )

    # Schedule the mail fetching function to run every 5 minutes
    scheduler.add_job(
        id='mail_scheduler',
        func=fetch_collab_emails_for_all_users,
        trigger='interval',
        minutes=5,
        max_instances=1
    )


    @app.template_filter("tojson_str")
    def tojson_str_filter(obj):
        return json.dumps(obj, default=str)

    @app.template_filter("censor_api_key")
    def censor_api_key(api_key):
        """Return a censored version of the API key (first 4 and last 4 characters visible)."""
        if not api_key or len(api_key) < 8:
            return api_key
        return api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]

    @app.context_processor
    def inject_global_api_settings():
        global_api_settings = get_global_api_settings()
        return dict(global_api_settings=global_api_settings)

    @app.route("/")
    def root():
        return redirect(url_for("auth.login"))

    return app
