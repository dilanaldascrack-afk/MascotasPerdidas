from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)
    # Basic info
    name = db.Column(db.String(100), nullable=True)  # puede ser desconocido
    species = db.Column(db.String(50), nullable=False)  # perro, gato, otro
    breed = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(100), nullable=True)
    size = db.Column(db.String(20), nullable=True)  # pequeño, mediano, grande
    age_estimate = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.String(20), nullable=True)

    # Status
    status = db.Column(db.String(20), nullable=False, default="perdido")  # perdido / encontrado

    # Location
    city = db.Column(db.String(100), nullable=False)
    neighborhood = db.Column(db.String(100), nullable=True)
    last_seen_address = db.Column(db.String(255), nullable=True)
    last_seen_date = db.Column(db.Date, nullable=False)

    # Description
    description = db.Column(db.Text, nullable=True)
    has_collar = db.Column(db.Boolean, default=False)
    has_chip = db.Column(db.Boolean, default=False)

    # Contact
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(30), nullable=False)
    contact_email = db.Column(db.String(150), nullable=True)
    reward = db.Column(db.String(100), nullable=True)

    # Photo (Base64 stored directly in DB)
    photo_data = db.Column(db.Text, nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "color": self.color,
            "size": self.size,
            "status": self.status,
            "city": self.city,
            "neighborhood": self.neighborhood,
            "last_seen_date": self.last_seen_date.isoformat() if self.last_seen_date else None,
            "description": self.description,
            "contact_name": self.contact_name,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "reward": self.reward,
            "photo_data": self.photo_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_resolved": self.is_resolved,
        }
