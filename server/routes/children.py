from flask import Blueprint, request, jsonify
import sys
sys.path.append('..')
from database import query_db, execute_db, get_db

bp = Blueprint('children', __name__)


@bp.route('', methods=['GET'])
def list_children():
    """Get all children."""
    children = query_db(
        "SELECT id, name, display_order, created_at FROM children ORDER BY display_order, id"
    )
    return jsonify([dict(c) for c in children])


@bp.route('', methods=['POST'])
def create_child():
    """Create a new child."""
    data = request.get_json()
    name = data.get('name', '').strip()

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    # Get max display_order
    max_order = query_db("SELECT MAX(display_order) as max_ord FROM children", one=True)
    new_order = (max_order['max_ord'] or 0) + 1

    child_id = execute_db(
        "INSERT INTO children (name, display_order) VALUES (?, ?)",
        [name, new_order]
    )

    child = query_db("SELECT * FROM children WHERE id = ?", [child_id], one=True)
    return jsonify(dict(child)), 201


@bp.route('/<int:child_id>', methods=['GET'])
def get_child(child_id):
    """Get a single child."""
    child = query_db("SELECT * FROM children WHERE id = ?", [child_id], one=True)
    if not child:
        return jsonify({'error': 'Child not found'}), 404
    return jsonify(dict(child))


@bp.route('/<int:child_id>', methods=['PUT'])
def update_child(child_id):
    """Update a child."""
    data = request.get_json()

    child = query_db("SELECT * FROM children WHERE id = ?", [child_id], one=True)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    name = data.get('name', child['name']).strip()
    display_order = data.get('display_order', child['display_order'])

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    execute_db(
        "UPDATE children SET name = ?, display_order = ? WHERE id = ?",
        [name, display_order, child_id]
    )

    child = query_db("SELECT * FROM children WHERE id = ?", [child_id], one=True)
    return jsonify(dict(child))


@bp.route('/<int:child_id>', methods=['DELETE'])
def delete_child(child_id):
    """Delete a child and all their chores."""
    child = query_db("SELECT * FROM children WHERE id = ?", [child_id], one=True)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    execute_db("DELETE FROM children WHERE id = ?", [child_id])
    return jsonify({'success': True})
