import os
import datetime
import yaml
from glob import glob
#from datetime import date, timedelta
from flask import render_template, flash, redirect, url_for, current_app, send_from_directory, request, abort, Blueprint, make_response
from flask_login import login_required, current_user
#from sqlalchemy import or_

from scutwork.models import Paragraph
from scutwork.components import db
from scutwork.decorators import admin_required
from scutwork.models import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    paragraphs = Paragraph.query.all()
    return render_template('main/index.html', paragraphs=paragraphs)


@main_bp.route('/profile')
@login_required
def profile():
    if current_user.is_teacher:
        results = dict()
        for yml_file in glob('submissions/*.yaml'):
            timestamp = os.path.basename(yml_file)[:-5]
            results[timestamp] = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%H:%M:%S %Y-%m-%d')
        return render_template('main/profile.html', results=results)
    if current_user.finals_score is not None:
        return render_template('main/profile.html', user_result=current_user.finals_score)
    return render_template('main/profile.html')


@main_bp.route('/manage_users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)


@main_bp.route('/set_teacher/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def set_teacher(user_id):
    to_edit = User.query.get(user_id)
    if to_edit:
        to_edit.set_role("Teacher")
        flash('Success.', 'info')
    return redirect(url_for('main.manage_users'))


@main_bp.route('/set_student/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def set_student(user_id):
    to_edit = User.query.get(user_id)
    if to_edit:
        to_edit.set_role("Student")
        flash('Success.', 'info')
    return redirect(url_for('main.manage_users'))

    
@main_bp.route('/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    to_delete = User.query.get(user_id)
    if to_delete:
        db.session.delete(to_delete)
        db.session.commit()
        flash('Success.', 'info')
    return redirect(url_for('main.manage_users'))


@main_bp.route('/submissions/<path:filename>')
@login_required
def get_submission(filename):
    path = os.path.join('submissions/', filename + '.yaml')
    if current_user.is_teacher:
        return send_from_directory(current_app.config['SUBMISSIONS_SAVE_PATH'], filename + '.yaml')
    else:
        with open(path, 'r') as stream:
            res_d = yaml.load(stream, yaml.FullLoader)
        if current_user.username == res_d['username']:
            return send_from_directory(current_app.config['SUBMISSIONS_SAVE_PATH'], filename + '.yaml')
    return abort(403)


@main_bp.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)


@main_bp.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response


@main_bp.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')


@main_bp.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')


@main_bp.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')
