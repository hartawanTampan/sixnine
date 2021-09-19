import sqlite3 as sql3

conn = sql3.connect("chat.db")
cur = conn.cursor()

try:
    cur.execute("""CREATE TABLE fsub_chat
               (chat_id integer, channel_id integer, user_id integer)""")
except sql3.OperationalError:
    pass


def add_chat(chat_id, channel_id):
    cur.execute(f"INSERT INTO fsub_chat VALUES ({chat_id}, {channel_id}, 1)")
    conn.commit()


def insert_user(chat_id, channel_id, user_id):
    cur.execute(f"INSERT INTO fsub_chat VALUES ({chat_id}, {channel_id}, {user_id})")
    conn.commit()


def disable_chat(chat_id):
    cur.execute(f"DELETE FROM fsub_chat WHERE chat_id = {chat_id}")
    conn.commit()


def remove_user(user_id):
    cur.execute(f"DELETE FROM fsub_chat WHERE user_id = {user_id}")
