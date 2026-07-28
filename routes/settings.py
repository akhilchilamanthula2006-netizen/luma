from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models.user_model import UserModel
from werkzeug.security import generate_password_hash, check_password_hash

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    user = UserModel.find_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
        
    return render_template('settings/index.html', user=user)

@settings_bp.route('/update', methods=['POST'])
def update_settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    theme = request.form.get('theme', 'light')
    notifications = request.form.get('notifications') == 'on'
    ai_personalization = request.form.get('ai_personalization') == 'on'
    
    UserModel.update_settings(user_id, theme, notifications, ai_personalization)
    
    # Store theme in session so we don't need a DB query on every page load
    session['theme'] = theme
    
    flash("Settings updated successfully.", "success")
    return redirect(url_for('settings.index'))

@settings_bp.route('/password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    user = UserModel.find_by_id(user_id)
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not check_password_hash(user.password_hash, current_password):
        flash("Incorrect current password.", "error")
        return redirect(url_for('settings.index'))
        
    if new_password != confirm_password:
        flash("New passwords do not match.", "error")
        return redirect(url_for('settings.index'))
        
    UserModel.update_password(user_id, generate_password_hash(new_password))
    flash("Password updated successfully.", "success")
    return redirect(url_for('settings.index'))
