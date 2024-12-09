# Import necessary modules
import sqlite3
from flask import Flask, request, render_template

# Create a Flask application instance
app = Flask(__name__)
# Path to the SQLite database file
DB_FILE = 'data/lookup.db'


# Route for the home page
@app.route("/")
def home():
    """
    Render the index.html template for the home page.
    """
    return render_template("index.html")


# Route for looking up documents by assigned integer
@app.route('/lookup', methods=['GET'])
def lookup():
    """
    Endpoint for looking up a document by assigned integer.
    :param assigned_integer_str: Assigned integer provided in the request URL
    :return: JSON response containing document information or error message
    """
    assigned_integer_str = request.args.get('assigned_integer')

    if assigned_integer_str is None:
        # Check if assigned_integer is provided in the request
        error_message = 'No assigned integer provided in the request'
        return render_template('error.html', error_message=error_message), 400

    try:
        assigned_integer = int(assigned_integer_str) 
        # Convert assigned_integer_str to integer
    except ValueError: 
        # Handle invalid assigned_integer
        error_message = 'Invalid assigned integer provided in the request'
        return render_template('error.html', error_message=error_message), 400

    conn = sqlite3.connect(DB_FILE)
    # Connect to the SQLite database
    try:
        # Create a cursor object
        cursor = conn.cursor()
        cursor.execute('SELECT belegnummer,assigned_integer FROM lookup WHERE assigned_integer = ?',
                       (assigned_integer,))
        # Fetch the result of the query
        result = cursor.fetchone()
        if result:
            # Return document number if found
            return render_template('result.html', belegnummer=result[0], assigned_integer=result[1])
        else:
            error_message = 'No document number found for the given assigned integer'
            return render_template('error.html', error_message=error_message), 404
    except Exception:
        # Handle unexpected errors
        error_message = 'An unexpected error occurredr'
        return render_template('error.html', error_message=error_message), 500
    finally:
        # Close the database connection after use
        conn.close()
        
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)