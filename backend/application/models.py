from .database import db
from datetime import datetime
from flask_security import UserMixin, RoleMixin 

user_roles = db.Table('user_roles',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))   

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    monthly_report_format = db.Column(db.String)
    send_daily_reminders = db.Column(db.Boolean)

    # user <-1-----n-> board
    boards = db.relationship('Board', backref='user', cascade='all, delete', lazy='subquery')

    active = db.Column(db.Boolean)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    
    # user <-m-----n-> role
    roles = db.relationship('Role', secondary=user_roles,backref=db.backref('users', lazy='subquery'))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class Board(db.Model):
    __tablename__ = 'board'
    board_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    board_name = db.Column(db.String(50), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    
    # board <-1-----n-> list
    lists = db.relationship('List', backref='board', cascade='all, delete', lazy='subquery')

class List(db.Model):
    __tablename__ = 'list'
    list_id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('board.board_id'))
    list_name = db.Column(db.String(50), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    
    # list <-1-----n-> card
    cards = db.relationship('Card', backref='list', cascade='all, delete', lazy='subquery')

class Card(db.Model):
    __tablename__ = 'card'
    card_id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('list.list_id'))
    created = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.now)
    
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    completed_datetime = db.Column(db.DateTime, default=None)
