# 🎬 EasyBook - Movie Ticket Booking System

![Python](https://img.shields.io/badge/Python-3.8%252B-green)
![Flask](https://img.shields.io/badge/Flask-2.3.0-lightgrey)
![SQLite](https://img.shields.io/badge/SQLite-Database-yellow)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1-purple)

A comprehensive movie ticket booking system built with **Flask** that allows users to browse movies, book tickets, and manage showtimes. Features separate interfaces for **regular users** and **administrators**.

---

## ✨ Features

### 🎯 User Features
- **User Registration & Authentication** – Secure signup and login system  
- **Movie Browser** – Browse available movies with details and showtimes  
- **Ticket Booking** – Select seats and book tickets with real-time availability  
- **Booking History** – View past and upcoming bookings  
- **User Profile** – Personal dashboard with booking statistics  
- **Payment Integration** – Simulated payment gateway for ticket purchases  

### ⚡ Admin Features
- **Admin Dashboard** – Comprehensive system overview with analytics  
- **Movie Management** – Add, edit, and manage movie listings  
- **Showtime Management** – Create and manage movie showtimes  
- **User Management** – View and manage user accounts and permissions  
- **Booking Management** – Monitor and manage all bookings  
- **Revenue Tracking** – View booking revenue and statistics  

---

## 🛠️ Technology Stack
- **Backend:** Python 3.8+, Flask 2.3.0  
- **Database:** SQLite (SQLAlchemy-like interface)  
- **Frontend:** HTML5, CSS3, Bootstrap 5.1, JavaScript  
- **Authentication:** Werkzeug security for password hashing  
- **Templating:** Jinja2 with template inheritance  

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher  
- `pip` (Python package manager)  

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/yourusername/EasyBook-Ticket-System.git

python create_db.py
python add_sample_data.py
python app.py
```

### 🗄️ Database Schema

- **users** – User accounts and authentication
- **movies** – Movie information and details
- **showtimes** – Movie screening times and theater information
- **bookings** – Ticket booking records
- **payments** – Payment transaction records


## 👥 User Roles

### Regular User
- Browse movies and showtimes
- Book tickets for available shows
- View personal booking history
- Manage personal profile

### Administrator

- Full system access and management
- Add/Edit movies and showtimes
- Manage user accounts and permissions
- View system analytics and reports
- Monitor booking revenue
# Run the application
python app.py
