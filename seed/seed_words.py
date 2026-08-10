import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Word

SEED_WORDS = [
    "PLANT", "CRANE", "SLATE", "APPLE", "PAPER",
    "STARE", "GEESE", "HOUSE", "LIGHT", "BRAIN",
    "SMART", "FLASH", "CLOUD", "STORM", "TIGER",
    "OCEAN", "MUSIC", "DREAM", "FLAME", "GIANT"
]

def seed_words():
    app = create_app()
    with app.app_context():
        db.create_all()
        added = 0
        for w in SEED_WORDS:
            w_upper = w.strip().upper()
            existing = Word.query.filter_by(word=w_upper).first()
            if not existing:
                word_obj = Word(word=w_upper, active=True)
                db.session.add(word_obj)
                added += 1
        db.session.commit()
        print(f"Seeding completed. Added {added} new words. Total words in DB: {Word.query.count()}")

if __name__ == "__main__":
    seed_words()
