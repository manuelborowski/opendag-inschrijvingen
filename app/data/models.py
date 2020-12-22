from app import log, db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint
import inspect

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    class USER_TYPE:
        LOCAL = 'local'
        OAUTH = 'oauth'

    @staticmethod
    def get_zipped_types():
        return list(zip(['local', 'oauth'], ['LOCAL', 'OAUTH']))

    class LEVEL:
        USER = 1
        SUPERVISOR = 3
        ADMIN = 5

        ls = ["GEBRUIKER", "SECRETARIAAT", "ADMINISTRATOR"]

        @staticmethod
        def i2s(i):
            if i == 1:
                return User.LEVEL.ls[0]
            elif i == 3:
                return User.LEVEL.ls[1]
            if i == 5:
                return User.LEVEL.ls[2]

    @staticmethod
    def get_zipped_levels():
        return list(zip(["1", "3", "5"], User.LEVEL.ls))

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    username = db.Column(db.String(256))
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    password_hash = db.Column(db.String(256))
    level = db.Column(db.Integer)
    user_type = db.Column(db.String(256))
    last_login = db.Column(db.DateTime())
    settings = db.relationship('Settings', cascade='all, delete', backref='user', lazy='dynamic')

    @property
    def is_local(self):
        return self.user_type == User.USER_TYPE.LOCAL

    @property
    def is_oauth(self):
        return self.user_type == User.USER_TYPE.OAUTH

    @property
    def is_at_least_user(self):
        return self.level >= User.LEVEL.USER

    @property
    def is_strict_user(self):
        return self.level == User.LEVEL.USER

    @property
    def is_at_least_supervisor(self):
        return self.level >= User.LEVEL.SUPERVISOR

    @property
    def is_at_least_admin(self):
        return self.level >= User.LEVEL.ADMIN

    @property
    def password(self):
        raise AttributeError('Paswoord kan je niet lezen.')

    @password.setter
    def password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        else:
            return True

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def log(self):
        return '<User: {}/{}>'.format(self.id, self.username)

    def ret_dict(self):
        return {'id': self.id, 'DT_RowId': self.id, 'email': self.email, 'username': self.username, 'first_name': self.first_name,
                'last_name': self.last_name,
                'level': User.LEVEL.i2s(self.level), 'user_type': self.user_type, 'last_login': self.last_login, 'chbx': ''}


class Settings(db.Model):
    __tablename__ = 'settings'

    class SETTING_TYPE:
        E_INT = 'INT'
        E_STRING = 'STRING'
        E_FLOAT = 'FLOAT'
        E_BOOL = 'BOOL'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    value = db.Column(db.String(256))
    type = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    UniqueConstraint('name', 'user_id')

    def log(self):
        return '<Setting: {}/{}/{}/{}>'.format(self.id, self.name, self.value, self.type)


class EndUser(db.Model):
    __tablename__ = 'end_users'

    class Profile:
        E_CLB = 'CLB'
        E_SCHOLENGEMEENSCHAP = 'Scholengemeenschap'
        E_INTERNAAT = 'Internaat'
        E_SCHOOL = 'School'
        E_GAST = 'Gast'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    code = db.Column(db.String(256))
    timeslot = db.Column(db.DateTime())
    last_login = db.Column(db.DateTime())
    profile = db.Column(db.String(256))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), default=None)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'{self.email}/{self.full_name()}/{self.code}/{self.profile}'

class Room(db.Model):
    __tablename__ = 'rooms'

    class State:
        E_NEW = 'nieuw'
        E_OPEN = 'open'
        E_CLOSING = 'afsluiten'
        E_CLOSED = 'gesloten'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), default='')
    info = db.Column(db.String(256), default='')
    state = db.Column(db.String(256), default=State.E_NEW)
    code = db.Column(db.String(256))
    guests = db.relationship('EndUser', cascade='all, delete', backref='room', lazy='dynamic')
    floor_id = db.Column(db.Integer, db.ForeignKey('floors.id'))

    def __repr__(self):
        return f'{self.code}/{self.name}'

class Floor(db.Model):
    __tablename__ = 'floors'

    class Level:
        E_CLB = EndUser.Profile.E_CLB
        E_INTERNAAT = EndUser.Profile.E_INTERNAAT
        E_SCHOLENGEMEENSCHAP = EndUser.Profile.E_SCHOLENGEMEENSCHAP

        @staticmethod
        def get_enum_list():
            attributes = inspect.getmembers(Floor.Level, lambda a: not (inspect.isroutine(a)))
            enums = [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]
            return enums

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), default='')
    info = db.Column(db.String(256), default='')
    level = db.Column(db.String(256))
    rooms = db.relationship('Room', cascade='all, delete', backref='floor', lazy='dynamic')

    def __repr__(self):
        return f'{self.level}'


def get_columns(sqlalchemy_object):
    columns = sqlalchemy_object.__dict__
    del columns['_sa_instance_state']
    return columns