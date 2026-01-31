from flask import Blueprint, request, jsonify
from datetime import date, timedelta
import sys
sys.path.append('..')
from database import query_db

bp = Blueprint('history', __name__)


@bp.route('', methods=['GET'])
def get_history():
    """Get chore completion history."""
    days = request.args.get('days', 7, type=int)
    child_id = request.args.get('child_id', type=int)

    # Limit to reasonable range
    days = min(max(days, 1), 365)

    start_date = (date.today() - timedelta(days=days-1)).isoformat()
    end_date = date.today().isoformat()

    # Build query based on whether filtering by child
    if child_id:
        completions = query_db("""
            SELECT
                cc.date,
                cc.completed_at,
                c.id as chore_id,
                c.title as chore_title,
                ch.id as child_id,
                ch.name as child_name
            FROM chore_completions cc
            JOIN chores c ON cc.chore_id = c.id
            JOIN children ch ON c.child_id = ch.id
            WHERE cc.date >= ? AND cc.date <= ?
                AND ch.id = ?
            ORDER BY cc.date DESC, ch.name, cc.completed_at
        """, [start_date, end_date, child_id])
    else:
        completions = query_db("""
            SELECT
                cc.date,
                cc.completed_at,
                c.id as chore_id,
                c.title as chore_title,
                ch.id as child_id,
                ch.name as child_name
            FROM chore_completions cc
            JOIN chores c ON cc.chore_id = c.id
            JOIN children ch ON c.child_id = ch.id
            WHERE cc.date >= ? AND cc.date <= ?
            ORDER BY cc.date DESC, ch.name, cc.completed_at
        """, [start_date, end_date])

    # Group by date and child
    history = {}
    for comp in completions:
        d = comp['date']
        if d not in history:
            history[d] = {}

        child_name = comp['child_name']
        if child_name not in history[d]:
            history[d][child_name] = {
                'child_id': comp['child_id'],
                'chores': []
            }

        history[d][child_name]['chores'].append({
            'chore_id': comp['chore_id'],
            'title': comp['chore_title'],
            'completed_at': comp['completed_at']
        })

    # Convert to list format
    result = []
    for d in sorted(history.keys(), reverse=True):
        day_data = {
            'date': d,
            'children': []
        }
        for child_name, child_data in sorted(history[d].items()):
            day_data['children'].append({
                'id': child_data['child_id'],
                'name': child_name,
                'chores': child_data['chores']
            })
        result.append(day_data)

    return jsonify({'history': result})


@bp.route('/child/<int:child_id>', methods=['GET'])
def get_child_history(child_id):
    """Get history for a specific child."""
    days = request.args.get('days', 30, type=int)
    days = min(max(days, 1), 365)

    start_date = (date.today() - timedelta(days=days-1)).isoformat()
    end_date = date.today().isoformat()

    completions = query_db("""
        SELECT
            cc.date,
            cc.completed_at,
            c.id as chore_id,
            c.title as chore_title
        FROM chore_completions cc
        JOIN chores c ON cc.chore_id = c.id
        WHERE c.child_id = ?
            AND cc.date >= ? AND cc.date <= ?
        ORDER BY cc.date DESC, cc.completed_at
    """, [child_id, start_date, end_date])

    # Group by date
    history = {}
    for comp in completions:
        d = comp['date']
        if d not in history:
            history[d] = []
        history[d].append({
            'chore_id': comp['chore_id'],
            'title': comp['chore_title'],
            'completed_at': comp['completed_at']
        })

    result = [
        {'date': d, 'chores': chores}
        for d, chores in sorted(history.items(), reverse=True)
    ]

    return jsonify({'history': result})
