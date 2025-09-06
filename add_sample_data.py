# add_sample_data.py (Updated)
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def add_sample_data():
    conn = sqlite3.connect('database/movie_ticket.db')
    cursor = conn.cursor()
    
    # Add admin user
    cursor.execute(
        'INSERT OR IGNORE INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
        ('admin', 'admin@easybook.com', generate_password_hash('admin123'), 1)
    )
    
    # Add regular user
    cursor.execute(
        'INSERT OR IGNORE INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
        ('user', 'user@example.com', generate_password_hash('user123'), 0)
    )
    
    # Add sample movies
    movies = [
        ('Inception', 'A thief who steals corporate secrets through dream-sharing technology.', 148, 'Sci-Fi/Thriller', '2010-07-16', 'https://source.unsplash.com/random/300x450/?inception'),
        ('The Dark Knight', 'Batman sets out to dismantle the remaining criminal organizations that plague the streets.', 152, 'Action/Crime', '2008-07-18', 'https://source.unsplash.com/random/300x450/?batman'),
        ('Interstellar', 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.', 169, 'Sci-Fi/Adventure', '2014-11-07', 'https://source.unsplash.com/random/300x450/?space'),
        ('The Shawshank Redemption', 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 142, 'Drama', '1994-09-23', 'https://source.unsplash.com/random/300x450/?prison'),
        ('Pulp Fiction', 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.', 154, 'Crime/Drama', '1994-10-14', 'https://source.unsplash.com/random/300x450/?pulp')
    ]
    
    cursor.executemany(
        'INSERT INTO movies (title, description, duration, genre, release_date, poster_url) VALUES (?, ?, ?, ?, ?, ?)',
        movies
    )
    
    # Add sample showtimes
    movie_ids = cursor.execute('SELECT id FROM movies').fetchall()
    showtimes = []
    
    for movie_id in movie_ids:
        movie_id = movie_id[0]
        base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        for day in range(7):  # Next 7 days
            for show_num in range(4):  # 4 shows per day
                showtime = base_time + timedelta(days=day, hours=show_num*3)
                theater = "Theater " + str((movie_id % 3) + 1)
                price = 12.50 + (movie_id * 0.50)  # Varying prices
                
                showtimes.append((
                    movie_id,
                    showtime.strftime('%Y-%m-%d %H:%M:%S'),
                    theater,
                    100,  # Available seats
                    price
                ))
    
    cursor.executemany(
        'INSERT INTO showtimes (movie_id, showtime, theater_name, available_seats, price) VALUES (?, ?, ?, ?, ?)',
        showtimes
    )
    
    conn.commit()
    conn.close()
    print("Sample data added successfully!")

if __name__ == '__main__':
    add_sample_data()