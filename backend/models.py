from db import get_postgres_connection, return_postgres_connection

class User:
    def __init__(self, id=None, username=None, password=None):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def create_user(username, password):
        conn = get_postgres_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password) 
                VALUES (%s, %s) RETURNING id;
            """, (username, password))
            user_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            return User(id=user_id, username=username, password=password)
        except Exception as e:
            conn.rollback()
            print(f"Error creating user: {e}")
            return None
        finally:
            return_postgres_connection(conn)

    @staticmethod
    def get_user_by_username(username):
        # retrieve a user from the database by username
        conn = get_postgres_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password 
                FROM users WHERE username = %s;
            """, (username,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return User(id=row[0], username=row[1], password=row[2])
            return None
        except Exception as e:
            print(f"Error fetching user by username: {e}")
            return None
        finally:
            return_postgres_connection(conn)

    @staticmethod
    def get_user_by_id(user_id):
#   etrieve a user from the database by id

        conn = get_postgres_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password 
                FROM users WHERE id = %s;
            """, (user_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return User(id=row[0], username=row[1], password=row[2])
            return None
        except Exception as e:
            print(f"Error fetching user by ID: {e}")
            return None
        finally:
            return_postgres_connection(conn)

    @staticmethod
    def update_password(user_id, new_password):
# update password for user
        conn = get_postgres_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET password = %s 
                WHERE id = %s;
            """, (new_password, user_id))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error updating password: {e}")
            return False
        finally:
            return_postgres_connection(conn)

    @staticmethod
    def delete_user(user_id):
#  delete a user from the database by id

        conn = get_postgres_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM users WHERE id = %s;
            """, (user_id,))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error deleting user: {e}")
            return False
        finally:
            return_postgres_connection(conn)
