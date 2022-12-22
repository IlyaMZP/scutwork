from flask import render_template, flash, redirect, request, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user, login_fresh, confirm_login

from scutwork.components import db
from scutwork.forms.auth import LoginForm, RegisterForm
from scutwork.models import User
from scutwork.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.validate_password(form.password.data):
            if login_user(user, form.remember_me.data):
                flash('Login success.', 'info')
                return redirect_back()
            else:
                flash('Your account is blocked.', 'warning')
                return redirect(url_for('main.index'))
        flash('Invalid username or password.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    registration_id = request.args.get('id', None)
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        password = form.password.data
        if User.query.filter_by(username=username).first():
            flash('User exists.', 'warning')
            return redirect(url_for('.register'))
        #registration_id = request.form['registration_id']
        #if registration_id:
#            template = User.query.filter_by(username=registration_id, active=False).first()
#            user = User(name=name, group=template.group, username=username)
#            user.set_role(template.role.name)
#            db.session.delete(template)
#        else:
        user = User(name=name, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created.', 'info')
        return redirect(url_for('.login'))
    if form.errors:
        flash('Passwords do not match.', 'warning')
    if registration_id:
        return render_template('auth/register.html', form=form, registration_id=registration_id)
    else:
        return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect(url_for('main.index'))
