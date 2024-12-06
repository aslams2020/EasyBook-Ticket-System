from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint,jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from checkout import checkout_blueprint

app = Flask(__name__)
app.register_blueprint(checkout_blueprint, url_prefix='/checkout')
app.secret_key = 'your_secret_key'

def get_user_by_username(username):
    connection = sqlite3.connect('database/movie_ticket.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()
    connection.close()
    return user

def get_movies():
    connection = sqlite3.connect('database/movie_ticket.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM movies')
    movies = cursor.fetchall()
    connection.close()
    return movies

def get_movie_by_id(movie_id):
    connection = sqlite3.connect('database/movie_ticket.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM movies WHERE id=?', (movie_id,))
    movie = cursor.fetchone()
    connection.close()
    return movie

def add_booking(user_id, movie_id, quantity, total):
    connection = sqlite3.connect('database/movie_ticket.db')
    cursor = connection.cursor()

    # already booked the movie
    cursor.execute('''
        SELECT quantity, total FROM bookings 
        WHERE user_id = ? AND movie_id = ?
    ''', (user_id, movie_id))

    existing_booking = cursor.fetchone()

    if existing_booking:
        # If existing, update the quantity and total
        existing_quantity, existing_total = existing_booking
        new_quantity = existing_quantity + quantity
        new_total = existing_total + total

        cursor.execute('''
            UPDATE bookings 
            SET quantity = ?, total = ? 
            WHERE user_id = ? AND movie_id = ?
        ''', (new_quantity, new_total, user_id, movie_id))

    else:
        # insert a new one
        cursor.execute('''
            INSERT INTO bookings (user_id, movie_id, quantity, total)
            VALUES (?, ?, ?, ?)
        ''', (user_id, movie_id, quantity, total))

    connection.commit()
    connection.close()



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # hashed_password = generate_password_hash(password)

        connection = sqlite3.connect('database/movie_ticket.db')
        cursor = connection.cursor()

        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            connection.commit()
            connection.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists!')
            connection.close()
            return render_template('register.html')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)

        # Compare the stored password with the input password
        if user and user[2] == password:
            session['user_id'] = user[0]
            return redirect(url_for('movies'))
        else:
            flash('Invalid credentials!')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/booking_success')
def booking_success():
    return render_template('booking_success.html')

@app.route('/movies')
def movies():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    movie_list = get_movies()
    return render_template('movies.html', movies=movie_list)

@app.route('/book/<movie_id>', methods=['GET', 'POST'])
def book(movie_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        movie = get_movie_by_id(movie_id)

        if quantity > movie[3]:  # available_seats
            flash('Not enough seats available!')
            return redirect(url_for('book', movie_id=movie_id))

        total = movie[2] * quantity 
        user_id = session['user_id']  
        movie_id = movie[0]  

        add_booking(user_id, movie_id, quantity, total)

        connection = sqlite3.connect('database/movie_ticket.db')
        cursor = connection.cursor()
        new_available_seats = movie[3] - quantity
        cursor.execute('UPDATE movies SET available_seats=? WHERE id=?', (new_available_seats, movie_id))
        connection.commit()
        connection.close()

        return redirect(url_for('checkout'))

    movie = get_movie_by_id(movie_id)
    return render_template('book_ticket.html', movie=movie)

def add_status_column_if_missing():
    connection = sqlite3.connect('database/movie_ticket.db')
    cursor = connection.cursor()

    # Check if the 'status' column exists in the 'bookings' table
    cursor.execute("PRAGMA table_info(bookings);")
    columns = [column[1] for column in cursor.fetchall()]

    if 'status' not in columns:
        # If 'status' column doesn't exist, add it
        cursor.execute('ALTER TABLE bookings ADD COLUMN status TEXT;')
        connection.commit()

    connection.close()

add_status_column_if_missing() 


@app.route('/decrement_quantity/<int:booking_id>', methods=['POST'])
def decrement_quantity(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database/movie_ticket.db')
    cursor = conn.cursor()

    # current booking details
    cursor.execute("""
        SELECT bookings.quantity, bookings.total, movies.price
        FROM bookings
        JOIN movies ON bookings.movie_id = movies.id
        WHERE bookings.id = ?
    """, (booking_id,))
    booking = cursor.fetchone()

    if booking:
        current_quantity = booking[0]
        current_total = booking[1]
        price_per_ticket = booking[2]

        # If quantity > 1, decrement the quantity 
        if current_quantity > 1:
            new_quantity = current_quantity - 1
            new_total = current_total - price_per_ticket
            cursor.execute("""
                UPDATE bookings
                SET quantity = ?, total = ?
                WHERE id = ?
            """, (new_quantity, new_total, booking_id))
        else:
            # delete the booking entry
            cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))

        conn.commit()

    conn.close()
    return redirect(url_for('checkout'))

from flask import flash, redirect, url_for

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))  

    user_id = session['user_id']

    try:
        connection = sqlite3.connect('database/movie_ticket.db')
        cursor = connection.cursor()

        cursor.execute('''
            SELECT b.quantity, b.total, m.name, b.id
            FROM bookings b
            JOIN movies m ON b.movie_id = m.id
            WHERE b.user_id = ?
        ''', (user_id,))
        bookings = cursor.fetchall()

        if not bookings:
            # flash('You have no bookings yet.')
            return redirect(url_for('home'))  # Redirect if no bookings found

        total_amount = sum([booking[1] for booking in bookings])  
        connection.close()

    except sqlite3.Error as e:
        flash(f"Database error: {e}")
        return redirect(url_for('home'))

    if request.method == 'POST':
        payment_method = request.form['payment_method'] 

        try:
            success = True  

            if success:
                connection = sqlite3.connect('database/movie_ticket.db')
                cursor = connection.cursor()

                for booking in bookings:
                    cursor.execute('''
                        INSERT INTO purchases (booking_id, payment_method, amount, transaction_date, status)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (booking[3], payment_method, booking[1], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Success'))

                # Update booking status to "Completed"
                cursor.execute('''
                    UPDATE bookings 
                    SET status = "Completed" 
                    WHERE user_id = ? AND status != "Completed"
                ''', (user_id,))
                connection.commit()
                connection.close()

                flash("Your payment has been processed successfully!")
                return redirect(url_for('home'))  # Redirect to homepage after payment success

            else:
                flash("Payment failed. Please try again later.")
                return redirect(url_for('checkout'))  # Stay on checkout if payment fails

        except sqlite3.Error as e:
            flash(f"Database error during payment processing: {e}")
            return redirect(url_for('home'))  # Redirect to homepage on DB error

    return render_template('checkout.html', bookings=bookings, total_amount=total_amount)

if __name__ == '__main__':
    app.run(debug=True)
