import os
from dotenv import load_dotenv
from supabase import create_client
from flask import Flask, render_template, jsonify

# Load environment variables from a .env file
load_dotenv()

# --- IMPORTANT: Corrected reading of Environment Variables ---
# You need to pass the NAME of the variable (e.g., "SUPABASE_URL") 
# to os.environ.get(), not the secret value itself.
# Please ensure your .env file has lines like this:
# SUPABASE_URL=https://dkidnjhrravzbblzzygd.supabase.co
# SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Check if environment variables are loaded (Good practice)
if not SUPABASE_URL or not SUPABASE_KEY:
    # Changed this to a print for terminal testing, but a raise is safer
    print("Warning: Supabase URL or Key not found in environment variables.")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize your Flask app instance
app = Flask(__name__)

# A simple root route
@app.route("/")
def home():
    return render_template('index.html')

# A route to fetch and display data from a Supabase table
@app.route("/users")
def get_users():
    """
    Example route to fetch data from a 'users' table in Supabase.
    """
    try:
        # Fetch all data from the 'users' table
        response = supabase.table("users").select("*").execute()
        
        # Check for errors and return the data
        if response.data:
            return jsonify(response.data)
        else:
            return jsonify({"error": "No data found or table does not exist."}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app directly (Optional, but useful for running with 'python hello.py')
if __name__ == "__main__":
    app.run(debug=True)