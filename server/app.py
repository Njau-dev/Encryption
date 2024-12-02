from flask import Flask, request, jsonify, send_file
from cryptography.fernet import Fernet
import pandas as pd
from faker import Faker
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import hashlib
from models import EncryptedData, db
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

#load environment variables
load_dotenv()

app = Flask(__name__)

# Load environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Example route for testing
@app.route('/')
def home():
    return "Database connection successfully configured!"


# Initialize Faker
fake = Faker()

# Helper function for error responses
def error_response(message):
    return jsonify({'error': message}), 400

# Key Generation Route
@app.route('/generate-key', methods=['GET'])
def generate_key():
    try:
        key = Fernet.generate_key()
        return jsonify({'key': key.decode()})
    except Exception as e:
        return error_response(str(e))

@app.route('/encrypt', methods=['POST'])
def encrypt():
    try:
        # Retrieve and validate input data
        pin = request.json.get('pin')
        expiry_time = request.json.get('expiry_time')  # in minutes
        text_data = request.json.get('data')
        file = request.files.get('file')

        if not pin or (not text_data and not file):
            return error_response("Missing required fields: 'pin' and either 'data' or 'file'.")

        # Validate expiry time
        try:
            expiry_time = int(expiry_time)
            if expiry_time < 30 or expiry_time > 2880:  # 30 minutes to 48 hours
                return error_response("Expiry time must be between 30 minutes and 48 hours.")
        except ValueError:
            return error_response("Invalid expiry time format. Please provide time in minutes.")

        if file:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()  # Get file size in bytes
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return error_response("File size exceeds the 10MB limit.")
            file.seek(0)  # Reset file pointer for reading

        # Generate Fernet key
        key = Fernet.generate_key()
        cipher = Fernet(key)

        # Encrypt text data
        encrypted_text = cipher.encrypt(text_data.encode()) if text_data else None

        # Encrypt file data
        encrypted_file_data = None
        if file:
            file_data = file.read()
            encrypted_file_data = cipher.encrypt(file_data)

        # Hash the pin
        hashed_pin = hashlib.sha256(pin.encode()).hexdigest()

        # Format expiry time as HH:MM:SS
        expiry_seconds = expiry_time * 60
        expiry_time_formatted = str(pd.to_datetime(expiry_seconds, unit='s').time())

        # Save to database
        entry = EncryptedData(
            key=key.decode(),
            pin=hashed_pin,
            encrypted_text=encrypted_text.decode() if encrypted_text else None,
            encrypted_file=encrypted_file_data if encrypted_file_data else None,
            expiry_time=datetime.utcnow() + timedelta(seconds=expiry_seconds),
            type='text' if encrypted_text else 'file'
        )
        db.session.add(entry)
        db.session.commit()

        # Response
        response = {
            "message": "Data encrypted successfully.",
            "key": key.decode(),
            "expiry_time": expiry_time_formatted
        }
        return jsonify(response), 201

    except SQLAlchemyError as e:
        return error_response(f"Database error: {str(e)}")
    except Exception as e:
        return error_response(f"An unexpected error occurred: {str(e)}")


# Decrypt Route
@app.route('/decrypt', methods=['POST'])
def decrypt():
    try:
        key = request.json.get('key')
        encrypted_data = request.json.get('encrypted_data')
        
        if not key or not encrypted_data:
            return error_response("Missing 'key' or 'encrypted_data' in request.")
        
        cipher = Fernet(key.encode())
        decrypted_data = cipher.decrypt(encrypted_data.encode())
        return jsonify({'decrypted_data': decrypted_data.decode()})
    except Exception as e:
        return error_response(str(e))

# Anonymize Route
@app.route('/anonymize', methods=['POST'])
def anonymize():
    try:
        data = request.json.get('data')
        
        if not data:
            return error_response("Missing 'data' in request.")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Anonymize the 'Email' column using Faker
        df['Email'] = df['Email'].apply(lambda x: fake.email())

        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return error_response(str(e))



# Decrypt File Route
@app.route('/decrypt-file', methods=['POST'])
def decrypt_file():
    try:
        if 'file' not in request.files or 'key' not in request.form:
            return error_response("Missing 'file' or 'key' in request.")

        file = request.files['file']
        key = request.form['key']
        cipher = Fernet(key.encode())
        
        # Read and decrypt file content
        file_data = file.read()
        decrypted_data = cipher.decrypt(file_data)

        # Save decrypted file
        decrypted_file_path = 'decrypted_file.dat'
        with open(decrypted_file_path, 'wb') as f:
            f.write(decrypted_data)

        return send_file(decrypted_file_path, as_attachment=True)
    except Exception as e:
        return error_response(str(e))

if __name__ == '__main__':
    app.run(debug=True)
