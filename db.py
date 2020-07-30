import sqlite3


class Database():
    def __init__(self):
        # define connection and cursor
        self.conn = sqlite3.connect('News.db')
        self.c = self.conn.cursor()
        # create table

    def create_table(self):
        try:
            self.c.execute('''CREATE TABLE NEWS
                        ([generated_id] INTEGER PRIMARY KEY, [JobId] integer , [Data] text)''')
        except:
            pass

    def AddToDb(self, job_id, news_data):
        self.c.execute("INSERT INTO NEWS VALUES (" +
                       job_id + ","+news_data+")")
        self.conn.commit()

    def GetOne_By_JobId(self, job_id):
        self.c.execute("SELECT Data from NEWS where JobId ="+job_id)
        rows = self.c.fetchall()
        return rows

    def close(self):
        if self.conn:
            self.conn.commit()
            self.c.close()
            self.conn.close()
