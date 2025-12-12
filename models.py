# models.py - FINAL version for JSON persistence (NO SQLALCHEMY)

class Item:
    """
    Defines the structure for a media item. 
    Uses 'id' in the constructor, which fixes the TypeError.
    """
    def __init__(self, id, type, title, author, year):
        self.id = id
        self.type = type
        self.title = title
        self.author = author
        self.year = year
        
    def as_dict(self):
        """Returns the item's data as a dictionary, compatible with JSON output."""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "author": self.author,
            "year": self.year
        }