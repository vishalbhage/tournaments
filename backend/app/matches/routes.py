from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
from ..extensions import db
from ..models import Match, MatchStatus, Participant, User, WalletTransaction
from ..services import join_match

match_bp = Blueprint('matches', __name__)


@match_bp.get('/matches')
def list_matches():
    matches = Match.query.order_by(Match.start_time.asc()).all()
    return jsonify([match.to_dict() for match in matches])


@match_bp.get('/matches/<int:match_id>')
@jwt_required(optional=True)
def match_details(match_id):
    match = Match.query.get_or_404(match_id)
    user_id = get_jwt_identity()
    current_user_joined = None
    if user_id:
        current_user_joined = Participant.query.filter_by(match_id=match.id, user_id=int(user_id)).first()
    booked_slots = [p.slot_number for p in Participant.query.filter_by(match_id=match.id).all()]
    response = match.to_dict(include_sensitive=bool(current_user_joined and match.status in [MatchStatus.FULL.value, MatchStatus.LIVE.value, MatchStatus.COMPLETED.value]))
    response['booked_slots'] = booked_slots
    response['participant'] = current_user_joined.to_dict() if current_user_joined else None
    return jsonify(response)


@match_bp.post('/matches/<int:match_id>/join')
@jwt_required()
def join_match_route(match_id):
    match = Match.query.get_or_404(match_id)
    user = User.query.get_or_404(int(get_jwt_identity()))
    slot_number = int((request.get_json(force=True) or {}).get('slot_number', 0))
    try:
        participant = join_match(user, match, slot_number)
    except ValueError as exc:
        db.session.rollback()
        return jsonify({'message': str(exc)}), 400

    return jsonify({
        'message': 'Match joined successfully',
        'participant': participant.to_dict(),
        'coins': user.coins,
    }), 201


@match_bp.get('/matches/<int:match_id>/leaderboard')
def leaderboard(match_id):
    match = Match.query.get_or_404(match_id)
    participants = Participant.query.filter_by(match_id=match.id).order_by(Participant.rank.asc().nullslast(), desc(Participant.score), desc(Participant.kills)).all()
    return jsonify({
        'match': match.to_dict(include_sensitive=False),
        'leaderboard': [p.to_dict() for p in participants],
    })


@match_bp.get('/my/matches')
@jwt_required()
def my_matches():
    user = User.query.get_or_404(int(get_jwt_identity()))
    data = []
    for participant in Participant.query.filter_by(user_id=user.id).order_by(Participant.joined_at.desc()).all():
        item = participant.to_dict()
        item['match'] = participant.match.to_dict(include_sensitive=participant.match.status in [MatchStatus.FULL.value, MatchStatus.LIVE.value, MatchStatus.COMPLETED.value])
        data.append(item)
    return jsonify(data)


@match_bp.get('/my/wallet')
@jwt_required()
def my_wallet():
    user = User.query.get_or_404(int(get_jwt_identity()))
    txns = WalletTransaction.query.filter_by(user_id=user.id).order_by(WalletTransaction.created_at.desc()).limit(50).all()
    return jsonify({
        'coins': user.coins,
        'transactions': [txn.to_dict() for txn in txns],
    })


@match_bp.get('/my/stats')
@jwt_required()
def my_stats():
    user = User.query.get_or_404(int(get_jwt_identity()))
    participations = Participant.query.filter_by(user_id=user.id).all()
    total = len(participations)
    wins = len([p for p in participations if p.rank == 1])
    top3 = len([p for p in participations if p.rank and p.rank <= 3])
    total_rewards = sum(p.reward_coins for p in participations)
    return jsonify({
        'matches_played': total,
        'wins': wins,
        'top3_finishes': top3,
        'total_rewards': total_rewards,
        'win_rate': round((wins / total) * 100, 2) if total else 0,
    })
