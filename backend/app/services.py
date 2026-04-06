from sqlalchemy import desc
from .extensions import db
from .models import Match, MatchStatus, Participant, User, WalletTransaction, WalletTxnType

PAYOUT_TABLE = {
    1: 0.40,
    2: 0.20,
    3: 0.12,
    4: 0.08,
    5: 0.06,
    6: 0.05,
    7: 0.04,
    8: 0.03,
    9: 0.015,
    10: 0.015,
}


def create_wallet_txn(user_id, amount, txn_type, description):
    txn = WalletTransaction(
        user_id=user_id,
        amount=amount,
        transaction_type=txn_type,
        description=description,
    )
    db.session.add(txn)
    return txn


def join_match(user: User, match: Match, slot_number: int):
    if Participant.query.filter_by(user_id=user.id, match_id=match.id).first():
        raise ValueError('User has already joined this match')
    if not (1 <= slot_number <= match.total_slots):
        raise ValueError('Invalid slot number')
    if Participant.query.filter_by(match_id=match.id, slot_number=slot_number).first():
        raise ValueError('Slot already booked')
    if match.available_slots <= 0 or match.status not in [MatchStatus.OPEN.value, MatchStatus.FULL.value]:
        raise ValueError('Match is not open for joining')
    if not match.is_free and user.coins < match.entry_fee:
        raise ValueError('Insufficient wallet balance')

    participant = Participant(match_id=match.id, user_id=user.id, slot_number=slot_number)
    db.session.add(participant)

    if not match.is_free:
        user.coins -= match.entry_fee
        create_wallet_txn(user.id, -match.entry_fee, WalletTxnType.ENTRY.value, f'Entry fee for match #{match.id}')

    user.username_locked = True
    match.available_slots -= 1
    if match.available_slots == 0:
        match.status = MatchStatus.FULL.value

    db.session.commit()
    return participant


def calculate_results(match):
    participants = Participant.query.filter_by(match_id=match.id).all()

    # 🔥 POSITION POINT SYSTEM
    position_points = {
        1: 20,
        2: 15,
        3: 12,
        4: 10,
        5: 8,
        6: 6,
        7: 4,
        8: 3,
        9: 2,
        10: 1,
    }

    for p in participants:
        base = position_points.get(p.rank, 0)
        kill_points = p.kills * 2

        p.score = base + kill_points

    # 🔥 SORT FINAL LEADERBOARD
    participants.sort(key=lambda p: p.score, reverse=True)

    # 🔥 REASSIGN FINAL RANK (optional)
    for i, p in enumerate(participants):
        p.final_rank = i + 1

    # 🔥 DISTRIBUTE REWARD
    prize_pool = match.prize_pool

    rewards = {
        1: int(prize_pool * 0.5),
        2: int(prize_pool * 0.3),
        3: int(prize_pool * 0.2),
    }

    for p in participants:
        reward = rewards.get(p.final_rank, 0)
        p.reward_coins = reward

        if reward > 0:
            user = User.query.get(p.user_id)
            user.coins += reward

    db.session.commit()

    return participants
