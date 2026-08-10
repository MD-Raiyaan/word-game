import random
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app import db
from app.models import Game, Guess, Word
from app.scoring import score_guess
from app.decorators import player_required

game_bp = Blueprint('game', __name__, url_prefix='/game')

def get_today_games_count(user_id):
    today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    all_user_games = Game.query.filter_by(user_id=user_id).all()
    count = sum(1 for g in all_user_games if g.started_at.strftime('%Y-%m-%d') == today_str)
    return count

@game_bp.route('/', methods=['GET'])
@player_required
def index():
    # Find active game in progress
    active_game = Game.query.filter_by(user_id=current_user.id, status='IN_PROGRESS').order_by(Game.started_at.desc()).first()

    today_count = get_today_games_count(current_user.id)
    daily_limit_reached = today_count >= 3 and not active_game

    guesses_formatted = []
    if active_game:
        for g in active_game.guesses:
            guesses_formatted.append({
                'word': g.guess_word,
                'results': g.result_pattern.split(','),
                'sequence': g.sequence_number
            })

    # If game just finished or last game finished
    last_finished_game = None
    if not active_game:
        last_finished_game = Game.query.filter(
            Game.user_id == current_user.id,
            Game.status.in_(['WON', 'LOST'])
        ).order_by(Game.finished_at.desc()).first()
        if last_finished_game:
            for g in last_finished_game.guesses:
                guesses_formatted.append({
                    'word': g.guess_word,
                    'results': g.result_pattern.split(','),
                    'sequence': g.sequence_number
                })

    return render_template(
        'game.html',
        game=active_game,
        last_game=last_finished_game,
        guesses=guesses_formatted,
        today_count=today_count,
        daily_limit_reached=daily_limit_reached
    )

@game_bp.route('/new', methods=['POST'])
@player_required
def new_game():
    # Check if active game exists
    active_game = Game.query.filter_by(user_id=current_user.id, status='IN_PROGRESS').first()
    if active_game:
        return redirect(url_for('game.index'))

    # Check daily limit
    today_count = get_today_games_count(current_user.id)
    if today_count >= 3:
        flash("You've reached your daily limit of 3 games. Come back tomorrow.", "danger")
        return redirect(url_for('game.index'))

    # Pick random active word
    words = Word.query.filter_by(active=True).all()
    if not words:
        flash("No word bank available. Contact administrator.", "danger")
        return redirect(url_for('game.index'))

    selected_word = random.choice(words)

    game = Game(
        user_id=current_user.id,
        word_id=selected_word.id,
        status='IN_PROGRESS',
        started_at=datetime.now(timezone.utc)
    )
    db.session.add(game)
    db.session.commit()

    return redirect(url_for('game.index'))

@game_bp.route('/guess', methods=['POST'])
@player_required
def submit_guess():
    game = Game.query.filter_by(user_id=current_user.id, status='IN_PROGRESS').first()
    if not game:
        flash("No active game found. Please start a new game.", "warning")
        return redirect(url_for('game.index'))

    guess_raw = request.form.get('guess', '').strip().upper()

    # Validate guess
    if len(guess_raw) != 5 or not guess_raw.isalpha():
        flash("Invalid guess. Guess must be a 5-letter word containing only letters.", "danger")
        return redirect(url_for('game.index'))

    current_sequence = len(game.guesses) + 1
    if current_sequence > 5:
        flash("Game already reached maximum guess limit.", "warning")
        return redirect(url_for('game.index'))

    # Calculate score pattern
    score_list = score_guess(game.word.word, guess_raw)
    result_pattern = ','.join(score_list)

    guess_obj = Guess(
        game_id=game.id,
        guess_word=guess_raw,
        sequence_number=current_sequence,
        result_pattern=result_pattern,
        guessed_at=datetime.now(timezone.utc)
    )
    db.session.add(guess_obj)

    # Check status
    if guess_raw == game.word.word:
        game.status = 'WON'
        game.finished_at = datetime.now(timezone.utc)
        flash("CONGRATULATIONS! You guessed the word correctly!", "game_won")
    elif current_sequence == 5:
        game.status = 'LOST'
        game.finished_at = datetime.now(timezone.utc)
        flash(f"Better luck next time. The correct word was '{game.word.word}'.", "game_lost")

    db.session.commit()
    return redirect(url_for('game.index'))
