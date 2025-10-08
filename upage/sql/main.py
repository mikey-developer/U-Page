import sqlite3

def dbb(database, command):
    db = sqlite3.connect(database)
    sql = db.cursor()
    sql.execute(command)
    db.commit()

sql = """
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            content TEXT,
            photo TEXT,
            time_is TEXT,
            repost_id TEXT,
            repost_contnet TEXT,
            ifedited TEXT,
            like_paid TEXT
        )
      """

dbb("../db.sqlite3", sql)