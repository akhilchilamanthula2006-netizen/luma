from flask import Flask, render_template, session
from config import config_by_name
import os

def create_app(config_name=None):
    """Application factory for Luma."""
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.chat import chat_bp
    from routes.journal import journal_bp
    from routes.analytics import analytics_bp
    from routes.wellness import wellness_bp
    from routes.profile import profile_bp
    from routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(wellness_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)

    # Home route / landing page
    @app.route('/')
    def home():
        return render_template('landing.html')

    # Global context processor to make session available easily in templates
    @app.context_processor
    def inject_user():
        return dict(
            is_authenticated=('user_id' in session),
            username=session.get('username', '')
        )

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
