from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 1. CREATE - Add a new item
@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Missing required fields (name, price)"}), 400
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, description, price) VALUES (?, ?, ?)",
                   (data['name'], data.get('description', ''), data['price']))
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    
    return jsonify({"message": "Item created successfully", "id": item_id}), 201

# 2. READ - Get all items
@app.route('/items', methods=['GET'])
def get_items():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()
    
    items = [{"id": r[0], "name": r[1], "description": r[2], "price": r[3]} for r in rows]
    return jsonify(items), 200

# 3. READ - Get single item by ID
@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    r = cursor.fetchone()
    conn.close()
    
    if not r:
        return jsonify({"error": "Item not found"}), 404
        
    item = {"id": r[0], "name": r[1], "description": r[2], "price": r[3]}
    return jsonify(item), 200

# 4. UPDATE - Modify an item
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Item not found"}), 404
        
    cursor.execute("UPDATE items SET name = ?, description = ?, price = ? WHERE id = ?",
                   (data.get('name'), data.get('description'), data.get('price'), item_id))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Item updated successfully"}), 200

# 5. DELETE - Remove an item
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Item not found"}), 404
        
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Item deleted successfully"}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
  
