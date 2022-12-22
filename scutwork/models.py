import os
from datetime import date, timedelta
from flask import current_app
from flask_login import UserMixin
from flask_avatars import Identicon
from werkzeug.security import generate_password_hash, check_password_hash

from scutwork.components import db


class Paragraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(128), nullable=False)
    header = db.Column(db.String(128), nullable=False)
    body = db.Column(db.Text, nullable=False)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', back_populates='role')
    name = db.Column(db.String(64), unique=True)

    @staticmethod
    def init_roles():
        roles = { 'Student', 'Teacher', 'Admin' }
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
        db.session.commit()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    pfp_s = db.Column(db.String(64))
    pfp_m = db.Column(db.String(64))
    pfp_l = db.Column(db.String(64))
    pfp_raw = db.Column(db.String(64))
    active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', back_populates='users')
    finals_score = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_pfp()
        self.set_role()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def block(self):
        self.active = False
        db.session.commit()

    def unblock(self):
        self.active = True
        db.session.commit()

    def set_role(self, role_name='Student'):
        self.role = Role.query.filter_by(name=role_name).first()
        db.session.commit()

    def set_score(self, score):
        if self.finals_score is None:
            self.finals_score = score
            db.session.commit()

    def generate_pfp(self):
        pfp = Identicon()
        filenames = pfp.generate(text=self.username)
        self.pfp_s = filenames[0]
        self.pfp_m = filenames[1]
        self.pfp_l = filenames[2]
        db.session.commit()

    @property
    def is_admin(self):
        return self.role.name == 'Admin'

    @property
    def is_teacher(self):
        return self.role.name == 'Teacher' or self.role.name == 'Admin'

    @property
    def is_active(self):
        return self.active


@db.event.listens_for(User, 'after_delete', named=True)
def delete_avatars(**kwargs):
    target = kwargs['target']
    for filename in [target.pfp_s, target.pfp_m, target.pfp_l, target.pfp_raw]:
        if filename is not None:
            path = os.path.join(current_app.config['AVATARS_SAVE_PATH'], filename)
            if os.path.exists(path):
                os.remove(path)
