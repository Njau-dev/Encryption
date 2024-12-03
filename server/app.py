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

        print(f"Using bucket: {os.getenv('B2_BUCKET_NAME')}")

        # Step 6: Handle file content
        decrypted_file = None
        if record.encrypted_file:
            try:
                info = InMemoryAccountInfo()
                b2_api = B2Api(info)
                b2_api.authorize_account("production", os.getenv('B2_KEY_ID'), os.getenv('B2_APPLICATION_KEY'))

                bucket_name = os.getenv('B2_BUCKET_NAME')
                bucket = b2_api.get_bucket_by_name(bucket_name)

                print(f"Attempting to download file: {record.encrypted_file}")

                file_version = bucket.get_file_info_by_name(record.encrypted_file)
                file_id = file_version.id_

                file_stream = BytesIO()

                # Download the file content to the in-memory stream
                try:
                    # bucket.download_file_by_name(record.encrypted_file, file_stream)
                    bucket.download_file_by_id(file_id, file_stream)


                    print("File downloaded successfully.")
                except Exception as download_error:
                    print(f"Error downloading file: {download_error}")
                    raise


                # Ensure the stream is at the beginning after writing
                file_stream.seek(0, os.SEEK_END)

                print(f"Downloaded file size in stream: {file_stream.tell()} bytes")


                if file_stream.tell() == 0:
                    raise Exception("Downloaded file is empty. Cannot decrypt.")

                # Decrypt the file content
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
        response = {
            "decrypted_text": decrypted_text,
            "expiry_time_status": f"{time_remaining:.2f} hours remaining before expiry."
        }

        if decrypted_file:
            # Serve the decrypted file as a downloadable attachment
            file_stream = BytesIO(decrypted_file)
            file_stream.seek(0)
            return send_file(
                file_stream,
                as_attachment=True,
                download_name="decrypted_file",
                mimetype="application/octet-stream"
            )

        return jsonify(response)

    except Exception as e:
        return error_response(f"An unexpected error occurred: {str(e)}")


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
