import sqlite3

def add_movie(name, price, available_seats, date, time):
    connection = sqlite3.connect('database/movie_ticket.db')
    cursor = connection.cursor()

    cursor.execute('''
    SELECT COUNT(*) FROM movies WHERE name = ? AND date = ? AND time = ?
    ''', (name, date, time))

    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO movies (name, price, available_seats, date, time)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, price, available_seats, date, time))

        connection.commit()
    

    connection.close()

add_movie("The Lunchbox", 150, 50, "2024-11-22", "07:30")
add_movie("Avengers: Endgame", 250, 50, "2024-11-23", "09:00")
add_movie("3 Idiots",350, 100, "2024-11-24", "12:00")
add_movie("Harry Potter", 120, 50, "2024-11-25", "16:30")
add_movie("The Pursuit of Happiness", 175, 50, "2024-11-26", "17:00")
add_movie("Sita Ramam", 100, 30, "2024-11-27", "18:00")
add_movie("12th Fail", 180, 20, "2024-11-28", "19:30")
add_movie("Drishyam", 280, 35, "2024-11-29", "20:00")
add_movie("Titanic", 230, 40, "2024-11-30", "18:00")

print('Finished adding movies!')
