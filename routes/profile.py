from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models.user_model import UserModel
from services.wellness.statistics_service import StatisticsService
from services.journal_service import JournalService
from services.mongo_service import MongoService
from bson.objectid import ObjectId

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = UserModel.find_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    stats = StatisticsService.get_summary(user_id)
    
    # Get total journal entries
    db = MongoService.get_db()
    total_journals = 0
    if db is not None:
        total_journals = db["journals"].count_documents({"user_id": user_id})
        
    return render_template(
        'profile/index.html', 
        user=user, 
        stats=stats,
        total_journals=total_journals,
        total_sessions=stats.get('activities_completed', 0)
    )

@profile_bp.route('/update', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    name = request.form.get('name', '')
    bio = request.form.get('bio', '')
    avatar = request.form.get('avatar')
    
    UserModel.update_profile(user_id, name, bio, avatar)
    flash("Profile updated successfully.", "success")
    return redirect(url_for('profile.index'))
