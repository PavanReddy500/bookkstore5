from flask import Flask, request, jsonify, abort
from flask_cors import CORS
# This line requires a separate file named 'models.py'
from models import db, Item 
import os


BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'items.db')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)


db.init_app(app)


@app.before_request
def create_tables():
    """Initializes the database and adds sample data if empty."""
    with app.app_context():
        if not hasattr(app, 'initialized'):
            db.create_all()
            app.initialized = True
            
            # add some sample data if empty
            if Item.query.count() == 0:
                samples = [
                    Item(type='book', title='The Pragmatic Engineer', author='John Doe', year=2020),
                    Item(type='magazine', title='Science Monthly', author='Editorial Team', year=2024),
                    Item(type='film', title='Space Adventure', author='Jane Director', year=2019),
                    Item(type='book', title='A Brief History of Time', author='Stephen Hawking', year=1988),
                    Item(type='book', title='Zen and the Art of Motorcycle Maintenance', author='Robert Pirsig', year=1974),
                ]
                db.session.bulk_save_objects(samples)
                db.session.commit()


@app.route('/items', methods=['GET'])
def list_items():
    """Handles searching, filtering, and listing all items."""
    q = request.args.get('q', '').strip()
    t = request.args.get('type', '').strip().lower()
    query = Item.query
    
    # Filter by type
    if t in ('book', 'magazine', 'film'):
        query = query.filter_by(type=t)
        
    # Filter by search query (title or author)
    if q:
        like = f"%{q}%"
        query = query.filter((Item.title.ilike(like)) | (Item.author.ilike(like)))
    
    # --- UPDATED: Sort alphabetically by title (A-Z) ---
    items = [i.as_dict() for i in query.order_by(Item.title.asc()).all()]
    # ----------------------------------------------------
    
    return jsonify(items)


@app.route('/items', methods=['POST'])
def create_item():
    """Adds a new item to the inventory."""
    data = request.get_json() or {}
    type_ = data.get('type')
    title = data.get('title')
    author = data.get('author')
    year = data.get('year')
    
    if not type_ or not title:
        return jsonify({'error': 'type and title are required'}), 400
    if type_.lower() not in ('book', 'magazine', 'film'):
        return jsonify({'error': 'invalid type'}), 400
        
    item = Item(type=type_.lower(), title=title.strip(), author=(author or '').strip(), year=year)
    db.session.add(item)
    db.session.commit()
    return jsonify(item.as_dict()), 201


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Deletes an item by ID."""
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'not found'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'ok': True})


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True, port=5000)