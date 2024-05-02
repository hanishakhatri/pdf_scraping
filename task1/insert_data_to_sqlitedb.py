import csv
import sqlite3


def create_table(conn):
    """Function to create database table if not exist"""
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS lookup (
                        belegnummer INTEGER,
                        assigned_integer INTEGER
                    )''')
    conn.commit()

def insert_data(conn, data):
    """Function to insert data into sqlite db"""
    cursor = conn.cursor()
    cursor.executemany('INSERT INTO lookup (belegnummer, assigned_integer) VALUES (?, ?)', data)
    conn.commit()

def read_csv(file_path):
    """Function to read csv file lookup.csv"""
    with open(file_path, encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        return [(int(row[0]), row[1]) for row in reader]

def main():
    """Execute the main functionality of the program"""
    
    csv_file = 'lookup.csv'
    db_file = 'flask_app/data/lookup.db'

    try:
        # Read data from CSV
        data = read_csv(csv_file)

        # Connect to SQLite database
        conn = sqlite3.connect(db_file)

        # Create table if not exists
        create_table(conn)

        # Insert data into the table
        insert_data(conn, data)
        print("Data inserted successfully ")

    except Exception as e:
        print("An error occurred:", e)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
