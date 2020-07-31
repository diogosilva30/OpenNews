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
        if not isinstance(news_data, str):
            raise ValueError('Inappropriate type: {} for news_dta whereas a str \
            is expected'.format(type(news_data)))

        q = "INSERT INTO NEWS (Data) VALUES (?)"
        self.c.execute(q, (news_data,))
        self.conn.commit()
        print("New row sucessfuly added to the database!")

    def GetOne_By_Data(self, Data):
        print("Getting one item from database...")
        print(Data)
        self.c.execute("SELECT Data from NEWS where Data ="+Data)
        rows = self.c.fetchall()
        print("retrived from db:" + rows)
        return rows

    def close(self):
        if self.conn:
            self.conn.commit()
            self.c.close()
            self.conn.close()
