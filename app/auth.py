from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

def validate_username(username: str) -> tuple[bool, str]:
    if not username or len(username) < 5:
        return False, "Username must be at least 5 characters long."
    has_upper = any(c.isupper() for c in username)
    has_lower = any(c.islower() for c in username)
    special_chars = set("$%*")
    has_special = any(c in special_chars for c in username)

    missing = []
    if not has_upper:
        missing.append("at least one uppercase letter")
    if not has_lower:
        missing.append("at least one lowercase letter")
    if not has_special:
        missing.append("at least one special character from $ % *")

    if missing:
        return False, f"Username must contain {', '.join(missing)}."
    return True, ""

def validate_password(password: str) -> tuple[bool, str]:
    if not password or len(password) < 5:
        return False, "Password must be at least 5 characters long."
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    special_chars = set("$%*")
    has_special = any(c in special_chars for c in password)

    missing = []
    if not has_letter:
        missing.append("at least one letter")
    if not has_digit:
        missing.append("at least one numeric digit")
    if not has_special:
        missing.append("at least one special character from $ % *")

    if missing:
        return False, f"Password must contain {', '.join(missing)}."
    return True, ""

@auth_bp.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('game.index'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('game.index'))

    username_error = None
    password_error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Server-side validation
        valid_user, user_err = validate_username(username)
        if not valid_user:
            username_error = user_err

        valid_pass, pass_err = validate_password(password)
        if not valid_pass:
            password_error = pass_err

        # Check existing user if username format is valid
        if valid_user:
            existing = User.query.filter_by(username=username).first()
            if existing:
                username_error = "Username already exists. Please choose another."

        if username_error or password_error:
            return render_template(
                'register.html',
                username=username,
                username_error=username_error,
                password_error=password_error
            )

        # Create new PLAYER
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='PLAYER'
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('game.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid username or password.", "danger")
            return render_template('login.html', username=username)

        login_user(user)
        flash(f"Welcome back, {user.username}!", "success")
        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('game.index'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
