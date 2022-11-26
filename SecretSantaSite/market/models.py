from market import db, login_manager
from flask_login import UserMixin

from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    invite_code = db.Column(db.String())
    wishlist = db.Column(db.String())
    can_enter = db.Column(db.Boolean())

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = plain_text_password

    def check_password_correction(self, attempted_password):
        return self.password_hash == attempted_password

class Event(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    started = db.Column(db.Boolean)
    displayed = db.Column(db.Boolean())
    users = db.Column(db.String())

    def set_owner(self, current_user):
        self.owner = current_user.id
        db.session.commit()


class Entry(db.Model):
    invite_code = db.Column(db.String())
    wishlist = db.Column(db.String(), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    owner_name = db.Column(db.String())
    id = db.Column(db.Integer(), primary_key=True)
    def set_owner(self, current_user):
        self.owner = current_user.id
        self.owner_name = current_user.username        
        current_user.invite_code = self.invite_code
        current_user.wishlist = self.wishlist
        db.session.commit()

    
class Data(db.Model):
    invite_code = db.Column(db.String())
    owner = db.Column(db.String())
    results = db.Column(db.String())
    id = db.Column(db.Integer(), primary_key=True)
    def set_owner(self, current_user):
        self.owner = current_user.username
        