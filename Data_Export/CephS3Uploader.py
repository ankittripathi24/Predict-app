import os
import boto3
import pandas as pd
from botocore.exceptions import ClientError
from io import StringIO

class CephS3Uploader:
    def __init__(self, 
                 endpoint_url='http://your-ceph-endpoint:7480', 
                 access_key='your-access-key', 
                 secret_key='your-secret-key',
                 bucket_name='your-bucket-name'):
        """
        Initialize Ceph S3 Client
        
        :param endpoint_url: Ceph S3 endpoint URL
        :param access_key: Access key for authentication
        :param secret_key: Secret key for authentication
        :param bucket_name: S3 bucket name
        """
        # Create S3 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            # Important for Ceph: disable SSL verification if using self-signed certs
            verify=False
        )
        
        # Create S3 resource for additional operations
        self.s3_resource = boto3.resource(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            verify=False
        )
        
        self.bucket_name = bucket_name
        
        # Ensure bucket exists
        self._create_bucket_if_not_exists()
    
    def _create_bucket_if_not_exists(self):
        """
        Create bucket if it doesn't exist
        """
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} already exists.")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    print(f"Created bucket {self.bucket_name}")
                except Exception as create_error:
                    print(f"Error creating bucket: {create_error}")
            else:
                print(f"Unexpected error: {e}")
    
    def upload_dataframe_to_s3(self, 
                                dataframe: pd.DataFrame, 
                                object_key: str, 
                                file_format: str = 'csv'):
        """
        Upload pandas DataFrame to S3
        
        :param dataframe: Pandas DataFrame to upload
        :param object_key: S3 object key (path)
        :param file_format: File format (csv, parquet, etc.)
        """
        # Validate input
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        # Create buffer for file
        buffer = StringIO()
        
        # Save based on format
        if file_format == 'csv':
            dataframe.to_csv(buffer, index=False)
        elif file_format == 'parquet':
            buffer = BytesIO()
            dataframe.to_parquet(buffer, index=False)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
        
        try:
            # Reset buffer position
            buffer.seek(0)
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                buffer, 
                self.bucket_name, 
                object_key
            )
            print(f"Successfully uploaded {object_key} to S3")
        except Exception as e:
            print(f"Error uploading to S3: {e}")
    
    def download_dataframe_from_s3(self, 
                                   object_key: str, 
                                   file_format: str = 'csv'):
        """
        Download DataFrame from S3
        
        :param object_key: S3 object key to download
        :param file_format: File format (csv, parquet)
        :return: Pandas DataFrame
        """
        try:
            # Create buffer
            buffer = StringIO() if file_format == 'csv' else BytesIO()
            
            # Download file
            self.s3_client.download_fileobj(
                self.bucket_name, 
                object_key, 
                buffer
            )
            
            # Reset buffer position
            buffer.seek(0)
            
            # Read based on format
            if file_format == 'csv':
                return pd.read_csv(buffer)
            elif file_format == 'parquet':
                return pd.read_parquet(buffer)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
        
        except Exception as e:
            print(f"Error downloading from S3: {e}")
            return None
    
    def list_objects(self):
        """
        List objects in the bucket
        """
        try:
            # List objects
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            # Print object details
            if 'Contents' in response:
                print("Objects in bucket:")
                for obj in response['Contents']:
                    print(f"- {obj['Key']} (Size: {obj['Size']} bytes)")
            else:
                print("No objects found in the bucket.")
        
        except Exception as e:
            print(f"Error listing objects: {e}")
    
    def delete_object(self, object_key):
        """
        Delete an object from the bucket
        
        :param object_key: Object key to delete
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name, 
                Key=object_key
            )
            print(f"Deleted {object_key} from bucket")
        except Exception as e:
            print(f"Error deleting object: {e}")

# Example Usage
def main():
    # Configuration (replace with your actual Ceph S3 details)
    ceph_uploader = CephS3Uploader(
        endpoint_url='http://your-ceph-endpoint:7480',
        access_key='your-access-key',
        secret_key='your-secret-key',
        bucket_name='your-bucket-name'
    )
    
    # Create sample DataFrame
    sample_data = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['New York', 'San Francisco', 'Chicago']
    })
    
    try:
        # Upload CSV
        ceph_uploader.upload_dataframe_to_s3(
            sample_data, 
            'data/users.csv'
        )
        
        # List objects
        ceph_uploader.list_objects()
        
        # Download and verify
        downloaded_data = ceph_uploader.download_dataframe_from_s3('data/users.csv')
        print(downloaded_data)
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()