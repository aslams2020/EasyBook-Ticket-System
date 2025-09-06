# create_db.py
import sqlite3

def create_database():
    conn = sqlite3.connect('database/movie_ticket.db')
    cursor = conn.cursor()
    
    # Users table with better security
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Movies table with more details
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        duration INTEGER,
        genre TEXT,
        release_date DATE,
        poster_url TEXT,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Showtimes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS showtimes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER NOT NULL,
        showtime DATETIME NOT NULL,
        theater_name TEXT NOT NULL,
        available_seats INTEGER NOT NULL,
        price DECIMAL(5,2) NOT NULL,
        FOREIGN KEY (movie_id) REFERENCES movies (id)
    )
    ''')
    
    # Bookings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        showtime_id INTEGER NOT NULL,
        num_tickets INTEGER NOT NULL,
        total_price DECIMAL(6,2) NOT NULL,
        booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'confirmed',
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (showtime_id) REFERENCES showtimes (id)
    )
    ''')
    
    # Payments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        amount DECIMAL(6,2) NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT DEFAULT 'pending',
        transaction_id TEXT,
        payment_date DATETIME,
        FOREIGN KEY (booking_id) REFERENCES bookings (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database created successfully with improved schema!")

if __name__ == '__main__':
    create_database()