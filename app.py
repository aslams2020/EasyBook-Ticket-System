from flask import Flask, render_template, redirect, url_for, session, request, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Change this to a secure secret key

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('database/movie_ticket.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home page
@app.route('/')
def index():
    conn = get_db_connection()
    movies = conn.execute('SELECT * FROM movies WHERE is_active = 1 ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', movies=movies)

# User registration
# app.py - Update the register route to allow admin registration in development
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        # Validate inputs
        if not all([username, email, password, confirm_password, role]):
            flash('All fields are required!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('register.html')
        
        if role not in ['user', 'admin']:
            flash('Please select a valid role!', 'error')
            return render_template('register.html')
        
        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?', 
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username or email already exists!', 'error')
            conn.close()
            return render_template('register.html')
        
        is_admin = 1 if role == 'admin' else 0
        

        hashed_password = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
            (username, email, hashed_password, is_admin)
        )
        conn.commit()
        
        # Get the newly created user
        new_user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        
        # Auto-login after registration
        session['user_id'] = new_user['id']
        session['username'] = new_user['username']
        session['is_admin'] = bool(new_user['is_admin'])
        
        flash('Registration successful!', 'success')
        
        # Redirect based on role
        if session.get('is_admin'):
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('index'))
    
    return render_template('register.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password!', 'error')
            return render_template('login.html')
        
        try:
            conn = get_db_connection()
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()
            
            if user:
                if check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['is_admin'] = bool(user['is_admin'])
                    
                    flash('Login successful!', 'success')
                    conn.close()
                    
                    # Redirect to profile (which will show admin panel for admins)
                    return redirect(url_for('profile'))
                else:
                    flash('Invalid password!', 'error')
            else:
                flash('Username not found!', 'error')
                
            conn.close()
            return render_template('login.html')
            
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'error')
            print(f"Login error: {e}")
            return render_template('login.html')
    
    return render_template('login.html')

# User logout
@app.route('/logout')
def logout():
    try:
        username = session.get('username', 'User')
        session.clear()
        
        flash(f'{username} has been logged out successfully.', 'info')
        
    except Exception as e:
        session.clear()
        flash('You have been logged out.', 'info')
        print(f"Logout error: {e}")
    
    return redirect(url_for('index'))

# User profile and booking history
# @app.route('/profile')
# def profile():
#     if 'user_id' not in session:
#         flash('Please log in to view your profile.', 'error')
#         return redirect(url_for('login'))
    
#     # For admin users, show admin profile page
#     if session.get('is_admin'):
#         conn = get_db_connection()
#         user = conn.execute(
#             'SELECT * FROM users WHERE id = ?', (session['user_id'],)
#         ).fetchone()
        
#         # Get admin-specific stats
#         total_movies = conn.execute('SELECT COUNT(*) FROM movies').fetchone()[0]
#         total_bookings = conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]
#         total_revenue = conn.execute('SELECT SUM(total_price) FROM bookings WHERE status = "confirmed"').fetchone()[0] or 0
        
#         # Count users
#         total_users = conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0').fetchone()[0]
#         total_admins = conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1').fetchone()[0]
        
#         conn.close()
        
#         # DEBUG: Print the values to console
#         print(f"DEBUG - total_users: {total_users}, total_admins: {total_admins}")
#         print(f"DEBUG - Type of total_users: {type(total_users)}")
        
#         return render_template('admin/profile.html', 
#                              user=user,
#                              total_movies=total_movies,
#                              total_bookings=total_bookings,
#                              total_revenue=total_revenue,
#                              total_users=total_users,
#                              total_admins=total_admins)
        
#     # Regular user profile logic
#     conn = get_db_connection()
#     user = conn.execute(
#         'SELECT * FROM users WHERE id = ?', (session['user_id'],)
#     ).fetchone()
    
#     bookings = conn.execute(
#         '''SELECT b.*, m.title, s.showtime, s.theater_name, s.price, p.payment_status 
#            FROM bookings b 
#            JOIN showtimes s ON b.showtime_id = s.id 
#            JOIN movies m ON s.movie_id = m.id 
#            LEFT JOIN payments p ON b.id = p.booking_id
#            WHERE b.user_id = ? 
#            ORDER BY b.booking_date DESC''', 
#         (session['user_id'],)
#     ).fetchall()
    
#     conn.close()
    
#     return render_template('profile.html', user=user, bookings=bookings)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to view your profile.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    # For admin users, show admin profile with system stats
    if session.get('is_admin'):
        # Get admin-specific stats
        total_movies = conn.execute('SELECT COUNT(*) FROM movies').fetchone()[0]
        total_bookings = conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]
        total_revenue = conn.execute('SELECT SUM(total_price) FROM bookings WHERE status = "confirmed"').fetchone()[0] or 0
        total_users = conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0').fetchone()[0]
        total_admins = conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1').fetchone()[0]
        
        conn.close()
        
        return render_template('admin/profile.html', 
                             user=user,
                             total_movies=total_movies,
                             total_bookings=total_bookings,
                             total_revenue=total_revenue,
                             total_users=total_users,
                             total_admins=total_admins)
    
    # Regular user profile logic
    bookings = conn.execute(
        '''SELECT b.*, m.title, s.showtime, s.theater_name, s.price, p.payment_status 
           FROM bookings b 
           JOIN showtimes s ON b.showtime_id = s.id 
           JOIN movies m ON s.movie_id = m.id 
           LEFT JOIN payments p ON b.id = p.booking_id
           WHERE b.user_id = ? 
           ORDER BY b.booking_date DESC''', 
        (session['user_id'],)
    ).fetchall()
    
    conn.close()
    
    return render_template('profile.html', user=user, bookings=bookings)

@app.template_filter('type')
def get_type(value):
    return type(value).__name__

# Admin dashboard
# @app.route('/admin')
# def admin_dashboard():
#     if 'user_id' not in session:
#         flash('Please log in to access admin panel.', 'error')
#         return redirect(url_for('login'))
    
#     conn = get_db_connection()
#     user = conn.execute(
#         'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
#     ).fetchone()
    
#     if not user or not user['is_admin']:
#         flash('You do not have permission to access this page.', 'error')
#         return redirect(url_for('index'))
    
#     # Get stats for dashboard
#     total_movies = conn.execute('SELECT COUNT(*) FROM movies').fetchone()[0]
#     total_bookings = conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]
#     total_revenue = conn.execute('SELECT SUM(total_price) FROM bookings WHERE status = "confirmed"').fetchone()[0] or 0
    
#     conn.close()
    
#     return render_template('admin/dashboard.html', 
#                          total_movies=total_movies,
#                          total_bookings=total_bookings,
#                          total_revenue=total_revenue)


# Admin movie management
@app.route('/admin/movies')
def admin_movies():
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    # Order by id descending to show newest first
    movies = conn.execute('SELECT * FROM movies ORDER BY id DESC').fetchall()
    conn.close()
    
    return render_template('admin/movies.html', movies=movies)

# Admin showtimes management
@app.route('/admin/showtimes')
def admin_showtimes():
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    showtimes = conn.execute('''
        SELECT s.*, m.title as movie_title 
        FROM showtimes s 
        JOIN movies m ON s.movie_id = m.id 
        ORDER BY s.showtime DESC
    ''').fetchall()
    
    movies = conn.execute('SELECT id, title FROM movies WHERE is_active = 1').fetchall()
    conn.close()
    
    return render_template('admin/showtimes.html', showtimes=showtimes, movies=movies)

@app.route('/admin/showtimes/add', methods=['GET', 'POST'])
def admin_add_showtime():
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    movies = conn.execute('SELECT id, title FROM movies WHERE is_active = 1').fetchall()
    
    if request.method == 'POST':
        movie_id = request.form['movie_id']
        showtime_str = request.form['showtime']
        theater_name = request.form['theater_name']
        available_seats = int(request.form['available_seats'])
        price = float(request.form['price'])
        
        # Convert showtime string to proper datetime format
        from datetime import datetime
        try:
            showtime = datetime.strptime(showtime_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date/time format!', 'error')
            return redirect(url_for('admin_add_showtime'))
        
        conn.execute(
            'INSERT INTO showtimes (movie_id, showtime, theater_name, available_seats, price) VALUES (?, ?, ?, ?, ?)',
            (movie_id, showtime, theater_name, available_seats, price)
        )
        conn.commit()
        conn.close()
        
        flash('Showtime added successfully!', 'success')
        return redirect(url_for('admin_showtimes'))
    
    conn.close()
    return render_template('admin/add_showtime.html', movies=movies)

@app.route('/admin/showtimes/delete/<int:showtime_id>')
def admin_delete_showtime(showtime_id):
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    # Check if there are any bookings for this showtime
    bookings = conn.execute(
        'SELECT COUNT(*) as count FROM bookings WHERE showtime_id = ?', (showtime_id,)
    ).fetchone()
    
    if bookings['count'] > 0:
        flash('Cannot delete showtime with existing bookings!', 'error')
        return redirect(url_for('admin_showtimes'))
    
    conn.execute('DELETE FROM showtimes WHERE id = ?', (showtime_id,))
    conn.commit()
    conn.close()
    
    flash('Showtime deleted successfully!', 'success')
    return redirect(url_for('admin_showtimes'))

# Admin bookings management
@app.route('/admin/bookings')
def admin_bookings():
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    bookings = conn.execute('''
        SELECT b.*, u.username, m.title, s.showtime, s.theater_name, p.payment_status 
        FROM bookings b 
        JOIN users u ON b.user_id = u.id 
        JOIN showtimes s ON b.showtime_id = s.id 
        JOIN movies m ON s.movie_id = m.id 
        LEFT JOIN payments p ON b.id = p.booking_id
        ORDER BY b.booking_date DESC
    ''').fetchall()
    
    conn.close()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/booking/<int:booking_id>/cancel')
def admin_cancel_booking(booking_id):
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    # Get booking details to restore seats
    booking = conn.execute('''
        SELECT b.*, s.available_seats 
        FROM bookings b 
        JOIN showtimes s ON b.showtime_id = s.id 
        WHERE b.id = ?
    ''', (booking_id,)).fetchone()
    
    if booking:
        # Restore seats
        conn.execute(
            'UPDATE showtimes SET available_seats = available_seats + ? WHERE id = ?',
            (booking['num_tickets'], booking['showtime_id'])
        )
        
        # Update booking status
        conn.execute(
            'UPDATE bookings SET status = ? WHERE id = ?',
            ('cancelled', booking_id)
        )
        
        # Update payment status if exists
        conn.execute(
            'UPDATE payments SET payment_status = ? WHERE booking_id = ?',
            ('refunded', booking_id)
        )
        
        conn.commit()
        flash('Booking cancelled successfully! Seats have been restored.', 'success')
    else:
        flash('Booking not found!', 'error')
    
    conn.close()
    return redirect(url_for('admin_bookings'))

# Admin movies management - Add, Edit, Delete
@app.route('/admin/movies/add', methods=['GET', 'POST'])
def admin_add_movie():
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        duration = int(request.form['duration'])
        genre = request.form['genre']
        release_date = request.form['release_date']
        poster_url = request.form['poster_url']
        
        conn.execute(
            'INSERT INTO movies (title, description, duration, genre, release_date, poster_url) VALUES (?, ?, ?, ?, ?, ?)',
            (title, description, duration, genre, release_date, poster_url)
        )
        conn.commit()
        conn.close()
        
        flash('Movie added successfully!', 'success')
        return redirect(url_for('admin_movies'))
    
    conn.close()
    return render_template('admin/add_movie.html')

@app.route('/admin/movies/edit/<int:movie_id>', methods=['GET', 'POST'])
def admin_edit_movie(movie_id):
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)).fetchone()
    
    if not movie:
        flash('Movie not found!', 'error')
        return redirect(url_for('admin_movies'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        duration = int(request.form['duration'])
        genre = request.form['genre']
        release_date = request.form['release_date']
        poster_url = request.form['poster_url']
        is_active = 1 if 'is_active' in request.form else 0
        
        conn.execute(
            '''UPDATE movies 
               SET title = ?, description = ?, duration = ?, genre = ?, 
                   release_date = ?, poster_url = ?, is_active = ?
               WHERE id = ?''',
            (title, description, duration, genre, release_date, poster_url, is_active, movie_id)
        )
        conn.commit()
        conn.close()
        
        flash('Movie updated successfully!', 'success')
        return redirect(url_for('admin_movies'))
    
    conn.close()
    return render_template('admin/edit_movie.html', movie=movie)


@app.route('/movies')
def movies():
    conn = get_db_connection()
    # Order by id descending to show newest first
    movies = conn.execute('SELECT * FROM movies WHERE is_active = 1 ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('movies.html', movies=movies)

@app.route('/admin/movies/delete/<int:movie_id>')
def admin_delete_movie(movie_id):
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    try:
        # First, delete all showtimes associated with this movie
        conn.execute('DELETE FROM showtimes WHERE movie_id = ?', (movie_id,))
        
        # Then delete the movie
        conn.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        
        conn.commit()
        flash('Movie and associated showtimes deleted successfully!', 'success')
        
    except sqlite3.Error as e:
        conn.rollback()
        flash('Error deleting movie: ' + str(e), 'error')
        print(f"Delete error: {e}")
    
    finally:
        conn.close()
    
    return redirect(url_for('admin_movies'))

    
# app.py - Add a confirmation route
@app.route('/admin/movies/delete/<int:movie_id>/confirm')
def admin_confirm_delete_movie(movie_id):
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    # Get movie details and associated showtimes
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)).fetchone()
    showtimes = conn.execute(
        'SELECT COUNT(*) as count FROM showtimes WHERE movie_id = ?', (movie_id,)
    ).fetchone()
    
    conn.close()
    
    return render_template('admin/confirm_delete_movie.html', 
                         movie=movie, 
                         showtimes_count=showtimes['count'])

# Then update the delete route to handle the actual deletion
@app.route('/admin/movies/delete/<int:movie_id>/execute')
def admin_execute_delete_movie(movie_id):
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Delete associated showtimes first
        conn.execute('DELETE FROM showtimes WHERE movie_id = ?', (movie_id,))
        
        # Then delete the movie
        conn.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        
        conn.commit()
        flash('Movie and all associated showtimes deleted successfully!', 'success')
        
    except sqlite3.Error as e:
        conn.rollback()
        flash('Error deleting movie: ' + str(e), 'error')
        print(f"Delete error: {e}")
    
    finally:
        conn.close()
    
    return redirect(url_for('admin_movies'))

# Admin users management
@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    users = conn.execute('SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:user_id>/toggle_admin')
def admin_toggle_admin(user_id):
    if 'user_id' not in session:
        flash('Please log in to access admin panel.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    if not user or not user['is_admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    
    # Prevent self-demotion
    if user_id == session['user_id']:
        flash('You cannot change your own admin status!', 'error')
        return redirect(url_for('admin_users'))
    
    target_user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if target_user:
        new_status = 0 if target_user['is_admin'] else 1
        conn.execute('UPDATE users SET is_admin = ? WHERE id = ?', (new_status, user_id))
        conn.commit()
        
        status_text = "granted" if new_status else "revoked"
        flash(f'Admin privileges {status_text} successfully!', 'success')
    else:
        flash('User not found!', 'error')
    
    conn.close()
    return redirect(url_for('admin_users'))


# Movie details and showtimes
@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    conn = get_db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)).fetchone()
    showtimes = conn.execute(
        'SELECT * FROM showtimes WHERE movie_id = ? AND showtime > datetime("now") ORDER BY showtime',
        (movie_id,)
    ).fetchall()
    conn.close()
    
    if not movie:
        flash('Movie not found!', 'error')
        return redirect(url_for('movies'))
    
    return render_template('movie_details.html', movie=movie, showtimes=showtimes)

# Booking process
@app.route('/book/<int:showtime_id>', methods=['GET', 'POST'])
def book_ticket(showtime_id):
    if 'user_id' not in session:
        flash('Please log in to book tickets.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    showtime = conn.execute(
        'SELECT s.*, m.title FROM showtimes s JOIN movies m ON s.movie_id = m.id WHERE s.id = ?',
        (showtime_id,)
    ).fetchone()
    
    if not showtime:
        flash('Showtime not found!', 'error')
        return redirect(url_for('movies'))
    
    if request.method == 'POST':
        num_tickets = int(request.form['tickets'])
        
        if num_tickets <= 0:
            flash('Please select at least one ticket.', 'error')
            return redirect(url_for('book_ticket', showtime_id=showtime_id))
        
        if num_tickets > showtime['available_seats']:
            flash('Not enough seats available!', 'error')
            return redirect(url_for('book_ticket', showtime_id=showtime_id))
        
        total_price = num_tickets * showtime['price']
        
        # Create booking
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO bookings (user_id, showtime_id, num_tickets, total_price) VALUES (?, ?, ?, ?)',
            (session['user_id'], showtime_id, num_tickets, total_price)
        )
        booking_id = cursor.lastrowid
        
        # Update available seats
        conn.execute(
            'UPDATE showtimes SET available_seats = available_seats - ? WHERE id = ?',
            (num_tickets, showtime_id)
        )
        
        conn.commit()
        conn.close()
        
        session['booking_id'] = booking_id
        return redirect(url_for('checkout'))
    
    conn.close()
    return render_template('book_ticket.html', showtime=showtime)

# Checkout process
# Checkout process - Updated query
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'booking_id' not in session or 'user_id' not in session:
        flash('Please complete your booking first.', 'error')
        return redirect(url_for('movies'))
    
    booking_id = session['booking_id']
    conn = get_db_connection()
    booking = conn.execute(
        '''SELECT b.*, m.title, s.showtime, s.theater_name, s.movie_id 
           FROM bookings b 
           JOIN showtimes s ON b.showtime_id = s.id 
           JOIN movies m ON s.movie_id = m.id 
           WHERE b.id = ?''', 
        (booking_id,)
    ).fetchone()
    
    if request.method == 'POST':
        payment_method = request.form['payment_method']
        
        # Process payment (simulated)
        transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Record payment
        conn.execute(
            'INSERT INTO payments (booking_id, amount, payment_method, payment_status, transaction_id, payment_date) VALUES (?, ?, ?, ?, ?, ?)',
            (booking_id, booking['total_price'], payment_method, 'completed', transaction_id, datetime.now())
        )
        
        # Update booking status
        conn.execute(
            'UPDATE bookings SET status = ? WHERE id = ?',
            ('confirmed', booking_id)
        )
        
        conn.commit()
        conn.close()
        
        # Clear booking from session
        session.pop('booking_id', None)
        
        return redirect(url_for('booking_success', booking_id=booking_id))
    
    conn.close()
    return render_template('checkout.html', booking=booking)

# Booking success
@app.route('/booking/success/<int:booking_id>')
def booking_success(booking_id):
    if 'user_id' not in session:
        flash('Please log in to view your booking.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    booking = conn.execute(
        '''SELECT b.*, m.title, s.showtime, s.theater_name, s.price, s.movie_id 
           FROM bookings b 
           JOIN showtimes s ON b.showtime_id = s.id 
           JOIN movies m ON s.movie_id = m.id 
           WHERE b.id = ? AND b.user_id = ?''', 
        (booking_id, session['user_id'])
    ).fetchone()
    conn.close()
    
    if not booking:
        flash('Booking not found!', 'error')
        return redirect(url_for('index'))
    
    return render_template('booking_success.html', booking=booking)


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    conn = get_db_connection()
    conn.rollback()
    conn.close()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)