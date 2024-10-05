from flask import Flask, request, redirect, render_template_string
import mysql.connector
from mysql.connector import errorcode

# Initialize the Flask app
app = Flask(__name__)

# Database connection
def get_db_connection(db_name=None):
    config = {
        'host': "mysql_server",
        'user': "root",
        'password': "",  # Empty password ->  MYSQL_ALLOW_EMPTY_PASSWORD=yes
    }
    if db_name:
        config['database'] = db_name
    return mysql.connector.connect(**config)

# Function to initialize the database and table
def init_db():
    try:
        # Connect without specifying the database to create it if it doesn't exist
        db = get_db_connection()
        cursor = db.cursor()

        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
        cursor.close()
        db.close()

        # Connect to the newly created database
        db = get_db_connection(db_name="test_db")
        cursor = db.cursor()

        # Create 'users' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        """)

        # Check if the table is empty before inserting default users
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count == 0:
            # Initialize the users table with default users
            default_users = ['Ran', 'Batel', 'Shaia', 'Geffen', 'Red', 'Kira']
            cursor.executemany("INSERT INTO users (name) VALUES (%s)", [(user,) for user in default_users])

        db.commit()
        cursor.close()
        db.close()
        print("Database initialized successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        else:
            print(err)
    except Exception as e:
        print(f"An error occurred: {e}")

# Route to display users
@app.route('/')
def show_users():
    try:
        db = get_db_connection(db_name="test_db")
        cursor = db.cursor()

        # Get all users from the table
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        cursor.close()
        db.close()

        # HTML template to display users and provide form to add/remove users
        template = '''
        <h1>Users List</h1>
        <ul>
            {% for user in users %}
                <li>{{ user[1] }} <a href="/delete/{{ user[0] }}">(Delete)</a></li>
            {% endfor %}
        </ul>

        <h2>Add a New User</h2>
        <form method="POST" action="/add">
            <input type="text" name="name" placeholder="Enter name" required>
            <input type="submit" value="Add User">
        </form>
        '''
        return render_template_string(template, users=users)
    except mysql.connector.Error as err:
        return f"Error: {err}"

# Route to add a new user
@app.route('/add', methods=['POST'])
def add_user():
    user_name = request.form['name']
    try:
        db = get_db_connection(db_name="test_db")
        cursor = db.cursor()

        # Insert a new user into the table
        cursor.execute("INSERT INTO users (name) VALUES (%s)", (user_name,))
        db.commit()

        cursor.close()
        db.close()

        return redirect('/')
    except mysql.connector.Error as err:
        return f"Error: {err}"

# Route to delete a user
@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    try:
        db = get_db_connection(db_name="test_db")
        cursor = db.cursor()

        # Delete user by ID
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()

        cursor.close()
        db.close()

        return redirect('/')
    except mysql.connector.Error as err:
        return f"Error: {err}"

# Initialize the database when the application starts
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
