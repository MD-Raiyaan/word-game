import pytest
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Word, Game

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })
    with app.app_context():
        db.create_all()
        w1 = Word(word="PLANT", active=True)
        player = User(username="Player$One", password_hash=generate_password_hash("Pass1$"), role="PLAYER")
        db.session.add_all([w1, player])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login_player(client):
    return client.post('/login', data={'username': 'Player$One', 'password': 'Pass1$'}, follow_redirects=True)

def test_daily_limit_blocking_and_reset(client, app):
    login_player(client)

    # Complete 3 games today
    for i in range(3):
        res = client.post('/game/new', follow_redirects=True)
        assert res.status_code == 200

        with app.app_context():
            game = Game.query.filter_by(status='IN_PROGRESS').first()
            target = game.word.word

        res = client.post('/game/guess', data={'guess': target}, follow_redirects=True)
        assert res.status_code == 200

    # Attempt 4th game on the same day
    res = client.post('/game/new', follow_redirects=True)
    assert b"daily limit of 3 games" in res.data or b"reached your daily limit" in res.data

    with app.app_context():
        total_games = Game.query.count()
        assert total_games == 3

    # Simulate next calendar day by shifting started_at timestamps of previous games to yesterday
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    with app.app_context():
        for g in Game.query.all():
            g.started_at = yesterday
        db.session.commit()

    # Now starting a game should succeed on the new day
    res = client.post('/game/new', follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        total_games = Game.query.count()
        assert total_games == 4
