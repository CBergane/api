from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)  # Skapa en Flask-applikation

DATA_FILE = 'data.json'  # Filnamnet för JSON-filen som lagrar objektdata


def load_data():
    """Laddar data från JSON-filen. Om filen saknas, returnera en tom struktur."""
    if os.path.exists(DATA_FILE):  # Kontrollera om filen finns
        with open(DATA_FILE, 'r') as file:
            return json.load(file)  # Läs in data från filen om den finns
    return {"objects": [], "latest_id": 0}  # Returnera en tom databasstruktur om filen inte finns


def save_data(data):
    """Sparar data till JSON-filen."""
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)  # Skriv data till filen med indentering för bättre läsbarhet


@app.route('/select_all', methods=['GET'])
def select_all():
    """Hämtar alla objekt."""
    data = load_data()  # Ladda all data från filen
    return jsonify(data["objects"])  # Returnera alla objekt i JSON-format


@app.route('/select_one/<int:id>', methods=['GET'])
def select_one(id):
    """Hämtar ett specifikt objekt baserat på ID."""
    data = load_data()  # Ladda all data från filen
    for obj in data["objects"]:
        if obj["id"] == id:  # Kontrollera om objektets ID matchar det begärda ID:t
            return jsonify(obj)  # Returnera det matchande objektet i JSON-format
    return jsonify({"error": "Object not found"}), 404  # Returnera felmeddelande om objektet inte hittades


@app.route('/insert', methods=['POST'])
def insert():
    """Lägger till ett nytt objekt med ett unikt, inkrementerande ID."""
    data = load_data()  # Ladda all data från filen
    
    # Skapa ett nytt ID genom att öka latest_id med 1
    new_id = data["latest_id"] + 1
    # Skapa det nya objektet med data från POST-begäran och nytt ID
    new_object = {"id": new_id, "name": request.json["name"], "value": request.json["value"]}
    
    # Lägg till det nya objektet till listan och uppdatera latest_id
    data["objects"].append(new_object)
    data["latest_id"] = new_id
    
    save_data(data)  # Spara den uppdaterade datan tillbaka till filen
    return jsonify(new_object), 201  # Returnera det nya objektet och HTTP-statuskod 201 (Created)


@app.route('/update/<int:id>', methods=['PUT'])
def update(id):
    """Uppdaterar ett befintligt objekt baserat på ID."""
    data = load_data()  # Ladda all data från filen
    updated_obj = request.json  # Hämta data från PUT-begäran som innehåller uppdateringar
    
    for obj in data["objects"]:
        if obj["id"] == id:  # Kontrollera om objektets ID matchar det begärda ID:t
            obj.update(updated_obj)  # Uppdatera objektet med nya värden
            save_data(data)  # Spara den uppdaterade datan tillbaka till filen
            return jsonify(obj)  # Returnera det uppdaterade objektet i JSON-format
    
    return jsonify({"error": "Object not found"}), 404  # Returnera felmeddelande om objektet inte hittades


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    """Tar bort ett objekt baserat på ID och returnerar information om det raderade objektet."""
    data = load_data()  # Ladda all data från filen
    
    for obj in data["objects"]:
        if obj["id"] == id:  # Kontrollera om objektets ID matchar det begärda ID:t
            deleted_obj = obj  # Spara det raderade objektet för att inkludera i svaret
            data["objects"].remove(obj)  # Ta bort objektet från listan
            save_data(data)  # Spara den uppdaterade datan tillbaka till filen
            return jsonify({"message": "Object deleted successfully", "deleted_object": deleted_obj}), 200  # Returnera bekräftelsemeddelande och det raderade objektet
    
    return jsonify({"error": "Object not found"}), 404  # Returnera felmeddelande om objektet inte hittades


if __name__ == "__main__":
    app.run()  # Starta Flask-applikationen i debug-läge
