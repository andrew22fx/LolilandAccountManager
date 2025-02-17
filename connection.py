import sqlite3
import os

user_folder = os.environ["USERPROFILE"]
conn = sqlite3.connect(rf"{user_folder}\loliland\LoliAccounts.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT NOT NULL,
               password TEXT NOT NULL
               )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS launcherlink (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               link TEXT NOT NULL
               )
''')