from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.user_model import UserModel
from utils.validators import is_valid_email, is_valid_password
from utils.security import hash_password, verify_password

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        identifier = request.form.get('username', '').strip() # Can be username or email
        password = request.form.get('password', '')

        if not identifier or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/login.html')

        # Find user by email or username
        user = None
        if '@' in identifier:
            user = UserModel.find_by_email(identifier)
        else:
            user = UserModel.find_by_username(identifier)

        if user and verify_password(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_email'] = user.email
            flash('Welcome back! Successfully logged in.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username/email or password.', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Basic validations
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('auth/signup.html')

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('auth/signup.html')

        if not is_valid_password(password):
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('auth/signup.html')

        try:
            # Check duplicate email
            if UserModel.find_by_email(email):
                flash('Email is already registered. Please login or use a different email.', 'error')
                return render_template('auth/signup.html')

            # Check duplicate username
            if UserModel.find_by_username(username):
                flash('Username is already taken.', 'error')
                return render_template('auth/signup.html')

            # Create User
            hashed = hash_password(password)
            UserModel.create(username, email, hashed)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'An error occurred during registration: {e}', 'error')

    return render_template('auth/signup.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

