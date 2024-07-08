# Import necessary modules
import re
import csv
import sqlite3
import pandas as pd
from flask import Flask, jsonify

app = Flask(__name__)
# Specify the DB_File
DB_FILE = 'data/mapToProduct.db'
# Specify the output CSV file path
OUTPUT_CSV_FILE = 'output.csv'



def read_csv_to_df(csv_file):
    """Reads a CSV file into a pandas DataFrame."""
    try:
        df = pd.read_csv(csv_file)
        return df
    except FileNotFoundError:
        # HTTP status code 404 for file not found
        error_message = {'error': f"File '{csv_file}' not found."}
        return jsonify(error_message), 404  
    except Exception:
        # HTTP status code 500 for internal server error
        error_message = {'error': 'Error in function read csv to dataframe'}
        return jsonify(error_message), 500  

def filter_df_by_document_number(df, document_number):
    """Filters the DataFrame by the given document number."""
    try:
        filtered_df = df[df['belegnummer'] == document_number]
        return filtered_df
    except KeyError:
        # HTTP status code 400 for bad request
        error_message = {'error': "Column 'belegnummer' not found in DataFrame."}
        return jsonify(error_message), 400
    except Exception as e:
        # HTTP status code 500 for internal server error
        error_message = {'error': f"Error filtering DataFrame: {e}"}
        return jsonify(error_message), 500
    
def dataframe_to_sqlitedb(extracted_df):
    """save dataframe to sqlite data base"""
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        # Write the filtered DataFrame to a SQLite database
        extracted_df.to_sql('mapToProducts', conn, index=False, if_exists='replace')
    
    except sqlite3.Error as e:
        error_message = {'error': f"SQLite error: {e}"}
        return jsonify(error_message), 500  # HTTP status code 500 for internal server error
    except Exception as e:
        error_message = {'error': f"Error writing DataFrame to SQLite database: {e}"}
        return jsonify(error_message), 500  # HTTP status code 500 for internal server error
    finally:
        conn.close()
    
def read_data_from_db():
    """
    Reads data from the SQLite database and returns the results.
    """
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        # Execute the SQL query
        cursor.execute("""
            SELECT assigned_integer, belegnummer, GROUP_CONCAT(artikelnummer, ', ') AS product_numbers, entry_number
            FROM mapToProducts
            GROUP BY entry_number
        """)

        # Fetch the results
        results = cursor.fetchall()
        
        # Drop the table after fetching results
        sql_drop_table = """
        DROP TABLE IF EXISTS mapToProducts;
        """
        cursor.execute(sql_drop_table)
        
        return results
    except Exception as e:
        # Handle the exception and return an error message in JSON format
        error_message = {'error': str(e)}
        return jsonify(error_message), 500
    finally:
        # Close the database connection in the finally block
        conn.close()
        
def fill_empty_comments(df):
    """
    Fills empty comments with the previous non-empty comment.
    """
    try:
        # Check if the DataFrame is empty or doesn't contain the 'comments' column
        if df.empty or 'comments' not in df.columns:
            raise ValueError("DataFrame is empty or doesn't contain the 'comments' column")

        prev_comment = ""
        for i in range(len(df) - 1, -1, -1):
            row_index = df.index[i]
            if pd.isna(df.at[row_index, 'comments']) or df.at[row_index, 'comments'] == '':
                df.at[row_index, 'comments'] = prev_comment
            else:
                prev_comment = df.at[row_index, 'comments']
        return df
    except ValueError as ve:
        # Return a JSON response with the error message and HTTP status code 400 (Bad Request)
        error_message = {'error': str(ve)}
        return jsonify(error_message), 400
    except Exception as e:
        # Return a JSON response with the error message and HTTP status code 500 (Internal Server Error)
        error_message = {'error': str(e)}
        return jsonify(error_message), 500

def extract_entry_numbers(df, pattern_extract,assigned_integer):
    """Extracts entry numbers from comments using a regular expression pattern."""
    try:
        entry_numbers = []
        for index, row in df.iterrows():
            entry_number = ""
            match = re.search(pattern_extract, row['comments'])
            if match:
                entry_number = match.group(1)
            entry_numbers.append(entry_number if entry_number else None)
        df['entry_number'] = entry_numbers
        df['assigned_integer'] = assigned_integer
        return df
    except Exception as e:
        # Return a JSON response with the error message and HTTP status code 500 (Internal Server Error)
        error_message = {'error': str(e)}
        return jsonify(error_message), 500

def write_results_to_csv(results,output_csv_file):
    """Writes the results to a CSV file."""
    try:
        with open(output_csv_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['assigned_integer','belegnummer', 'product_number', 'entry_number'])
            csv_writer.writerows(results)
        return output_csv_file
    except Exception as e:
        # Return a JSON response with the error message and HTTP status code 500 (Internal Server Error)
        error_message = {'error': str(e)}
        return jsonify(error_message), 500
        
@app.route("/")
def home():
    """
    Render the index.html template for the home page.
    """
    return jsonify({"message": "Hello"})


@app.route('/identify_product_numbers/<document_number>', methods=['GET'])
def identify_product_numbers(document_number):
    '''it takes a document number as input and finds the corresponding entries'''
    try:
        # Get the document number from the query parameters
        document_number = int(document_number)

        # Read the CSV file into a pandas DataFrame
        df = read_csv_to_df('mapToProducts.csv')
        lookup_df  = read_csv_to_df('lookup.csv')
        
        # Filter the DataFrame by the document number to get assigned_integer
        lookup_filtered_df = filter_df_by_document_number(lookup_df, document_number)
        assigned_integer = lookup_filtered_df['assigned_integer'].values[0]

        # Filter the DataFrame by the document number
        filtered_df = filter_df_by_document_number(df, document_number)
        
        # Fills empty comments with the previous non-empty comment.
        filtered_df = fill_empty_comments(filtered_df)

        # Define the regular expression pattern
        pattern = r'Pos\.\s([\d.]+)'
        # Filter the DataFrame to keep rows where the pattern exists in the 'comments' column
        filtered_df_pattern = filtered_df[filtered_df['comments'].str.contains(pattern)]

        # Extract entry numbers from comments
        extracted_df = extract_entry_numbers(filtered_df_pattern, pattern,assigned_integer)
      
        # filtered DataFrame to a SQLite database
        dataframe_to_sqlitedb(extracted_df)
        
        # Fetch the results
        results = read_data_from_db()
        
        # Write the results to the CSV file
        output_csv_file = write_results_to_csv(results,output_csv_file = OUTPUT_CSV_FILE)

        # Return the path to the output CSV file
        return jsonify({"message": "Results written to csv file", "output_csv_file": output_csv_file})
    except Exception as e:
        # Return a JSON response with the error message and HTTP status code 500 (Internal Server Error)
        error_message = {'error': str(e)}
        return jsonify(error_message), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
