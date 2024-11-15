from flask import Flask, request, jsonify
import pyreadstat
import os
import uuid
from dotenv import load_dotenv
import pandas as pd
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Fetch UUID_SECRET from environment variables
UUID_SECRET = os.getenv('UUID_SECRET')

# Function to check UUID in the request headers
def authenticate(request):
    # Retrieve the UUID from the request headers
    user_uuid = request.headers.get('USER-UUID')
    
    if user_uuid != UUID_SECRET:
        return False  # If the UUID doesn't match, authentication fails
    return True

@app.route('/get_headers', methods=['POST'])
def get_headers():
    # Authenticate the request using the UUID
    if not authenticate(request):
        return jsonify({"error": "Unauthorized. Invalid UUID."}), 401

    # Check if the file is part of the request
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    
    # Check the file extension and process accordingly
    try:
        if file.filename.endswith('.sav'):
            # Handle .sav file
            temp_file_path = os.path.join("temp.sav")
            file.save(temp_file_path)

            # Read the .sav file to extract headers
            df, meta = pyreadstat.read_sav(temp_file_path)
            headers = list(df.columns)

            # Delete the temporary file after reading
            os.remove(temp_file_path)

        elif file.filename.endswith('.xlsx'):
            # Handle .xlsx file
            temp_file_path = os.path.join("temp.xlsx")
            file.save(temp_file_path)

            # Read the .xlsx file to extract headers using pandas
            df = pd.read_excel(temp_file_path)
            headers = list(df.columns)

            # Delete the temporary file after reading
            os.remove(temp_file_path)

        else:
            return jsonify({"error": "File format not supported. Please upload a .sav or .xlsx file."}), 400

        # Return the headers in JSON format
        return jsonify({"headers": headers})
    
    except Exception as e:
        # Handle any errors that occur
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)

