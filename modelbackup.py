from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define the Item class (your database table)
class Item(db.Model):
    id = Column(Integer, primary_key=True)
    type = Column(String(80), nullable=False)
    title = Column(String(120), nullable=False)
    author = Column(String(120), nullable=True)
    year = Column(Integer, nullable=True)

    def as_dict(self):
        # Helper to convert object to a dictionary for JSON output
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'author': self.author,
            'year': self.year
        }