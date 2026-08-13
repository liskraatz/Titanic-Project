import sqlite3
conn = sqlite3.connect('submissions.db')
for row in conn.execute('SELECT * FROM submissions'):
    print(row)
