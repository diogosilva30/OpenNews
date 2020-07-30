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
                        ([generated_id] INTEGER PRIMARY KEY , [Data] text)''')
        except:
            pass

    def AddToDb(self, news_data):
        self.c.execute("INSERT INTO NEWS VALUES (" +
                       news_data + ")")
        self.conn.commit()

    def GetOne_By_Data(self, Data):
        self.c.execute("SELECT Data from NEWS where Data ="+Data)
        rows = self.c.fetchall()
        return rows

    def close(self):
        if self.conn:
            self.conn.commit()
            self.c.close()
            self.conn.close()
