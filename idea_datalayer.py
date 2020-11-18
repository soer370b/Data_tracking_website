from flask import g
import sqlite3

class IdeaData():

    def __init__(self):
        self.DATABASE = 'ideahouse.db'

        self._create_db_tables()
        c = self._get_db().cursor()

        c.execute("SELECT * FROM UserProfiles;")
        for u in c:
            print(u)


    def _get_db(self):
        db = g.get('_database', None)
        if db is None:
            db = g._databdase = sqlite3.connect(self.DATABASE)
        return db

    def close_connection(self):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    def get_number_of_ideas(self):
        c = self._get_db().cursor()
        c.execute("SELECT COUNT(rowid) FROM Ideas;")
        val = c.fetchone()
        if val is not None:
            return val[0]
        else:
            return None

    def get_idea_list(self, userid, ideaid = None):
        db = self._get_db()
        c = db.cursor()
        if ideaid is not None:
            c.execute("SELECT idea FROM Ideas WHERE id = ?", ideaid)
            t = c.fetchone()
            print("Idéen er: {}".format(t[0]))
            c.execute("""SELECT Ideas.id, idea, timestamp, UserProfiles.username FROM Ideas JOIN UserProfiles ON Ideas.userid = UserProfiles.id WHERE idea LIKE ?""", (t[0],))
        else:
            c.execute("""SELECT Ideas.id, idea, timestamp, UserProfiles.username FROM Ideas JOIN UserProfiles ON Ideas.userid = UserProfiles.id WHERE userid = ?""",(userid,))
        idea_list = []
        for i in c:
            idea_list.append({'id':i[0], 'text':i[1], 'date':i[2], 'user': i[3]})
        return idea_list


    def register_new_idea(self, idea, id):
        db = self._get_db()
        c = db.cursor()
        c.execute("""INSERT INTO Ideas (idea, userid) VALUES (?, ?);""",(idea, id))
        db.commit()

    def get_idea_count(self, userid):
        c = self._get_db().cursor()
        c.execute("SELECT count(rowid) FROM Ideas WHERE userid == ?;", (userid,))
        n = c.fetchone()
        return n[0]

    def get_user_id(self, s):
        c = self._get_db().cursor()
        c.execute("SELECT id FROM UserProfiles WHERE username = ?", (s,))
        r = c.fetchone()
        #If the user doesn't exist, the result will be None
        if r is not None:
            return r[0]
        else:
            return None

    def register_user(self, user, pw, email):
        db = self._get_db()
        c = db.cursor()
        c.execute("SELECT * from UserProfiles WHERE username = ? OR email = ?", (user,email))
        r = c.fetchone()
        res = False
        if r is not None:
            #The username og email is already in use
            res = False
        else:
            c.execute("INSERT INTO UserProfiles (username, password, email) VALUES (?,?,?)", (user,pw,email))
            db.commit()
            res = True
        return res

    def get_user_list(self):
        l = []
        c = self._get_db().cursor()
        c.execute('SELECT * FROM UserProfiles;')
        for u in c:
            l.append("Navn: {}, email: {}, pw: {}".format(u[1],u[2],u[3]))
        return l

    def login_success(self, user, pw):
        c = self._get_db().cursor()
        c.execute("SELECT password FROM UserProfiles WHERE username = ?", (user,))
        r = c.fetchone()
        if r is not None:
            db_pw = r[0]
        else:
            return False
        return db_pw == pw

    def _create_db_tables(self):
        db = self._get_db()
        #try:
        #    db.execute("DROP TABLE IF EXISTS Ideas;")
        #    db.commit()
        #except:
        #    print('Fejl ved sletning af tabeller.')
        c = db.cursor()
        try:
            c.execute("""CREATE TABLE UserProfiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT,
                password TEXT);""")
        except Exception as e:
            print(e)

        try:
            c.execute("""CREATE TABLE Ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid INTEGER,
                idea TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);""")
        except Exception as e:
            print(e)

        db.commit()
        return 'Database tables created'
#Funktion som laver string om til en datatype 
    def tryeval(val):
      try:
        val = ast.literal_eval(val)
      except ValueError:
        pass
      return val
