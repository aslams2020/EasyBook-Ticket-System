# debug_users.py
import sqlite3

def check_users():
    conn = sqlite3.connect('database/movie_ticket.db')
    cursor = conn.cursor()
    
    print("=== Users Table Contents ===")
    users = cursor.execute('SELECT id, username, email, is_admin FROM users').fetchall()
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Admin: {bool(user[3])}")
    
    print("\n=== Counts ===")
    total_users = cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    regular_users = cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0').fetchone()[0]
    admin_users = cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1').fetchone()[0]
    
    print(f"Total Users: {total_users}")
    print(f"Regular Users (is_admin=0): {regular_users}")
    print(f"Admin Users (is_admin=1): {admin_users}")
    
    conn.close()

if __name__ == '__main__':
    check_users()