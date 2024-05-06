# de-assignment-tenderfix
DE Assignment by TenderFix

# TASK-1  Flask App with SQLite Database

This project is a Flask application that uses a SQLite database to store and retrieve data. The application follows a containerized approach, where the Flask app and the SQLite database run in separate containers managed by Docker Compose.

## Prerequisites

Before running the application, make sure you have the following installed:

- Docker
- Docker Compose

## create virtual enviroment 

- python -m venv env
- source env/bin/activate  # On Windows, use env\Scripts\activate

## Project Structure

- `docker-compose.yml`: Docker Compose configuration file that defines the services for the Flask app and SQLite database.
- `flask_app/data/lookup.db`: SQLite database file that stores the data.
- `insert_data_to_sqlitedb.py`: Python script to initialize the SQLite database with data from the `lookup.csv` file.
- `lookup.csv`: CSV file containing the initial data to be inserted into the SQLite database.

## Setup

1. Clone the repository:

git clone https://github.com/hanishakhatri/de-assignment-tenderfix.git

cd de-assignment-tenderfix/task1

2. Initialize the SQLite database by running the Python script:
python insert_data_to_sqlitedb.py

This script will create the `lookup` table in the SQLite database and insert the data from the `lookup.csv` file.

3. Build and start the Docker containers:

- docker build -t flask-app:latest .
- cd .. 
- docker-compose up -d  
- docker-compose ps
- docker-compose logs -f



## Task2 - Identifying the relevant "artikelnummer" (product numbers) for each entry in the PDF documents using the `mapToProducts.csv` file.


1. Build and start the Docker containers:

- cd task2/flask-app-task2
- docker build -t flask-app-task-2:latest .
- cd .. 
- docker-compose up -d  
- docker-compose ps
- docker-compose logs -f
