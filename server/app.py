from flask import Flask, request, jsonify, send_file, json
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
from b2sdk.v2 import InMemoryAccountInfo, B2Api, UploadSourceBytes
from io import BytesIO
import requests
import base64
from flask_cors import CORS

#load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

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

def initialize_b2():
    """Initialize and authenticate the Backblaze B2 API."""
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", os.getenv("B2_KEY_ID"), os.getenv("B2_APPLICATION_KEY"))
    return b2_api

def upload_to_b2(b2_api, bucket_name, file_data, file_name):
    """Upload encrypted file data to Backblaze B2."""
    bucket = b2_api.get_bucket_by_name(os.getenv("B2_BUCKET_NAME"))
    # Upload the file
    file_info = bucket.upload_bytes(file_data, file_name)
    # Generate the public URL
    file_url = f"https://f000.backblazeb2.com/file/{bucket_name}/{file_name}"
    
    return file_info, file_url

# Function to authorize the B2 account
def authorize_account(key_id, application_key):
    url = "https://api.backblazeb2.com/b2api/v2/b2_authorize_account"
    response = requests.get(url, auth=(key_id, application_key))
    
    if response.status_code == 200:
        data = response.json()

        # print(data)

        return data['authorizationToken'], data['apiUrl'], data['downloadUrl']
    
    else:
        print(f"Error authorizing account: {response.status_code}, {response.text}")
        return None, None, None


# Function to get download authorization token
def get_download_authorization(auth_token, api_url, bucket_id, file_name_prefix="", valid_duration=6000):
    url = f"{api_url}/b2api/v2/b2_get_download_authorization"
    headers = {
        "Authorization": f"{auth_token}"
    }
    payload = {
        "bucketId": bucket_id,
        "fileNamePrefix": file_name_prefix,
        "validDurationInSeconds": valid_duration
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # print(data)
        return data['authorizationToken']
    else:
        print(f"Error getting download authorization: {response.status_code}, {response.text}")
        return None, None

# Function to download the file
def download_file(download_url, authorization_token, file_name, local_path):
    url = f"{download_url}/file/{file_name}"
    headers = {
        "Authorization": f"{authorization_token}"
    }
    
    response = requests.get(url, headers=headers, stream=True)
    
    if response.status_code == 200:
        with open(local_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"File downloaded successfully: {local_path}")
    else:
        print(f"Error downloading file: {response.status_code}, {response.text}")


# Helper function for error responses
def error_response(message):
    return jsonify({'error': message}), 400

@app.route('/encrypt', methods=['POST'])
def encrypt():
    try:
        # Retrieve and validate input data
        pin = request.form.get('pin')
        expiry_time = request.form.get('expiry_time')  # in minutes
        text_data = request.form.get('data')
        file = request.files.get('file')

        if not pin or (not text_data and not file):
            return error_response("Missing required fields: 'pin' and either 'data' or 'file'.")

        # Validate expiry time
        expiry_time = int(expiry_time)
        if expiry_time < 30 or expiry_time > 2880:
            return error_response("Expiry time must be between 30 minutes and 48 hours.")

        if file:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            if file_size > 10 * 1024 * 1024:
                return error_response("File size exceeds the 10MB limit.")
            file.seek(0)

        # Generate Fernet key
        key = Fernet.generate_key()
        cipher = Fernet(key)

        # Encrypt text data
        encrypted_text = cipher.encrypt(text_data.encode()) if text_data else None

        # Encrypt file data and upload to Backblaze
        encrypted_file_name = None
        if file:
            file_data = file.read()
            encrypted_file_data = cipher.encrypt(file_data)

            # Backblaze upload
            b2_api = initialize_b2()
            file_name = f"encrypted_{datetime.utcnow().isoformat()}.bin"

            # Upload the file and get its URL
            _, encrypted_file_url = upload_to_b2(b2_api, os.getenv("B2_BUCKET_NAME"), encrypted_file_data, file_name)
            encrypted_file_name = file_name


        hashed_pin = hashlib.sha256(pin.encode()).hexdigest()

        # Save metadata to database
        entry = EncryptedData(
            key=key.decode(),
            pin=hashed_pin,
            encrypted_text=encrypted_text.decode() if encrypted_text else None,
            encrypted_file=encrypted_file_name if encrypted_file_name else None,
            expiry_time=datetime.utcnow() + timedelta(seconds=expiry_time * 60),
            type='text' if encrypted_text else 'file'
        )
        db.session.add(entry)
        db.session.commit()

        # Response
        response = {
            "message": "Data encrypted and uploaded successfully.",
            "key": key.decode(),
            # "file_url": encrypted_file_url,
            "expiry_time": expiry_time
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
        # Step 1: Retrieve and validate input
        key = request.json.get('key')
        pin = request.json.get('pin')

        if not key or not pin:
            return error_response("Missing 'key' or 'pin' in the request.")

        # Step 2: Query the database
        record = EncryptedData.query.filter_by(key=key).first()
        if not record:
            return error_response("Invalid key or pin. Please try again.")

        # Step 3: Validate the pin
        hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
        if hashed_pin != record.pin:
            return error_response("Invalid key or pin. Please try again.")

        # Step 4: Check expiry
        if datetime.utcnow() > record.expiry_time:
            return error_response("The content has expired and cannot be decrypted.")

        # Step 5: Decrypt text content
        decrypted_text = None
        if record.encrypted_text:
            cipher = Fernet(record.key.encode())
            decrypted_text = cipher.decrypt(record.encrypted_text.encode()).decode()

        # Step 6: Handle file content
        decrypted_file = None
        if record.encrypted_file:
            try:
                # Authorize the B2 account
                auth_token, api_url, download_url = authorize_account(
                    os.getenv('B2_KEY_ID'), os.getenv('B2_APPLICATION_KEY')
                )
                
                if not auth_token or not download_url:
                    raise Exception("Failed to authorize Backblaze B2 account.")

                # Get the download authorization token
                download_auth_token = get_download_authorization(
                    auth_token,
                    api_url,
                    os.getenv('B2_BUCKET_ID'),
                    record.encrypted_file,
                )
                
                if not download_auth_token:
                    raise Exception("Failed to get download authorization token.")

                # Construct the full download URL
                file_url = f"{download_url}/file/{os.getenv('B2_BUCKET_NAME')}/{record.encrypted_file}?Authorization={download_auth_token}"

                # Download the file to an in-memory stream (BytesIO)
                file_stream = BytesIO()
                try:
                    response = requests.get(file_url, headers={"Authorization": f"Bearer {download_auth_token}"}, stream=True)
                    
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=8192):
                            file_stream.write(chunk)
                        file_stream.seek(0)  # Reset stream pointer
                        print("File downloaded successfully.")
                    else:
                        print(f"Error downloading file: {response.status_code}, {response.text}")
                        raise Exception("Failed to download the file.")

                except Exception as download_error:
                    print(f"Error downloading file: {download_error}")
                    raise

                # Decrypt the downloaded file
                try:
                    cipher = Fernet(record.key.encode())
                    decrypted_file = cipher.decrypt(file_stream.read())
                    print("File decrypted successfully.")
                except Exception as decryption_error:
                    print(f"Error decrypting file: {decryption_error}")
                    raise

            except Exception as e:
                return error_response(f"An error occurred while downloading or decrypting the file: {str(e)}")



        # Step 7: Calculate remaining time
        time_remaining = (record.expiry_time - datetime.utcnow()).total_seconds() / 3600

        # Step 8: Construct response
        if decrypted_file and decrypted_text:
            # Include both text and file in the JSON response
            response = {
                "decrypted_text": decrypted_text,
                "expiry_time_status": f"{time_remaining:.2f} hours remaining before expiry.",
                "decrypted_file": base64.b64encode(decrypted_file).decode("utf-8"),  # Convert binary to base64 string
            }
            return jsonify(response)

        elif decrypted_file:
            # Include only the file and expiry time in the JSON response
            response = {
                "expiry_time_status": f"{time_remaining:.2f} hours remaining before expiry.",
                "decrypted_file": base64.b64encode(decrypted_file).decode("utf-8"),  # Convert binary to base64 string
            }
            return jsonify(response)

        else:
            # Include only the text and expiry time in the JSON response
            response = {
                "decrypted_text": decrypted_text,
                "expiry_time_status": f"{time_remaining:.2f} hours remaining before expiry."
            }
            return jsonify(response)


    except Exception as e:
        return error_response(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
