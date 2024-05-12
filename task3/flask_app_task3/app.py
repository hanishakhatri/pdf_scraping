import PyPDF2
import re
import json 
import csv

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.

    Parameters:
    pdf_path (str): The path to the PDF file.

    Returns:
    str: The extracted text from the PDF.
    """
    # Open the PDF file
    with open(pdf_path, 'rb') as pdf_file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Get the total number of pages
        num_pages = len(pdf_reader.pages)

        # Initialize an empty string to store the extracted text
        text = ''

        # Loop through each page and extract the text
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    return text

def write_items_to_csv(items, csv_file):
    """
    Write items to a CSV file.

    Parameters:
    items (list): List of dictionaries containing items.
    csv_file (str): Path to the CSV file.
    """
    fieldnames = ['entry_number', 'quantity', 'entry_body']

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)

    print("Data saved to", csv_file)
    
import csv
import sqlite3

def csv_to_sqlite(input_file, db_file, table_name):
    """
    Convert a CSV file to a SQLite database table.

    Parameters:
    input_file (str): Path to the input CSV file.
    db_file (str): Path to the SQLite database file.
    table_name (str): Name of the SQLite database table.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Open the input CSV file
    with open(input_file, mode='r', newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        # Extract header from the CSV file
        header = next(reader)
        # Create a table in the database with the provided table name
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        cursor.execute(f'CREATE TABLE {table_name} ({", ".join(header)})')
        # Insert the data from the CSV file into the table
        for row in reader:
            cursor.execute(f'INSERT INTO {table_name} VALUES ({", ".join("?" * len(row))})', row)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f"CSV file '{input_file}' converted to SQLite database table '{table_name}' in '{db_file}'")


def write_results_to_csv(results,output_csv_file):
    """Writes the results to a CSV file."""
    with open(output_csv_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['entry_number','entry_body','quantity','assigned_integer','belegnummer', 'product_number'])
        csv_writer.writerows(results)
    return output_csv_file



def extract_items_from_text(lines):
    items = []
    entry_number = ""
    quantity = ""
    inner_item = {}
    line_start_index = None
    line_end_index = None 
    for index,line in enumerate(lines):
        entry_number_match = re.search(r'\b(\d+\.\d+)\.(?!\d)', line)
        if entry_number_match and entry_number == "":
            entry_number = entry_number_match.group(1)
            line_start_index = index + 1
            inner_item["entry_number"] = entry_number
        quantity_match = re.search(r'(St\d+,\d+|m\d+,\d+|psch\d+,\d+)', line)
        if quantity_match and quantity == "":
            quantity = quantity_match.group(1)
            # Extracting the numerical part using regular expression
            numerical_part = re.search(r'\d+,\d+', quantity).group()
            # Extracting the unit part using regular expression
            unit_part = re.search(r'(m|St|psch|Stck)', quantity).group()
            # Concatenating the numerical part and the unit part
            line_end_index = index
            inner_item["quantity"] = numerical_part + " "  +unit_part
        if line_start_index and line_end_index:
            entry_body= lines[line_start_index:line_end_index]
            inner_item["entry_body"] = '\n'.join(entry_body)
            items.append(inner_item)  
            inner_item = {}
            line_start_index = ""
            line_end_index = ""
            entry_number = ""
            quantity = ""
            
    return items

def sqlite_query(datafile):
    conn = sqlite3.connect(datafile)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute("""
        SELECT entry_data.entry_number, entry_data.entry_body, entry_data.quantity, combined_data.assigned_integer, combined_data.belegnummer, combined_data.product_number
        FROM entry_data
        JOIN combined_data ON entry_data.entry_number = combined_data.entry_number
    """)

    # Fetch all rows from the result set
    rows = cursor.fetchall()
    return rows

def main():
    # Example usage:
    try :
        pdf_path = 'pdfs/29386.pdf'
        csv_file = "29386.csv"
        extracted_text = extract_text_from_pdf(pdf_path)
        lines = extracted_text.strip().split('\n')
        list_extracted_data = extract_items_from_text(lines)
        write_items_to_csv(list_extracted_data,csv_file)
        # Example usage:
        input_file = 'data.csv'  # Path to the input combined CSV file
        db_file = 'data.db'  # Path to the output SQLite database file
        table_name = 'entry_data'  # Name of the SQLite database table
        csv_to_sqlite(input_file, db_file, table_name)
        rows = sqlite_query('data.db')
        write_results_to_csv(rows,output_csv_file = "output.csv")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()