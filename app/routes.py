# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from . import db
from .models import User, Message
from .forms import RegistrationForm, LoginForm, UpdateProfileForm, DeleteAccountForm, MessageForm
from .services.ai_service import get_ai_response

main_bp = Blueprint('main', __name__)


# --- Helper for File Upload ---
def save_avatar_file(form_file_data):
    if form_file_data:
        filename = secure_filename(form_file_data.filename)

        _, ext = os.path.splitext(filename)
        if not ext:
            flash("File must have an extension (e.g., .jpg, .png).", "warning")
            return None  # Or raise an error

        if ext.lower() not in current_app.config.get('UPLOAD_EXTENSIONS', ['.jpg', '.png', '.jpeg']):
            flash(f"Invalid file type. Allowed types: {', '.join(current_app.config.get('UPLOAD_EXTENSIONS'))}",
                  "danger")
            return None


        avatar_save_dir = os.path.join(current_app.root_path, 'static', 'user_avatars')
        if not os.path.exists(avatar_save_dir):
            os.makedirs(avatar_save_dir)
        avatar_path = os.path.join(avatar_save_dir, filename)
        form_file_data.save(avatar_path)
        path_to_store = f"user_avatars/{filename}"
        return path_to_store
    return None


# --- Authentication Routes ---
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat'))
    form = RegistrationForm()
    if form.validate_on_submit():
        avatar_rel_path = None
        if form.avatar.data:
            avatar_rel_path = save_avatar_file(form.avatar.data)
            if avatar_rel_path is None:
                return render_template('register.html', title='Register', form=form)

        user = User(username=form.username.data, avatar_filename=avatar_rel_path)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Congratulations, you are now a registered user!', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
            if "UNIQUE constraint failed: user.username" in str(e):  # More specific error
                form.username.errors.append("This username is already taken.")

    return render_template('register.html', title='Register', form=form)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('main.login'))

        login_user(user, remember=form.remember.data)
        if form.remember.data:
            session.permanent = True

        flash(f'Welcome back, {user.username}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.chat'))
    return render_template('login.html', title='Sign In', form=form)


@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


# --- Chat Route ---
@main_bp.route('/', methods=['GET', 'POST'])
@main_bp.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    form = MessageForm()
    if form.validate_on_submit() and request.method == 'POST':
        user_message_text = form.message_text.data

        msg_user = Message(content=user_message_text, author=current_user, is_from_ai=False)
        db.session.add(msg_user)

        recent_messages_for_ai = Message.query.filter_by(user_id=current_user.id) \
            .order_by(Message.timestamp.asc()).limit(10).all()

        ai_response_text = get_ai_response(user_message_text, chat_history=recent_messages_for_ai)

        if ai_response_text:
            msg_ai = Message(content=ai_response_text, author=current_user, is_from_ai=True)
            db.session.add(msg_ai)
        else:
            flash("The AI assistant could not respond at this time or the response was empty.", "warning")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving messages: {e}")
            flash("An error occurred while sending your message.", "danger")

        return redirect(url_for('main.chat'))

    messages = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp.asc()).all()
    return render_template('chat.html', title='Chat', form=form, messages=messages)

# --- User Profile and CRUD Operations ---

@main_bp.route('/profile')
@login_required
def profile():
    user = current_user
    recent_messages = user.messages.order_by(Message.timestamp.desc()).limit(5).all()
    delete_form_instance = DeleteAccountForm()

    return render_template('profile.html',
                           title='My Profile',
                           user=user,
                           recent_messages=recent_messages,
                           delete_form=delete_form_instance) # Pass the form instance


@main_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm(
        original_username=current_user.username)

    if form.validate_on_submit():
        if form.new_password.data:
            if not current_user.check_password(form.current_password.data):
                flash('Incorrect current password. New password not set.', 'danger')
                return render_template('edit_profile.html', title='Edit Profile', form=form)
            current_user.set_password(form.new_password.data)
            flash('Your password has been updated.', 'success')

        if form.username.data != current_user.username:
            existing_user = User.query.filter(User.username == form.username.data, User.id != current_user.id).first()
            if existing_user:
                flash('That username is already taken.', 'danger')
                return render_template('edit_profile.html', title='Edit Profile', form=form)
            current_user.username = form.username.data
            flash('Your username has been updated.', 'success')
        if form.avatar.data:
            if current_user.avatar_filename and 'default_avatar.png' not in current_user.avatar_filename:  # Assuming you might have a default
                old_avatar_path = os.path.join(current_app.root_path, 'static', current_user.avatar_filename)
                if os.path.exists(old_avatar_path):
                    try:
                        os.remove(old_avatar_path)
                    except Exception as e:
                        current_app.logger.error(f"Error deleting old avatar: {e}")

            avatar_file = save_avatar_file(form.avatar.data)
            if avatar_file:
                current_user.avatar_filename = avatar_file
                flash('Your avatar has been updated.', 'success')
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Profile update error: {e}")
            flash('An error occurred while updating your profile.', 'danger')

        return redirect(url_for('main.profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@main_bp.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    user_to_delete = User.query.get_or_404(current_user.id)
    Message.query.filter_by(user_id=user_to_delete.id).delete()

    if user_to_delete.avatar_filename:
        avatar_path = os.path.join(current_app.root_path, 'static', user_to_delete.avatar_filename)
        if os.path.exists(avatar_path):
            try:
                os.remove(avatar_path)
            except Exception as e:
                current_app.logger.error(f"Error deleting avatar on account deletion: {e}")

    db.session.delete(user_to_delete)
    try:
        db.session.commit()
        logout_user()
        flash('Your account and all associated data have been permanently deleted.', 'success')
        return redirect(url_for('main.register'))  # Or home page if you have one
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Account deletion error: {e}")
        flash('An error occurred while deleting your account.', 'danger')
        return redirect(url_for('main.profile'))


# --- Search ---
@main_bp.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    results = []
    if query:
        results = Message.query.filter(
            Message.user_id == current_user.id,
            Message.content.ilike(f'%{query}%')
        ).order_by(Message.timestamp.desc()).all()
        flash(f"Found {len(results)} messages matching '{query}'.", "info") if results else flash(
            f"No messages found for '{query}'.", "info")
    return render_template('search_results.html', title='Search Results', query=query, results=results)


