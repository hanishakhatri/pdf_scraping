# Import necessary modules
import sqlite3
from flask import Flask, request, jsonify, render_template

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
        return jsonify({'error': 'No assigned_integer provided in the request'}), 400

    try:
        assigned_integer = int(assigned_integer_str) 
        # Convert assigned_integer_str to integer
    except ValueError:  
        # Handle invalid assigned_integer
        return jsonify({'error': 'Invalid assigned_integer provided in the request'}), 400

    conn = sqlite3.connect(DB_FILE)
    # Connect to the SQLite database
    try:
        # Create a cursor object
        cursor = conn.cursor()
        cursor.execute('SELECT belegnummer FROM lookup WHERE assigned_integer = ?',
                       (assigned_integer,))
        # Fetch the result of the query
        result = cursor.fetchone()
        if result:
            # Return document number if found
            return jsonify({'belegnummer': result[0]})
        else:
            return jsonify(
                {'error': 'No document number found for the given assigned integer'}
                ), 404
    except Exception:
        # Handle unexpected errors
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        # Close the database connection after use
        conn.close()