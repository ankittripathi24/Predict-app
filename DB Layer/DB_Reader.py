import pg8000
from pg8000 import Connection
from prettytable import PrettyTable

# Database connection parameters
DB_HOST = "127.0.0.1"
DB_NAME = "postgres"
DB_USER = "postgres"  # Replace with your PostgreSQL username
DB_PASSWORD = "BVV6Hty6bZ"  # Replace with your PostgreSQL password

def create_table(cursor):
    """Create the sensor_data table if it does not exist."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS sensor_data (
        machine_id DOUBLE PRECISION,
        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        temperature DOUBLE PRECISION,
        vibration DOUBLE PRECISION,
        energy_consumption DOUBLE PRECISION,
        PRIMARY KEY (machine_id, timestamp)
    );
    """
    cursor.execute(create_table_query)
    print("Table 'sensor_data' created or already exists.")

def insert_data(cursor, data):
    """Insert a record into the sensor_data table."""
    insert_data_query = """
    INSERT INTO sensor_data (machine_id, temperature, vibration, energy_consumption)
    VALUES (%s, %s, %s, %s);
    """
    cursor.execute(insert_data_query, data)

def fetch_all_records(cursor):
    """Fetch all records from the sensor_data table."""
    cursor.execute("SELECT * FROM sensor_data;")
    return cursor.fetchall()

def print_records(records):
    """Print records in a beautiful table format."""
    table = PrettyTable()
    table.field_names = ["Machine ID", "Timestamp", "Temperature", "Vibration", "Energy Consumption"]
    
    for record in records:
        table.add_row(record)
    
    print(table)

# Main execution
try:
    conn = Connection(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    # Create the table
    create_table(cursor)

    # Sample data to insert
    sample_data = (3.0, 36.5, 0.4, 151.0)

    # # Insert data
    # insert_data(cursor, sample_data)
    # conn.commit()  # Commit the transaction
    # print("Data inserted successfully.")

    # Fetch and print all records
    records = fetch_all_records(cursor)
    
    if records:
        print("All Records:")
        print_records(records)
    else:
        print("No records found.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()
