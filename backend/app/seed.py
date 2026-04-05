from datetime import datetime, timedelta
from .extensions import db
from .models import Match, User, UserRole
from .utils import generate_referral_code


def run_seed():
    if User.query.filter_by(email='admin@ffarena.com').first() is None:
        admin = User(
            email='admin@ffarena.com',
            username='admin_master',
            full_name='Platform Admin',
            role=UserRole.ADMIN.value,
            referral_code=generate_referral_code(),
            coins=100000,
        )
        admin.set_password('Admin@123')
        db.session.add(admin)

    if Match.query.count() == 0:
        fees = [0, 200, 500, 1000, 2000, 5000]
        for index, fee in enumerate(fees, start=1):
            match = Match(
                title='Free Entry Match' if fee == 0 else f'Battle Royale {fee} Coins',
                entry_fee=fee,
                prize_pool=max(1000, fee * 50),
                total_slots=50,
                available_slots=50,
                is_free=fee == 0,
                status='open',
                start_time=datetime.utcnow() + timedelta(hours=index * 3),
            )
            db.session.add(match)

    db.session.commit()
