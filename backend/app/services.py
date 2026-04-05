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


def calculate_results(match: Match):
    participants = Participant.query.filter_by(match_id=match.id).order_by(desc(Participant.score), desc(Participant.kills), Participant.joined_at.asc()).all()
    for idx, participant in enumerate(participants, start=1):
        participant.rank = idx
        reward_pct = PAYOUT_TABLE.get(idx, 0)
        reward = int(match.prize_pool * reward_pct)
        participant.reward_coins = reward
        if reward > 0:
            participant.user.coins += reward
            create_wallet_txn(participant.user_id, reward, WalletTxnType.REWARD.value, f'Reward for rank #{idx} in match #{match.id}')

    match.status = MatchStatus.COMPLETED.value
    db.session.commit()
    return participants
