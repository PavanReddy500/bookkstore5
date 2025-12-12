from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    
    def as_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'author': self.author,
            'year': self.year
        }
