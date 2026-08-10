from datetime import datetime, timezone
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='PLAYER')  # 'ADMIN' or 'PLAYER'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    games = db.relationship('Game', backref='user', lazy=True)

    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    @property
    def is_player(self):
        return self.role == 'PLAYER'


class Word(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(5), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    games = db.relationship('Game', backref='word', lazy=True)


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='IN_PROGRESS')  # 'IN_PROGRESS', 'WON', 'LOST'
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    finished_at = db.Column(db.DateTime, nullable=True)

    guesses = db.relationship('Guess', backref='game', lazy=True, order_by='Guess.sequence_number')


class Guess(db.Model):
    __tablename__ = 'guesses'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    guess_word = db.Column(db.String(5), nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False)  # 1-5
    result_pattern = db.Column(db.String(50), nullable=False)  # e.g., 'GREEN,ORANGE,GREY,GREY,GREEN'
    guessed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
