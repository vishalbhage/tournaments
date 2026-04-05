import os
import secrets
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from .models import User, UserRole


def generate_referral_code(length=8):
    return secrets.token_hex(length // 2).upper()


def save_uploaded_file(file_storage, upload_folder):
    ext = os.path.splitext(file_storage.filename or '')[-1].lower() or '.jpg'
    filename = f"profile_{secrets.token_hex(8)}{ext}"
    path = os.path.join(upload_folder, filename)
    file_storage.save(path)
    return f'/uploads/{filename}'


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = int(get_jwt_identity())
        user = User.query.get_or_404(user_id)
        if user.role != UserRole.ADMIN.value:
            return jsonify({'message': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper
