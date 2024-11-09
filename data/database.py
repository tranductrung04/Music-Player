from flet import *
import sqlite3

class DataBase:
    def CreateDatabase():
        try:
            db = sqlite3.connect('assets/storage/song.db')
            c = db.cursor()
            c.execute("""CREATE TABLE songs(
                audio_path text,
                thumbnail text,
                title text, 
                artist text,
                duration text,
                lyrics text
            ) """)
            db.close()
        except Exception as e:
            print(e)

    def ConectToDatabase():
        try:
            db = sqlite3.connect('assets/storage/song.db')
            c = db.cursor()
            return db
        except Exception as e:
            print(e)

    def ReadDatabase(db):
        c = db.cursor()
        c.execute("SELECT * FROM songs")
        items = c.fetchall()
        return items

    def UpdateDatabase(db, value):
        pass
    
    def InsertDatabase(db, values):
        flag =  True
        c = db.cursor()
        c.execute("SELECT * FROM songs")
        items = c.fetchall()
        for item in items:
            if item[1] == values[1]: flag = False
        if flag:
            c.execute("INSERT INTO songs VALUES (?, ?, ?, ?, ?, ?)", values)
            db.commit()

    def DeleteDatabase(db, value):
        c = db.cursor()
        c.execute("DELETE FROM songs WHERE thumbnail = ?", value)
        db.commit()
        
