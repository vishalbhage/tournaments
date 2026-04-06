from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models import Match, MatchStatus, Participant
from ..services import calculate_results
from ..utils import admin_required

admin_bp = Blueprint('admin', __name__)


# -----------------------------
# CREATE MATCH
# -----------------------------
@admin_bp.delete('/matches/<int:match_id>')
@admin_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    return jsonify({'message': 'Match deleted'})
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
            room_id=data.get('room_id'),
            room_password=data.get('room_password'),
            status=MatchStatus.OPEN.value,
        )

        db.session.add(match)
        db.session.commit()

        return jsonify(match.to_dict(include_sensitive=True)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating match: {str(e)}'}), 500


# -----------------------------
# UPDATE MATCH STATUS
# -----------------------------
@admin_bp.put('/matches/<int:match_id>/status')
@admin_required
def update_match_status(match_id):
    try:
        match = Match.query.get_or_404(match_id)
        data = request.get_json(force=True)

        status = data.get('status')
        if status not in [m.value for m in MatchStatus]:
            return jsonify({'message': 'Invalid status'}), 400

        match.status = status

        # Update room details only when match is FULL or LIVE
        if status in [MatchStatus.FULL.value, MatchStatus.LIVE.value]:
            if 'room_id' in data:
                match.room_id = data['room_id']
            if 'room_password' in data:
                match.room_password = data['room_password']

        db.session.commit()

        return jsonify(match.to_dict(include_sensitive=True))

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating match: {str(e)}'}), 500


# -----------------------------
# SUBMIT RESULTS (SAFE VERSION)
# -----------------------------
@admin_bp.post('/matches/<int:match_id>/results')
@admin_required
def submit_results(match_id):
    try:
        match = Match.query.get_or_404(match_id)

        # 🚫 Prevent duplicate reward distribution
        if match.status == MatchStatus.COMPLETED.value:
            return jsonify({'message': 'Results already submitted'}), 400

        payload = request.get_json(force=True)
        rows = payload.get('results', [])

        if not rows:
            return jsonify({'message': 'Results payload is required'}), 400

        updated_count = 0

        for row in rows:
            participant = Participant.query.filter_by(
                match_id=match.id,
                user_id=row['user_id']
            ).first()

            if participant:
                participant.score = int(row.get('score', 0))
                participant.kills = int(row.get('kills', 0))
                updated_count += 1

        if updated_count == 0:
            return jsonify({'message': 'No valid participants found'}), 400

        db.session.commit()

        # 🔥 Calculate ranking + rewards
        ranked = calculate_results(match)

        return jsonify({
            'message': 'Results processed successfully',
            'total_updated': updated_count,
            'leaderboard': [p.to_dict() for p in ranked]
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error processing results: {str(e)}'}), 500


# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@admin_bp.get('/dashboard')
@admin_required
def dashboard():
    try:
        return jsonify({
            'total_matches': Match.query.count(),
            'open_matches': Match.query.filter_by(status=MatchStatus.OPEN.value).count(),
            'live_matches': Match.query.filter_by(status=MatchStatus.LIVE.value).count(),
            'completed_matches': Match.query.filter_by(status=MatchStatus.COMPLETED.value).count(),
            'participants': Participant.query.count(),
        })

    except Exception as e:
        return jsonify({'message': f'Error loading dashboard: {str(e)}'}), 500


# -----------------------------
# GET ALL MATCHES (ADMIN VIEW)
# -----------------------------
@admin_bp.get('/matches')
@admin_required
def get_all_matches():
    try:
        matches = Match.query.order_by(Match.created_at.desc()).all()

        return jsonify([
            m.to_dict(include_sensitive=True)
            for m in matches
        ])

    except Exception as e:
        return jsonify({'message': f'Error fetching matches: {str(e)}'}), 500
