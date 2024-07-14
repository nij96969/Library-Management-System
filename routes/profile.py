from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Profile, User
from forms import ProfileForm
from werkzeug.utils import secure_filename
import os

profile = Blueprint('profile', __name__)

@profile.route('/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        # Update User model fields
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data

        # Update or create Profile
        if current_user.profile:
            profile = current_user.profile
        else:
            profile = Profile(user_id=current_user.user_id)
            db.session.add(profile)

        profile.bio = form.bio.data
        profile.location = form.location.data
        profile.birthdate = form.birthdate.data
        profile.website = form.website.data

        # Handle profile picture upload
        if form.profile_picture.data:
            filename = secure_filename(form.profile_picture.data.filename)
            file_path = os.path.join('static', 'profile_pics', filename)
            form.profile_picture.data.save(file_path)
            profile.profile_picture = file_path

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.dashboard'))
    elif request.method == 'GET':
        # Populate form with existing data
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        if current_user.profile:
            form.bio.data = current_user.profile.bio
            form.location.data = current_user.profile.location
            form.birthdate.data = current_user.profile.birthdate
            form.website.data = current_user.profile.website

    return render_template('profile.html', form=form)