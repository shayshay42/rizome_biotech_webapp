import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

print(f"Connecting with:")
print(f"  User: {USER}")
print(f"  Host: {HOST}")
print(f"  Port: {PORT}")
print(f"  Database: {DBNAME}")

# Connect to the database
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Example query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Current Time:", result)
    
    # Test our tables exist
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"Users in database: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM cbc_results")
    cbc_count = cursor.fetchone()[0]
    print(f"CBC results in database: {cbc_count}")

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Connection closed.")
    print("SUCCESS: Remote Supabase is working!")

except Exception as e:
    print(f"Failed to connect: {e}")