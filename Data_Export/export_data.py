import os
import pg8000
import pandas as pd
import rados

# Database connection settings from environment variables
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "postgres")

DB_USER = os.getenv("DB_USER", 'postgres')  # Will be set from Kubernetes Secret
DB_PASSWORD = os.getenv("DB_PASSWORD", 'BVV6Hty6bZZ')  # Will be set from Kubernetes Secret


# Ceph configuration settings
CEPH_CONF_FILE = '/etc/ceph/ceph.conf'  # Path to your Ceph configuration file
BUCKET_NAME = 'sensor-data-bucket'  # Replace with your desired bucket name

def export_data_to_csv():
    """Export data from PostgreSQL to a CSV file and upload it to Ceph."""
    try:
        conn = pg8000.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()

        # Define the SQL query to fetch data
        query = "SELECT machine_id, timestamp, temperature, vibration, energy_consumption FROM sensor_data;"

        # Use pandas to read the SQL query directly into a DataFrame
        df = pd.read_sql(query, conn)

        # Save DataFrame to CSV
        csv_file_path = 'sensor_data_export.csv'
        df.to_csv(csv_file_path, index=False)
        print(f"Data exported successfully to {csv_file_path}")

        # Upload CSV file to Ceph
        upload_to_ceph(csv_file_path)

    except Exception as e:
        print(f"An error occurred while exporting data: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def upload_to_ceph(file_path):
    """Upload a file to a Ceph storage bucket."""
    try:
        # Create a connection to the Ceph cluster
        cluster = rados.Rados(conffile=CEPH_CONF_FILE)
        cluster.connect()

        # Create an I/O context for the bucket (pool)
        ioctx = cluster.open_ioctx(BUCKET_NAME)

        # Upload the file
        with open(file_path, 'rb') as f:
            ioctx.write_full(file_path.split('/')[-1], f.read())
        
        print(f"Uploaded {file_path} to Ceph bucket '{BUCKET_NAME}'.")

    except Exception as e:
        print(f"An error occurred while uploading to Ceph: {e}")
    finally:
        if 'ioctx' in locals():
            ioctx.close()
        if 'cluster' in locals():
            cluster.shutdown()

if __name__ == "__main__":
    export_data_to_csv()
