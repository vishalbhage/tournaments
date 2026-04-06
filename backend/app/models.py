from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


# ================= ENUMS ================= #

class UserRole(str, Enum):
    USER = 'user'
    ADMIN = 'admin'


class MatchStatus(str, Enum):
    OPEN = 'open'
    FULL = 'full'
    LIVE = 'live'
    COMPLETED = 'completed'
    CLOSED = 'closed'


class WalletTxnType(str, Enum):
    CREDIT = 'credit'
    DEBIT = 'debit'
    REWARD = 'reward'
    ENTRY = 'entry'
    REFERRAL = 'referral'


# ================= USER ================= #

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(80), nullable=False)

    photo_url = db.Column(db.String(255))
    youtube_link = db.Column(db.String(255))  # 🔥 NEW

    role = db.Column(db.String(20), default=UserRole.USER.value, nullable=False)
    coins = db.Column(db.Integer, default=1000, nullable=False)

    referral_code = db.Column(db.String(12), unique=True, nullable=False)
    referred_by = db.Column(db.String(12))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    participants = db.relationship('Participant', back_populates='user')
    transactions = db.relationship('WalletTransaction', back_populates='user')

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN.value

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return bool(self.password_hash and check_password_hash(self.password_hash, password))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'coins': self.coins,
            'role': self.role,
            'youtube_link': self.youtube_link,
        }


# ================= MATCH ================= #

class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(120), nullable=False)
    match_type = db.Column(db.String(20), default="solo")  # 🔥 NEW

    entry_fee = db.Column(db.Integer, nullable=False)
    prize_pool = db.Column(db.Integer, nullable=False)

    total_slots = db.Column(db.Integer, default=50)

    status = db.Column(db.String(20), default=MatchStatus.OPEN.value)

    start_time = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime)  # 🔥 IMPORTANT

    room_id = db.Column(db.String(50))
    room_password = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    participants = db.relationship(
        'Participant',
        back_populates='match',
        cascade='all, delete-orphan'
    )

    # 🔥 AUTO CALCULATED (NO DB FIELD)
    @property
    def spots_left(self):
        return self.total_slots - len(self.participants)

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'title': self.title,
            'entry_fee': self.entry_fee,
            'prize_pool': self.prize_pool,
            'total_slots': self.total_slots,
            'spots_left': self.spots_left,
            'status': self.status,
            'start_time': self.start_time.isoformat(),
        }

        if include_sensitive:
            data['room_id'] = self.room_id
            data['room_password'] = self.room_password

        return data


# ================= PARTICIPANT ================= #

class Participant(db.Model):
    __tablename__ = 'participants'
    __table_args__ = (
        db.UniqueConstraint('match_id', 'user_id', name='uq_match_user'),
        db.UniqueConstraint('match_id', 'slot_number', name='uq_match_slot'),
    )

    id = db.Column(db.Integer, primary_key=True)

    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    slot_number = db.Column(db.Integer, nullable=False)

    kills = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer)

    reward_coins = db.Column(db.Integer, default=0)

    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='participants')
    match = db.relationship('Match', back_populates='participants')

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'slot_number': self.slot_number,
            'kills': self.kills,
            'rank': self.rank,
            'reward_coins': self.reward_coins,
        }


# ================= WALLET ================= #

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)

    description = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='transactions')
