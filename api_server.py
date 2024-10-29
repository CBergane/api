from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'


def load_data():
    """Laddar data från JSON-filen. Om filen saknas, returnera en tom struktur."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {"objects": [], "latest_id": 0}


def save_data(data):
    """Sparar data till JSON-filen."""
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


@app.route('/select_all', methods=['GET'])
def select_all():
    """Hämtar alla objekt."""
    data = load_data()
    return jsonify(data["objects"])


@app.route('/select_one/<int:id>', methods=['GET'])
def select_one(id):
    """Hämtar ett specifikt objekt baserat på ID."""
    data = load_data()
    for obj in data["objects"]:
        if obj["id"] == id:
            return jsonify(obj)
    return jsonify({"error": "Object not found"}), 404


@app.route('/insert', methods=['POST'])
def insert():
    """Lägger till ett nytt objekt med ett unikt, inkrementerande ID."""
    data = load_data()
    
    # Skapa nytt ID genom att öka latest_id
    new_id = data["latest_id"] + 1
    new_object = {"id": new_id, "name": request.json["name"], "value": request.json["value"]}
    
    # Lägg till det nya objektet och uppdatera latest_id
    data["objects"].append(new_object)
    data["latest_id"] = new_id
    
    # Spara tillbaka till JSON-filen
    save_data(data)
    return jsonify(new_object), 201


@app.route('/update/<int:id>', methods=['PUT'])
def update(id):
    """Uppdaterar ett befintligt objekt baserat på ID."""
    data = load_data()
    updated_obj = request.json
    for obj in data["objects"]:
        if obj["id"] == id:
            obj.update(updated_obj)
            save_data(data)
            return jsonify(obj)
    return jsonify({"error": "Object not found"}), 404


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    """Tar bort ett objekt baserat på ID och returnerar information om det raderade objektet."""
    data = load_data()
    for obj in data["objects"]:
        if obj["id"] == id:
            deleted_obj = obj
            data["objects"].remove(obj)
            save_data(data)
            return jsonify({"message": "Object deleted successfully", "deleted_object": deleted_obj}), 200
    return jsonify({"error": "Object not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
