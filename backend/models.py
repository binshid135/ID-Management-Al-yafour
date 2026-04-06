from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class IDDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.String(50), nullable=False)  # 'id1' or 'id2'
    full_name = db.Column(db.String(100))
    document_number = db.Column(db.String(50))  # Removed unique=True
    date_of_birth = db.Column(db.String(20))
    nationality = db.Column(db.String(50))
    expiry_date = db.Column(db.String(20))
    extracted_text = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_type': self.document_type,
            'full_name': self.full_name,
            'document_number': self.document_number,
            'date_of_birth': self.date_of_birth,
            'nationality': self.nationality,
            'expiry_date': self.expiry_date,
            'extracted_text': self.extracted_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }