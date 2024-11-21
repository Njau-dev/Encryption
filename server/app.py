from flask import Flask, request, jsonify, send_file
from cryptography.fernet import Fernet
import pandas as pd
from faker import Faker
import os

app = Flask(__name__)

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

# Encrypt Route
@app.route('/encrypt', methods=['POST'])
def encrypt():
    try:
        key = request.json.get('key')
        data = request.json.get('data')
        
        if not key or not data:
            return error_response("Missing 'key' or 'data' in request.")
        
        cipher = Fernet(key.encode())
        encrypted_data = cipher.encrypt(data.encode())
        return jsonify({'encrypted_data': encrypted_data.decode()})
    except Exception as e:
        return error_response(str(e))

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

# Encrypt File Route
@app.route('/encrypt-file', methods=['POST'])
def encrypt_file():
    try:
        if 'file' not in request.files or 'key' not in request.form:
            return error_response("Missing 'file' or 'key' in request.")

        file = request.files['file']
        key = request.form['key']
        cipher = Fernet(key.encode())
        
        # Read and encrypt file content
        file_data = file.read()
        encrypted_data = cipher.encrypt(file_data)

        # Save encrypted file
        encrypted_file_path = 'encrypted_file.dat'
        with open(encrypted_file_path, 'wb') as f:
            f.write(encrypted_data)

        return send_file(encrypted_file_path, as_attachment=True)
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
