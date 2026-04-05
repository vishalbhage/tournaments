from datetime import datetime
from flask import Blueprint, jsonify, request
from ..extensions import db
from ..models import Match, MatchStatus, Participant
from ..services import calculate_results
from ..utils import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.post('/matches')
@admin_required
def create_match():
    data = request.get_json(force=True)
    match = Match(
        title=data['title'],
        entry_fee=int(data['entry_fee']),
        prize_pool=int(data['prize_pool']),
        total_slots=int(data.get('total_slots', 50)),
        available_slots=int(data.get('total_slots', 50)),
        is_free=bool(data.get('is_free', False)),
        start_time=datetime.fromisoformat(data['start_time']),
        room_id=data.get('room_id'),
        room_password=data.get('room_password'),
        status=MatchStatus.OPEN.value,
    )
    db.session.add(match)
    db.session.commit()
    return jsonify(match.to_dict(include_sensitive=True)), 201


@admin_bp.put('/matches/<int:match_id>/status')
@admin_required
def update_match_status(match_id):
    match = Match.query.get_or_404(match_id)
    data = request.get_json(force=True)
    status = data.get('status')
    if status not in [m.value for m in MatchStatus]:
        return jsonify({'message': 'Invalid status'}), 400
    match.status = status
    if 'room_id' in data:
        match.room_id = data['room_id']
    if 'room_password' in data:
        match.room_password = data['room_password']
    db.session.commit()
    return jsonify(match.to_dict(include_sensitive=True))


@admin_bp.post('/matches/<int:match_id>/results')
@admin_required
def submit_results(match_id):
    match = Match.query.get_or_404(match_id)
    rows = request.get_json(force=True).get('results', [])
    if not rows:
        return jsonify({'message': 'Results payload is required'}), 400
    for row in rows:
        participant = Participant.query.filter_by(match_id=match.id, user_id=row['user_id']).first()
        if participant:
            participant.score = int(row.get('score', 0))
            participant.kills = int(row.get('kills', 0))
    db.session.commit()
    ranked = calculate_results(match)
    return jsonify({'message': 'Results processed', 'leaderboard': [p.to_dict() for p in ranked]})


@admin_bp.get('/dashboard')
@admin_required
def dashboard():
    return jsonify({
        'total_matches': Match.query.count(),
        'open_matches': Match.query.filter_by(status=MatchStatus.OPEN.value).count(),
        'completed_matches': Match.query.filter_by(status=MatchStatus.COMPLETED.value).count(),
        'participants': Participant.query.count(),
    })
