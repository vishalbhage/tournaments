from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_
from email_validator import validate_email, EmailNotValidError
from ..extensions import db
from ..models import User, WalletTxnType
from ..services import create_wallet_txn
from ..utils import generate_referral_code, save_uploaded_file

auth_bp = Blueprint('auth', __name__)


def _user_response(user):
    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()})


@auth_bp.post('/signup')
def signup():
    data = request.form or request.json or {}
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()
    username = (data.get('username') or '').strip().lower()
    full_name = (data.get('full_name') or '').strip()
    referral_code = (data.get('referral_code') or '').strip().upper() or None

    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError as exc:
        return jsonify({'message': str(exc)}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400
    if len(username) < 4:
        return jsonify({'message': 'Username must be at least 4 characters'}), 400
    if User.query.filter(or_(User.email == email, User.username == username)).first():
        return jsonify({'message': 'Email or username already exists'}), 409

    user = User(
        email=email,
        username=username,
        full_name=full_name or username,
        referral_code=generate_referral_code(),
        referred_by=referral_code,
    )
    user.set_password(password)

    if 'photo' in request.files:
        user.photo_url = save_uploaded_file(request.files['photo'], current_app.config['UPLOAD_FOLDER'])

    db.session.add(user)
    db.session.flush()

    if referral_code:
        referrer = User.query.filter_by(referral_code=referral_code).first()
        if referrer:
            referrer.coins += 100
            user.coins += 100
            create_wallet_txn(referrer.id, 100, WalletTxnType.REFERRAL.value, f'Referral bonus for {user.username}')
            create_wallet_txn(user.id, 100, WalletTxnType.REFERRAL.value, 'Referral signup bonus')

    db.session.commit()
    return _user_response(user), 201


@auth_bp.post('/login')
def login():
    data = request.get_json(force=True)
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401
    return _user_response(user)


@auth_bp.post('/google')
def google_login():
    data = request.get_json(force=True)
    email = (data.get('email') or '').strip().lower()
    google_id = (data.get('google_id') or '').strip()
    full_name = (data.get('full_name') or 'Google User').strip()
    photo_url = data.get('photo_url')
    username = (data.get('username') or email.split('@')[0]).strip().lower()

    if not email or not google_id:
        return jsonify({'message': 'email and google_id are required'}), 400

    user = User.query.filter(or_(User.google_id == google_id, User.email == email)).first()
    if user is None:
        original = username
        suffix = 1
        while User.query.filter_by(username=username).first():
            suffix += 1
            username = f'{original}{suffix}'
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            google_id=google_id,
            photo_url=photo_url,
            referral_code=generate_referral_code(),
        )
        db.session.add(user)
        db.session.commit()
    else:
        user.google_id = google_id
        user.photo_url = photo_url or user.photo_url
        db.session.commit()

    # In production, verify Google token with Google Identity services before issuing JWT.
    return _user_response(user)


@auth_bp.get('/me')
@jwt_required()
def me():
    user = User.query.get_or_404(int(get_jwt_identity()))
    return jsonify(user.to_dict())


@auth_bp.put('/profile')
@jwt_required()
def update_profile():
    user = User.query.get_or_404(int(get_jwt_identity()))
    data = request.form or request.json or {}

    if 'full_name' in data:
        user.full_name = data['full_name'].strip() or user.full_name

    requested_username = (data.get('username') or '').strip().lower()
    if requested_username and requested_username != user.username:
        if user.username_locked:
            return jsonify({'message': 'Username cannot be changed after joining a match'}), 400
        if User.query.filter(User.username == requested_username, User.id != user.id).first():
            return jsonify({'message': 'Username already taken'}), 409
        user.username = requested_username

    if 'photo' in request.files:
        user.photo_url = save_uploaded_file(request.files['photo'], current_app.config['UPLOAD_FOLDER'])

    db.session.commit()
    return jsonify(user.to_dict())


@auth_bp.get('/make-admin/<email>')
def make_admin(email):
    from ..models import User
    from ..extensions import db
    from flask import jsonify

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.role = 'admin'   # ✅ main fix

    db.session.commit()

    return jsonify({'message': f'{email} is now admin'})

