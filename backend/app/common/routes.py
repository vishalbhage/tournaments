from flask import Blueprint, jsonify, send_from_directory, current_app
import os

common_bp = Blueprint('common', __name__)


@common_bp.get('/health')
def health():
    return jsonify({'status': 'ok'})


@common_bp.get('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
