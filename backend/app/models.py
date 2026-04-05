from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


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


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(80), nullable=False)
    photo_url = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(20), default=UserRole.USER.value, nullable=False)
    coins = db.Column(db.Integer, default=1000, nullable=False)
    username_locked = db.Column(db.Boolean, default=False, nullable=False)
    referral_code = db.Column(db.String(12), unique=True, nullable=False)
    referred_by = db.Column(db.String(12), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    participants = db.relationship('Participant', back_populates='user', lazy=True)
    transactions = db.relationship('WalletTransaction', back_populates='user', lazy=True)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN.value

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return bool(self.password_hash and check_password_hash(self.password_hash, password))

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'photo_url': self.photo_url,
            'role': self.role,
            'is_admin': self.is_admin,
            'coins': self.coins,
            'username_locked': self.username_locked,
            'referral_code': self.referral_code,
            'referred_by': self.referred_by,
            'created_at': self.created_at.isoformat(),
        }


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    entry_fee = db.Column(db.Integer, nullable=False)
    prize_pool = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, default=50, nullable=False)
    available_slots = db.Column(db.Integer, default=50, nullable=False)
    is_free = db.Column(db.Boolean, default=False, nullable=False)
    room_id = db.Column(db.String(50), nullable=True)
    room_password = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default=MatchStatus.OPEN.value, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    participants = db.relationship(
        'Participant',
        back_populates='match',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self, include_sensitive: bool = False):
        data = {
            'id': self.id,
            'title': self.title,
            'entry_fee': self.entry_fee,
            'prize_pool': self.prize_pool,
            'total_slots': self.total_slots,
            'available_slots': self.available_slots,
            'spots_left': self.available_slots,
            'is_free': self.is_free,
            'status': self.status,
            'start_time': self.start_time.isoformat(),
        }

        if include_sensitive:
            data['room_id'] = self.room_id
            data['room_password'] = self.room_password

        return data


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
    score = db.Column(db.Integer, default=0, nullable=False)
    kills = db.Column(db.Integer, default=0, nullable=False)
    rank = db.Column(db.Integer, nullable=True)
    reward_coins = db.Column(db.Integer, default=0, nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='participants')
    match = db.relationship('Match', back_populates='participants')

    def to_dict(self):
        return {
            'id': self.id,
            'match_id': self.match_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'slot_number': self.slot_number,
            'score': self.score,
            'kills': self.kills,
            'rank': self.rank,
            'reward_coins': self.reward_coins,
            'joined_at': self.joined_at.isoformat(),
        }


class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='transactions')

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
        }
