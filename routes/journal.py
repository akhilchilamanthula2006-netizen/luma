from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
import logging

from services.journal_service import JournalService

logger = logging.getLogger(__name__)
journal_bp = Blueprint('journal', __name__, url_prefix='/journal')

@journal_bp.route('/')
def index():
    """Renders the main journal interface in 'New Reflection' mode."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    entries = JournalService.list_entries(user_id)

    return render_template(
        'journal/index.html',
        entries=entries,
        entry=None
    )

@journal_bp.route('/<entry_id>')
def view_entry(entry_id):
    """Renders the journal interface with a specific entry pre-loaded in the editor."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    entry = JournalService.get_entry(entry_id, user_id)

    if not entry:
        flash("Journal entry not found or access denied.", "error")
        return redirect(url_for('journal.index'))

    entries = JournalService.list_entries(user_id)

    return render_template(
        'journal/index.html',
        entries=entries,
        entry=entry
    )

@journal_bp.route('/save', methods=['POST'])
def save():
    """Handles creating a new journal entry or updating an existing one."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    username = session.get('username', 'there')
    
    entry_id = request.form.get('entry_id')
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    if not content:
        flash("Journal content cannot be empty.", "error")
        if entry_id:
            return redirect(url_for('journal.view_entry', entry_id=entry_id))
        return redirect(url_for('journal.index'))

    if not title:
        title = "Untitled Reflection"

    saved_entry = JournalService.save_entry(
        user_id=user_id,
        username=username,
        title=title,
        content=content,
        entry_id=entry_id if entry_id else None
    )

    if not saved_entry:
        flash("Failed to save journal entry. Please try again.", "error")
        if entry_id:
            return redirect(url_for('journal.view_entry', entry_id=entry_id))
        return redirect(url_for('journal.index'))

    flash("Reflection saved successfully!", "success")
    return redirect(url_for('journal.view_entry', entry_id=saved_entry.id))

@journal_bp.route('/delete/<entry_id>', methods=['POST'])
def delete(entry_id):
    """Handles soft-deleting an entry."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    success = JournalService.delete_entry(entry_id, user_id)

    if success:
        flash("Reflection deleted successfully.", "success")
    else:
        flash("Failed to delete reflection.", "error")

    return redirect(url_for('journal.index'))

@journal_bp.route('/verify-password', methods=['POST'])
def verify_journal_password():
    """Verify the logged-in user's password before granting access to the journal."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated.'}), 401

    data = request.get_json(silent=True) or {}
    password = data.get('password', '')

    if not password:
        return jsonify({'success': False, 'error': 'Incorrect password.'}), 400

    user_id = session['user_id']
    user = None

    try:
        from bson import ObjectId
        from models.user_model import UserModel
        user = UserModel.get_collection().find_one({"_id": ObjectId(user_id)})
    except Exception:
        pass

    if not user and 'username' in session:
        from models.user_model import UserModel
        user = UserModel.get_collection().find_one({"username": session['username']})

    if not user and 'user_email' in session:
        from models.user_model import UserModel
        user = UserModel.get_collection().find_one({"email": session['user_email']})

    if not user:
        return jsonify({'success': False, 'error': 'User record not found.'}), 404

    from utils.security import verify_password
    password_hash = user.get('password_hash', '')

    if verify_password(password_hash, password):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Incorrect password.'}), 400
