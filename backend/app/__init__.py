from .database import init_db


def init_app():
    """Initialize database tables when the app container starts."""
    init_db()