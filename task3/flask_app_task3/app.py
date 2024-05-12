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


def main():
    # Example usage:
    pdf_path = 'pdfs/29386.pdf'
    csv_file = "29386.csv"
    extracted_text = extract_text_from_pdf(pdf_path)
    lines = extracted_text.strip().split('\n')
    list_extracted_data = extract_items_from_text(lines)
    write_items_to_csv(list_extracted_data,csv_file)

if __name__ == "__main__":
    main()