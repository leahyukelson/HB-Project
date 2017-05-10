from model import Game, connect_to_db, db
from server import app





if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()