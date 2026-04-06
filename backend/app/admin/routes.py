from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models import Match, MatchStatus, Participant, User
from ..services import calculate_results
from ..utils import admin_required

admin_bp = Blueprint('admin', __name__)


# -----------------------------
# CREATE MATCH
# -----------------------------
@admin_bp.post('/matches')
@admin_required
def create_match():
    try:
        data = request.get_json(force=True)

        match = Match(
            title=data['title'],
            entry_fee=int(data['entry_fee']),
            prize_pool=int(data['prize_pool']),
            total_slots=int(data.get('total_slots', 50)),
            available_slots=int(data.get('total_slots', 50)),
            is_free=bool(data.get('is_free', False)),
            start_time=datetime.fromisoformat(data['start_time']),
            status=MatchStatus.OPEN.value,
        )

        db.session.add(match)
        db.session.commit()

        return jsonify(match.to_dict(include_sensitive=True)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# -----------------------------
# DELETE MATCH
# -----------------------------
@admin_bp.delete('/matches/<int:match_id>')
@admin_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)

    db.session.delete(match)
    db.session.commit()

    return jsonify({'message': 'Match deleted'})


# -----------------------------
# UPDATE MATCH
# -----------------------------
@admin_bp.put('/matches/<int:match_id>')
@admin_required
def update_match(match_id):
    try:
        match = Match.query.get_or_404(match_id)
        data = request.get_json(force=True)

        if 'status' in data:
            if data['status'] in [m.value for m in MatchStatus]:
                match.status = data['status']

        if 'room_id' in data:
            match.room_id = data['room_id']

        if 'room_password' in data:
            match.room_password = data['room_password']

        db.session.commit()

        return jsonify(match.to_dict(include_sensitive=True))

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# -----------------------------
# AUTO RESULT SYSTEM (FINAL 🔥)
# -----------------------------
@admin_bp.post('/matches/<int:match_id>/results')
@admin_required
def submit_results(match_id):
    try:
        match = Match.query.get_or_404(match_id)

        if match.status == MatchStatus.COMPLETED.value:
            return jsonify({'message': 'Already completed'}), 400

        data = request.get_json(force=True)
        rows = data.get('results', [])

        if not rows:
            return jsonify({'message': 'Results required'}), 400

        updated = 0

        # 🔥 STEP 1: SAVE RANK + KILLS
        for row in rows:
            participant = Participant.query.filter_by(
                match_id=match.id,
                user_id=row['user_id']
            ).first()

            if participant:
                participant.rank = int(row.get('rank', 0))
                participant.kills = int(row.get('kills', 0))
                updated += 1

        if updated == 0:
            return jsonify({'message': 'No participants found'}), 400

        db.session.commit()

        # 🔥 STEP 2: CALCULATE SCORE + FINAL RANK + REWARD
        ranked = calculate_results(match)

        # 🔥 STEP 3: COMPLETE MATCH
        match.status = MatchStatus.COMPLETED.value
        db.session.commit()

        return jsonify({
            'message': 'Results processed successfully',
            'leaderboard': [p.to_dict() for p in ranked]
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# -----------------------------
# ADMIN MATCH LIST
# -----------------------------
@admin_bp.get('/matches')
@admin_required
def get_all_matches():
    matches = Match.query.order_by(Match.created_at.desc()).all()

    return jsonify([
        m.to_dict(include_sensitive=True)
        for m in matches
    ])
