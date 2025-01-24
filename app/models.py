from app_db import db

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    valor = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<Registro {self.nombre}>"
