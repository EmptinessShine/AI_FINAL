from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional, \
    StopValidation
from flask_wtf.file import FileField, FileAllowed
import os
from .models import User

# Helper functions
def get_upload_extensions_list():
    return current_app.config.get('UPLOAD_EXTENSIONS', ['.jpg', '.png', '.jpeg'])

def get_max_file_size_mb():
    return current_app.config.get('MAX_CONTENT_LENGTH', 2 * 1024 * 1024) // (1024 * 1024)

# Custom validator for file size (accesses config when called)
def validate_file_size_dynamic():
    def _validate_file_size(form, field):
        if field.data:
            max_bytes = get_max_file_size_mb() * 1024 * 1024
            try:
                field.data.seek(0, os.SEEK_END)
                file_length = field.data.tell()
                field.data.seek(0)

                if file_length > max_bytes:
                    raise ValidationError(f'File size must be less than {get_max_file_size_mb()}MB.')
            except Exception as e:
                current_app.logger.error(f"Could not determine file size accurately: {e}")
                raise ValidationError("Could not validate file size.")
    return _validate_file_size

class DynamicFileAllowed:
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if field.data and field.data.filename:
            allowed_extensions = get_upload_extensions_list()
            validator = FileAllowed(allowed_extensions, self.message or 'File type not allowed.')
            try:
                validator(form, field)
            except ValidationError as ve:
                raise ve
            except StopValidation:

                pass
            except Exception as e:
                current_app.logger.error(f"!!! Unexpected FileAllowed Error (not ValidationError or StopValidation): {e} | Type: {type(e)} !!!")
                raise ValidationError("An unexpected error occurred during file type validation. Check logs.")

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    avatar = FileField('Profile Picture (Optional)', validators=[
        Optional(), # <-- ADD THIS FIRST!
        DynamicFileAllowed(message='Invalid file type.'),
        validate_file_size_dynamic()
    ])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    avatar = FileField('Update Profile Picture', validators=[
        Optional(),
        DynamicFileAllowed(message='Invalid file type.'),
        validate_file_size_dynamic()
    ])
    current_password = PasswordField('Current Password (only if changing password)', validators=[Optional()])
    new_password = PasswordField('New Password (leave blank to keep current)', validators=[Optional(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[Optional(), EqualTo('new_password', message='New passwords must match.')])
    submit = SubmitField('Update Profile')

    def __init__(self, original_username, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_new_password(self, field):
        if field.data:
            if not self.current_password.data:
                raise ValidationError('Current password is required to set a new password.')

    def validate_confirm_new_password(self, field):
        if self.new_password.data and not field.data:
            raise ValidationError("Please confirm your new password.")

class MessageForm(FlaskForm):
    message_text = TextAreaField('Your Message', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Send')


class DeleteAccountForm(FlaskForm):
    submit = SubmitField('Delete My Account')
