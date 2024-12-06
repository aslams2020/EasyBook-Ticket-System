import sqlite3

def create_db():
    connection = sqlite3.connect('database/movie_ticket.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    username TEXT NOT NULL,                    
    password TEXT NOT NULL               
    )''')
   
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        available_seats INTEGER NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        UNIQUE(name, date, time)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,    -- This stores the user who made the booking
        movie_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY (movie_id) REFERENCES movies(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL, 
        payment_method TEXT NOT NULL, 
        amount REAL NOT NULL,        
        transaction_date TEXT NOT NULL, 
        status TEXT NOT NULL,         
        FOREIGN KEY(booking_id) REFERENCES bookings(id)
    )
    ''')

    connection.commit()
    connection.close()

if __name__ == '__main__':
    create_db()

print("database tables created successfully..!")