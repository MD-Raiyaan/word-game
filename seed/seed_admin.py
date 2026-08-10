import os
import sys
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User

def seed_admin():
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin$123')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')

    app = create_app()
    with app.app_context():
        db.create_all()
        existing = User.query.filter_by(username=admin_username).first()
        if not existing:
            admin_user = User(
                username=admin_username,
                password_hash=generate_password_hash(admin_password),
                role='ADMIN'
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user '{admin_username}' successfully created.")
        else:
            print(f"Admin user '{admin_username}' already exists.")

if __name__ == "__main__":
    seed_admin()
