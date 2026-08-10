from datetime import datetime, timezone
from flask import Blueprint, render_template, request
from flask_login import current_user
from app import db
from app.models import User, Game
from app.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.filter_by(role='PLAYER').count()
    total_games = Game.query.count()
    return render_template('admin_dashboard.html', total_users=total_users, total_games=total_games)

@admin_bp.route('/reports/daily')
@admin_required
def daily_report():
    selected_date_str = request.args.get('date', datetime.now(timezone.utc).strftime('%Y-%m-%d'))
 
    try:
        datetime.strptime(selected_date_str, '%Y-%m-%d')
    except ValueError:
        selected_date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    all_games = Game.query.all()

    # Filter games started on selected date
    games_started_on_date = [
        g for g in all_games
        if g.started_at.strftime('%Y-%m-%d') == selected_date_str
    ]

    distinct_user_ids = {g.user_id for g in games_started_on_date}
    distinct_users_count = len(distinct_user_ids)

    # Filter games won on selected date
    games_won_on_date = [
        g for g in all_games
        if g.status == 'WON' and g.finished_at and g.finished_at.strftime('%Y-%m-%d') == selected_date_str
    ]
    correct_guesses_count = len(games_won_on_date)

    return render_template(
        'admin_daily_report.html',
        selected_date=selected_date_str,
        distinct_users_count=distinct_users_count,
        correct_guesses_count=correct_guesses_count,
        games_started_count=len(games_started_on_date)
    )

@admin_bp.route('/reports/user')
@admin_required
def user_report():
    players = User.query.filter_by(role='PLAYER').order_by(User.username.asc()).all()
    selected_user_id = request.args.get('user_id', type=int)

    selected_user = None
    report_rows = []

    if selected_user_id:
        selected_user = db.session.get(User, selected_user_id)

    if not selected_user and players:
        selected_user = players[0]

    if selected_user:
        user_games = Game.query.filter_by(user_id=selected_user.id).all()

        date_stats = {}
        for game in user_games:
            date_key = game.started_at.strftime('%Y-%m-%d')
            if date_key not in date_stats:
                date_stats[date_key] = {'date': date_key, 'words_tried': 0, 'correct_guesses': 0}
            date_stats[date_key]['words_tried'] += 1
            if game.status == 'WON' and game.finished_at and game.finished_at.strftime('%Y-%m-%d') == date_key:
                date_stats[date_key]['correct_guesses'] += 1

        report_rows = sorted(date_stats.values(), key=lambda x: x['date'], reverse=True)

    return render_template(
        'admin_user_report.html',
        players=players,
        selected_user=selected_user,
        report_rows=report_rows
    )
