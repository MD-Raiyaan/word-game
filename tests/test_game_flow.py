import pytest
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Word, Game, Guess

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })
    with app.app_context():
        db.create_all()
        # Seed words
        w1 = Word(word="PLANT", active=True)
        w2 = Word(word="CRANE", active=True)
        w3 = Word(word="APPLE", active=True)
        db.session.add_all([w1, w2, w3])

        # Seed Admin and Player
        admin = User(username="Admin$User", password_hash=generate_password_hash("Admin1$"), role="ADMIN")
        player = User(username="Player$One", password_hash=generate_password_hash("Pass1$"), role="PLAYER")
        db.session.add_all([admin, player])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login_client(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

def test_rbac_access_control(client):
    # Unauthenticated access (redirects to login)
    res = client.get('/game/', follow_redirects=False)
    assert res.status_code == 302

    res = client.get('/admin/dashboard', follow_redirects=False)
    assert res.status_code == 302

    # Login as Player
    login_client(client, "Player$One", "Pass1$")

    # Player can access /game/
    res = client.get('/game/')
    assert res.status_code == 200

    # Player CANNOT access /admin/dashboard (403 Forbidden)
    res = client.get('/admin/dashboard')
    assert res.status_code == 403

    # Logout & login as Admin
    client.get('/logout')
    login_client(client, "Admin$User", "Admin1$")

    # Admin can access /admin/dashboard
    res = client.get('/admin/dashboard')
    assert res.status_code == 200

    # Admin CANNOT access /game/ (403 Forbidden)
    res = client.get('/game/')
    assert res.status_code == 403

def test_full_game_win_flow(client, app):
    login_client(client, "Player$One", "Pass1$")

    res = client.post('/game/new', follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        game = Game.query.filter_by(status='IN_PROGRESS').first()
        assert game is not None
        target_word = game.word.word

    wrong_guess = "CRANE" if target_word != "CRANE" else "PLANT"
    res = client.post('/game/guess', data={'guess': wrong_guess}, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        game = Game.query.first()
        assert len(game.guesses) == 1
        assert game.guesses[0].guess_word == wrong_guess
        assert game.status == 'IN_PROGRESS'

    res = client.post('/game/guess', data={'guess': target_word}, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        game = Game.query.first()
        assert len(game.guesses) == 2
        assert game.status == 'WON'
        assert game.finished_at is not None

def test_full_game_loss_flow(client, app):
    login_client(client, "Player$One", "Pass1$")
    client.post('/game/new', follow_redirects=True)

    with app.app_context():
        game = Game.query.filter_by(status='IN_PROGRESS').first()
        target_word = game.word.word

    wrong_guess = "CRANE" if target_word != "CRANE" else "PLANT"

    for i in range(1, 6):
        res = client.post('/game/guess', data={'guess': wrong_guess}, follow_redirects=True)
        assert res.status_code == 200

    with app.app_context():
        game = Game.query.first()
        assert len(game.guesses) == 5
        assert game.status == 'LOST'
        assert game.finished_at is not None

def test_guess_history_order(client, app):
    login_client(client, "Player$One", "Pass1$")
    client.post('/game/new', follow_redirects=True)

    # Force target word to APPLE so CRANE/PLANT/STARE are wrong guesses
    with app.app_context():
        game = Game.query.filter_by(status='IN_PROGRESS').first()
        apple_word = Word.query.filter_by(word="APPLE").first()
        game.word_id = apple_word.id
        db.session.commit()

    guesses = ["CRANE", "PLANT", "STARE"]
    for g in guesses:
        client.post('/game/guess', data={'guess': g}, follow_redirects=True)

    with app.app_context():
        game = Game.query.first()
        saved_guesses = [g.guess_word for g in game.guesses]
        assert saved_guesses == guesses
        sequence_numbers = [g.sequence_number for g in game.guesses]
        assert sequence_numbers == [1, 2, 3]
