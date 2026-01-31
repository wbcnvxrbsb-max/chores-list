from flask import Blueprint, request, jsonify
import bcrypt
import sys
sys.path.append('..')
from database import query_db, execute_db, get_db

bp = Blueprint('auth', __name__)


def get_pin_hash():
    """Get the stored PIN hash from settings."""
    result = query_db("SELECT value FROM settings WHERE key = 'pin_hash'", one=True)
    return result['value'] if result else None


@bp.route('/pin-exists', methods=['GET'])
def pin_exists():
    """Check if a PIN has been set."""
    return jsonify({'exists': get_pin_hash() is not None})


@bp.route('/verify-pin', methods=['POST'])
def verify_pin():
    """Verify the parent PIN."""
    data = request.get_json()
    pin = data.get('pin', '')

    stored_hash = get_pin_hash()
    if not stored_hash:
        return jsonify({'error': 'No PIN set'}), 400

    if bcrypt.checkpw(pin.encode('utf-8'), stored_hash.encode('utf-8')):
        return jsonify({'valid': True})
    else:
        return jsonify({'valid': False}), 401


@bp.route('/set-pin', methods=['POST'])
def set_pin():
    """Set or change the parent PIN."""
    data = request.get_json()
    new_pin = data.get('pin', '')
    current_pin = data.get('current_pin', '')

    if len(new_pin) < 4:
        return jsonify({'error': 'PIN must be at least 4 digits'}), 400

    stored_hash = get_pin_hash()

    # If PIN already exists, verify current PIN first
    if stored_hash:
        if not current_pin:
            return jsonify({'error': 'Current PIN required'}), 401
        if not bcrypt.checkpw(current_pin.encode('utf-8'), stored_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid current PIN'}), 401

    # Hash the new PIN
    new_hash = bcrypt.hashpw(new_pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Store the new PIN hash
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES ('pin_hash', ?)",
        [new_hash]
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True})
