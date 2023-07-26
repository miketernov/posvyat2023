import sqlite3
from bot_const import *


# conn = sqlite3.connect(path)
# cursor = conn.cursor()
# cursor.execute("""CREATE TABLE IF NOT EXISTS users(
#    userid INT PRIMARY KEY,
#    username INT);
# """)
# conn.commit()
# cursor.close()
# conn.close()


def add_user(userid, username):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    val = (userid, username)
    cursor.execute("INSERT INTO users VALUES (?, ?)", val)
    conn.commit()
    cursor.close()
    conn.close()


def delete_user(userid):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    val = userid
    cursor.execute("delete from users where userid = ?", (val,))
    conn.commit()
    cursor.close()
    conn.close()


def check_if_user(userid):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    val = userid
    cursor.execute("select count (*) from users where userid = ?", (val,))
    for i in cursor:
        k = i[0]
    cursor.close()
    conn.close()
    return k


def get_username(userid):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    val = userid
    cursor.execute("select username from users where userid = ?", (val,))
    for i in cursor:
        k = i[0]
    cursor.close()
    conn.close()
    return k
