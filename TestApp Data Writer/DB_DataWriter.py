import pg8000
from pg8000 import Connection

# Database connection parameters
DB_HOST = "127.0.0.1"
DB_NAME = "postgres"
DB_USER = "postgres"  # Replace with your PostgreSQL username
DB_PASSWORD = "BVV6Hty6bZ"  # Replace with your PostgreSQL password

# Connect to PostgreSQL database
try:
    conn = Connection(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    # Define the SQL command to create the table if it does not exist
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

    # Execute the create table command
    cursor.execute(create_table_query)
    print("Table 'sensor_data' created or already exists.")

    # Define the data to be inserted
    insert_data_query = """
    INSERT INTO sensor_data (machine_id, temperature, vibration, energy_consumption)
    VALUES (%s, %s, %s, %s);
    """
    
    # Sample data to insert
    sample_data = (1.0, 25.5, 0.5, 150.0)

    # Execute the insert command
    cursor.execute(insert_data_query, sample_data)
    conn.commit()  # Commit the transaction
    print("Data inserted successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()
