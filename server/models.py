from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define tables using db.Model
class EncryptedData(db.Model):
    __tablename__ = 'encrypted_data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(455), unique=True, nullable=False)  # Unique key identifier
    pin = db.Column(db.String(455), nullable=False)  # Hashed PIN
    encrypted_text = db.Column(db.Text, nullable=True)  # Encrypted text data (nullable)
    encrypted_file = db.Column(db.Text, nullable=True)  # Encrypted file data (nullable)
    type = db.Column(db.Enum('text', 'file', name='data_type'), nullable=False)  # Type of data (text or file)
    expiry_time = db.Column(db.DateTime, nullable=False)  # Expiry timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp

    def __repr__(self):
        return f"<EncryptedData(id={self.id}, key={self.key}, type={self.type}, expiry_time={self.expiry_time})>"

# Export db for use in app.py
__all__ = ['db', 'EncryptedData']
