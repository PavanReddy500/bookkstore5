from flask import Flask, request, jsonify
from flask_cors import CORS
# Ensure this line correctly imports the Item class from the new models.py
from models import Item 
import os
import json
import operator 

# --- FILE PERSISTENCE CONFIGURATION (MANDATORY CHANGE) ---
BASE_DIR = os.path.dirname(__file__)
DATA_FILE_PATH = os.path.join(BASE_DIR, 'library_data.json')
# --- END PERSISTENCE CONFIGURATION ---

app = Flask(__name__)
CORS(app)

media_items = []
next_item_id = 1


def load_data():
    """Loads media data from the JSON file into memory at startup."""
    global media_items, next_item_id
    media_items = []
    
    # Check 1: If the file does not exist, create it with samples
    if not os.path.exists(DATA_FILE_PATH):
        print(f"Creating initial data file: {DATA_FILE_PATH}")
        # FIX: Ensure all sample creation uses 'id=' and not 'item_id='
        samples = [
            Item(id=1, type='book', title='The Pragmatic Engineer', author='John Doe', year=2020),
            Item(id=2, type='magazine', title='Science Monthly', author='Editorial Team', year=2024),
            Item(id=3, type='film', title='Space Adventure', author='Jane Director', year=2019),
            Item(id=4, type='book', title='A Brief History of Time', author='Stephen Hawking', year=1988),
            Item(id=5, type='book', title='Zen and the Art of Motorcycle Maintenance', author='Robert Pirsig', year=1974),
        ]
        media_items = samples
        save_data()
        next_item_id = len(media_items) + 1
        return

    try:
        # Check 2: Load data from the existing file
        with open(DATA_FILE_PATH, 'r') as f:
            data = json.load(f)
            
        for item_data in data:
            media_items.append(Item(
                id=item_data.get('id'), # FIX: Ensure constructor call uses 'id'
                type=item_data.get('type'), 
                title=item_data.get('title'), 
                author=item_data.get('author'), 
                year=item_data.get('year')
            ))
            
        if media_items:
            next_item_id = max(item.id for item in media_items) + 1
        else:
            next_item_id = 1
            
    except Exception as e:
        print(f"Error loading JSON data: {e}. Starting with empty data.")
        media_items = []
        next_item_id = 1
        

def save_data():
    """Writes the current data list back to the JSON file for persistence."""
    try:
        data_to_save = [item.as_dict() for item in media_items]
        with open(DATA_FILE_PATH, 'w') as f:
            json.dump(data_to_save, f, indent=4) 
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to save JSON data: {e}") 


# --------------------------------------------------------------------------------
# API ROUTES 
# --------------------------------------------------------------------------------

@app.route('/items', methods=['GET'])
def list_items():
    q = request.args.get('q', '').strip().lower()
    t = request.args.get('type', '').strip().lower()
    
    filtered_items = media_items
    
    if t in ('book', 'magazine', 'film'):
        filtered_items = [item for item in filtered_items if item.type == t]
        
    if q:
        filtered_items = [
            item for item in filtered_items 
            if q in item.title.lower() or q in item.author.lower()
        ]
    
    filtered_items.sort(key=operator.attrgetter('title'))
    
    items_as_dict = [i.as_dict() for i in filtered_items]
    
    return jsonify(items_as_dict)


@app.route('/items', methods=['POST'])
def create_item():
    global next_item_id
    data = request.get_json() or {}
    type_ = data.get('type')
    title = data.get('title')
    author = data.get('author')
    year = data.get('year')
    
    if not type_ or not title:
        return jsonify({'error': 'type and title are required'}), 400
    if type_.lower() not in ('book', 'magazine', 'film'):
        return jsonify({'error': 'invalid type'}), 400
        
    new_item = Item(
        id=next_item_id, # FIX: Ensure constructor call uses 'id'
        type=type_.lower(), 
        title=title.strip(), 
        author=(author or '').strip(), 
        year=year
    )
    
    media_items.append(new_item)
    next_item_id += 1 
    
    save_data() 
    
    return jsonify(new_item.as_dict()), 201


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global media_items
    
    initial_count = len(media_items)
    media_items = [item for item in media_items if item.id != item_id]
    
    if len(media_items) == initial_count:
        return jsonify({'error': 'not found'}), 404
        
    save_data() 
    
    return jsonify({'ok': True})


if __name__ == '__main__':
    load_data() 
    app.run(debug=True, port=5000)