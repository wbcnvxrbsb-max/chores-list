from flask import Blueprint, request, jsonify
from datetime import date, datetime, timedelta
import calendar
import sys
sys.path.append('..')
from database import query_db, execute_db, get_db

bp = Blueprint('chores', __name__)


def get_period_start(frequency):
    """Get the start date for the current period based on frequency."""
    today = date.today()

    if frequency == 'daily' or frequency == 'oneoff':
        return today.isoformat()

    elif frequency == 'weekly':
        # Monday of current week (week starts Monday)
        # If today is Sunday, we want this week's Monday
        days_since_monday = today.weekday()  # Monday=0, Sunday=6
        monday = today - timedelta(days=days_since_monday)
        return monday.isoformat()

    elif frequency == 'monthly':
        # First day of current month
        return date(today.year, today.month, 1).isoformat()

    return today.isoformat()


def cleanup_expired_oneoff_chores():
    """Deactivate one-off chores that were completed before today."""
    today = date.today().isoformat()

    # Find one-off chores that have completions before today
    # and deactivate them
    execute_db("""
        UPDATE chores
        SET is_active = 0
        WHERE frequency = 'oneoff'
          AND is_active = 1
          AND id IN (
              SELECT DISTINCT chore_id
              FROM chore_completions
              WHERE date < ?
          )
    """, [today])

    # Also deactivate one-off chores created before today that were never completed
    # (they should only be visible on their creation day)
    execute_db("""
        UPDATE chores
        SET is_active = 0
        WHERE frequency = 'oneoff'
          AND is_active = 1
          AND DATE(created_at) < ?
          AND id NOT IN (
              SELECT DISTINCT chore_id
              FROM chore_completions
              WHERE date = DATE(chores.created_at)
          )
    """, [today])


@bp.route('/children/<int:child_id>/chores', methods=['GET'])
def get_chores_for_child(child_id):
    """Get all chores for a child with completion status based on frequency."""
    # Clean up expired one-off chores first
    cleanup_expired_oneoff_chores()

    today = date.today()
    today_str = today.isoformat()

    # Get period starts for each frequency
    daily_start = today_str
    weekly_start = get_period_start('weekly')
    monthly_start = get_period_start('monthly')

    # Query all active chores with completion status based on frequency
    chores = query_db("""
        SELECT
            c.id,
            c.title,
            c.frequency,
            c.display_order,
            c.created_at,
            CASE
                WHEN c.frequency = 'daily' OR c.frequency = 'oneoff' THEN
                    (SELECT id FROM chore_completions WHERE chore_id = c.id AND date = ?)
                WHEN c.frequency = 'weekly' THEN
                    (SELECT id FROM chore_completions WHERE chore_id = c.id AND date >= ?)
                WHEN c.frequency = 'monthly' THEN
                    (SELECT id FROM chore_completions WHERE chore_id = c.id AND date >= ?)
                ELSE NULL
            END as completion_id,
            CASE
                WHEN c.frequency = 'daily' OR c.frequency = 'oneoff' THEN
                    (SELECT completed_at FROM chore_completions WHERE chore_id = c.id AND date = ?)
                WHEN c.frequency = 'weekly' THEN
                    (SELECT completed_at FROM chore_completions WHERE chore_id = c.id AND date >= ? ORDER BY date DESC LIMIT 1)
                WHEN c.frequency = 'monthly' THEN
                    (SELECT completed_at FROM chore_completions WHERE chore_id = c.id AND date >= ? ORDER BY date DESC LIMIT 1)
                ELSE NULL
            END as completed_at
        FROM chores c
        WHERE c.child_id = ?
            AND c.is_active = 1
        ORDER BY
            CASE c.frequency
                WHEN 'daily' THEN 1
                WHEN 'weekly' THEN 2
                WHEN 'monthly' THEN 3
                WHEN 'oneoff' THEN 4
                ELSE 5
            END,
            c.display_order,
            c.id
    """, [daily_start, weekly_start, monthly_start, daily_start, weekly_start, monthly_start, child_id])

    return jsonify([{
        'id': c['id'],
        'title': c['title'],
        'frequency': c['frequency'] or 'daily',
        'display_order': c['display_order'],
        'completed': c['completion_id'] is not None,
        'completed_at': c['completed_at']
    } for c in chores])


@bp.route('/children/<int:child_id>/chores', methods=['POST'])
def create_chore(child_id):
    """Create a new chore for a child."""
    # Verify child exists
    child = query_db("SELECT id FROM children WHERE id = ?", [child_id], one=True)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    data = request.get_json()
    title = data.get('title', '').strip()
    frequency = data.get('frequency', 'daily')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    # Validate frequency
    valid_frequencies = ['daily', 'weekly', 'monthly', 'oneoff']
    if frequency not in valid_frequencies:
        return jsonify({'error': f'Invalid frequency. Must be one of: {", ".join(valid_frequencies)}'}), 400

    # Get max display_order for this child and frequency
    max_order = query_db(
        "SELECT MAX(display_order) as max_ord FROM chores WHERE child_id = ? AND frequency = ?",
        [child_id, frequency], one=True
    )
    new_order = (max_order['max_ord'] or 0) + 1

    chore_id = execute_db(
        "INSERT INTO chores (child_id, title, frequency, display_order) VALUES (?, ?, ?, ?)",
        [child_id, title, frequency, new_order]
    )

    chore = query_db("SELECT * FROM chores WHERE id = ?", [chore_id], one=True)
    return jsonify(dict(chore)), 201


@bp.route('/chores/<int:chore_id>', methods=['PUT'])
def update_chore(chore_id):
    """Update a chore."""
    chore = query_db("SELECT * FROM chores WHERE id = ?", [chore_id], one=True)
    if not chore:
        return jsonify({'error': 'Chore not found'}), 404

    data = request.get_json()
    title = data.get('title', chore['title']).strip()
    frequency = data.get('frequency', chore['frequency'])
    display_order = data.get('display_order', chore['display_order'])

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    # Validate frequency
    valid_frequencies = ['daily', 'weekly', 'monthly', 'oneoff']
    if frequency not in valid_frequencies:
        return jsonify({'error': f'Invalid frequency. Must be one of: {", ".join(valid_frequencies)}'}), 400

    execute_db(
        "UPDATE chores SET title = ?, frequency = ?, display_order = ? WHERE id = ?",
        [title, frequency, display_order, chore_id]
    )

    chore = query_db("SELECT * FROM chores WHERE id = ?", [chore_id], one=True)
    return jsonify(dict(chore))


@bp.route('/chores/<int:chore_id>', methods=['DELETE'])
def delete_chore(chore_id):
    """Soft delete a chore (keeps history)."""
    chore = query_db("SELECT * FROM chores WHERE id = ?", [chore_id], one=True)
    if not chore:
        return jsonify({'error': 'Chore not found'}), 404

    execute_db("UPDATE chores SET is_active = 0 WHERE id = ?", [chore_id])
    return jsonify({'success': True})


@bp.route('/chores/<int:chore_id>/complete', methods=['POST'])
def complete_chore(chore_id):
    """Mark a chore as completed for the current period."""
    chore = query_db("SELECT * FROM chores WHERE id = ? AND is_active = 1", [chore_id], one=True)
    if not chore:
        return jsonify({'error': 'Chore not found'}), 404

    today = date.today().isoformat()
    frequency = chore['frequency'] or 'daily'
    period_start = get_period_start(frequency)

    # Check if already completed in this period
    if frequency in ['daily', 'oneoff']:
        existing = query_db(
            "SELECT * FROM chore_completions WHERE chore_id = ? AND date = ?",
            [chore_id, today], one=True
        )
    else:
        existing = query_db(
            "SELECT * FROM chore_completions WHERE chore_id = ? AND date >= ?",
            [chore_id, period_start], one=True
        )

    if existing:
        return jsonify({
            'success': True,
            'completed_at': existing['completed_at'],
            'already_completed': True
        })

    # Insert completion record with today's date
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO chore_completions (chore_id, date) VALUES (?, ?)",
        [chore_id, today]
    )
    conn.commit()

    completion = query_db(
        "SELECT completed_at FROM chore_completions WHERE id = ?",
        [cur.lastrowid], one=True
    )
    conn.close()

    return jsonify({
        'success': True,
        'completed_at': completion['completed_at']
    })


@bp.route('/chores/<int:chore_id>/complete', methods=['DELETE'])
def uncomplete_chore(chore_id):
    """Unmark a chore as completed for current period (parent only)."""
    chore = query_db("SELECT * FROM chores WHERE id = ?", [chore_id], one=True)
    if not chore:
        return jsonify({'error': 'Chore not found'}), 404

    frequency = chore['frequency'] or 'daily'
    period_start = get_period_start(frequency)

    if frequency in ['daily', 'oneoff']:
        execute_db(
            "DELETE FROM chore_completions WHERE chore_id = ? AND date = ?",
            [chore_id, date.today().isoformat()]
        )
    else:
        execute_db(
            "DELETE FROM chore_completions WHERE chore_id = ? AND date >= ?",
            [chore_id, period_start]
        )

    return jsonify({'success': True})
