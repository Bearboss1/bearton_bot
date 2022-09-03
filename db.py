import sqlite3
import random


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, referrer_id=None):
        with self.connection:
            if referrer_id is not None:
                return self.cursor.execute("INSERT INTO users (user_id, referrer_id) VALUES (?,?)",
                                           (user_id, referrer_id,))
            else:
                return self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))

    def delete_user(self, user_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM users WHERE user_id=(?)", (user_id,))

    def count_referrals(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT COUNT (id) as count FROM users WHERE referrer_id = ?",
                                       (user_id,)).fetchone()[0]

    def get_users(self):
        with self.connection:
            users = self.cursor.execute("SELECT user_id FROM users")
            users_list = [users[0] for users in users.fetchall()]

            return users_list
