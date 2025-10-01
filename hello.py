# hello.py

import os
from dotenv import load_dotenv
from supabase import create_client
# Import ALL required components from flask here
from flask import Flask, render_template, jsonify 

# Load environment variables from a .env file
load_dotenv()

# --- Load Environment Variables ---
# NOTE: Ensure your .env file has lines like:
# SUPABASE_URL=your_url_here
# SUPABASE_KEY=your_key_here
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Check and raise an error if secrets are missing
if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError("Supabase URL or Key not found in environment variables. Check your .env file.")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize your Flask app instance
app = Flask(__name__)

@app.route("/test-insert")
def test_insert():
    try:
        result = supabase.table("Users").insert({"full_name": "FlaskTest", "email": "pmuirurri@gmail.com", "password": "kugeria"}).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# A simple root route
@app.route("/")
def home():
    # Make sure you have a 'login.html' file in a 'templates' folder
    return render_template('login.html')

# A route to fetch and display data from a Supabase table
@app.route("/users")
def get_users():
    """
    Example route to fetch data from a 'users' table in Supabase.
    """
    try:
        # Fetch all data from the 'users' table
        response = supabase.table("users").select("*").execute()
        
        # Supabase client returns a specific data structure; check the 'data' key
        if response.data:
            return jsonify(response.data)
        else:
            return jsonify({"error": "No data found or table does not exist."}), 404
            
    except Exception as e:
        # Catch network or database errors
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# This is the standard way to run a Flask app when executing the file directly
if __name__ == "__main__":
    app.run(debug=True)