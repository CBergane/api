from flask import Flask, jsonify, request
import json
import sqlite3

app = Flask(__name__)  # Skapa en Flask-applikation

DATA_FILE = 'data.json'  # Filnamnet för JSON-filen som lagrar data
DB_FILE = 'database.db'  # Filnamnet för SQLite-databasen


def init_db():
    """Initierar SQLite-databasen och skapar tabellen om den inte redan finns."""
    conn = sqlite3.connect(DB_FILE)  # Anslut till databasen
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS objects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        value TEXT NOT NULL
                      )''')  # Skapa tabell om den inte existerar
    conn.commit()
    conn.close()  # Stäng anslutningen


def load_data_from_db():
    """Hämtar alla data från SQLite-databasen."""
    conn = sqlite3.connect(DB_FILE)  # Anslut till databasen
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM objects")  # Hämta alla rader från tabellen
    rows = cursor.fetchall()
    conn.close()  # Stäng anslutningen
    return [{"id": row[0], "name": row[1], "value": row[2]} for row in rows]  # Returnera data som en lista av dictionaries


def save_data_to_json():
    """Sparar all data från SQLite-databasen till JSON-filen som en säkerhetskopia."""
    data = {"objects": load_data_from_db()}  # Hämta alla data och skapa en dictionary
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)  # Skriv data till JSON-filen med indentering för läsbarhet


@app.route('/select_all', methods=['GET'])
def select_all():
    """Hämtar alla objekt från databasen."""
    data = load_data_from_db()  # Hämta alla objekt från databasen
    return jsonify(data)  # Returnera objekt i JSON-format


@app.route('/select_one/<int:id>', methods=['GET'])
def select_one(id):
    """Hämtar ett specifikt objekt baserat på ID från databasen."""
    conn = sqlite3.connect(DB_FILE)  # Anslut till databasen
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM objects WHERE id = ?", (id,))  # Hämta objektet med angivet ID
    row = cursor.fetchone()
    conn.close()  # Stäng anslutningen

    if row:
        # Om objektet finns, returnera det i JSON-format
        return jsonify({"id": row[0], "name": row[1], "value": row[2]})
    return jsonify({"error": "Object not found"}), 404  # Returnera felmeddelande om objektet inte hittades


@app.route('/insert', methods=['POST'])
def insert():
    """Lägger till ett nytt objekt i databasen."""
    name = request.json["name"]  # Hämta namn från begäran
    value = request.json["value"]  # Hämta värde från begäran

    conn = sqlite3.connect(DB_FILE)  # Anslut till databasen
    cursor = conn.cursor()
    cursor.execute("INSERT INTO objects (name, value) VALUES (?, ?)", (name, value))  # Lägg till nytt objekt i databasen
    conn.commit()
    new_id = cursor.lastrowid  # Hämta ID för det nya objektet
    conn.close()  # Stäng anslutningen

    new_object = {"id": new_id, "name": name, "value": value}  # Skapa en dictionary för det nya objektet
    return jsonify(new_object), 201  # Returnera det nya objektet med statuskod 201 (Created)


@app.route('/update/<int:id>', methods=['PUT'])
def update(id):
    """Uppdaterar ett befintligt objekt baserat på ID i databasen."""
    updated_data = request.json  # Hämta uppdaterad data från klienten
    name = updated_data.get("name")
    value = updated_data.get("value")

    conn = sqlite3.connect(DB_FILE)  # Anslut till databasen
    cursor = conn.cursor()

    # Hämta det befintliga objektet från databasen
    cursor.execute("SELECT name, value FROM objects WHERE id = ?", (id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Ingen användare hittades"}), 404

    # Använd befintliga värden om input är tom
    current_name, current_value = row
    name = name if name else current_name
    value = value if value else current_value

    try:
        # Uppdatera objektet i databasen
        cursor.execute(
            "UPDATE objects SET name = ?, value = ? WHERE id = ?",
            (name, value, id),
        )
        conn.commit()
        rows_updated = cursor.rowcount  # Kontrollera hur många rader som uppdaterades
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400  # Hantera SQLite-specifika fel
    finally:
        conn.close()  # Stäng anslutningen till databasen

    if rows_updated > 0:
        return jsonify({"id": id, "name": name, "value": value}), 200
    return jsonify({"error": "Ingen användare hittades"}), 404


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    """Tar bort ett objekt baserat på ID i databasen och JSON-filen."""
    conn = sqlite3.connect(DB_FILE)  # Anslut till databasen
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM objects WHERE id = ?", (id,))  # Hämta objektet som ska raderas
    row = cursor.fetchone()
    if not row:
        # Om objektet inte finns, returnera felmeddelande
        return jsonify({"error": "Object not found"}), 404

    cursor.execute("DELETE FROM objects WHERE id = ?", (id,))  # Ta bort objektet från databasen
    conn.commit()
    conn.close()  # Stäng anslutningen

    deleted_object = {"id": row[0], "name": row[1], "value": row[2]}  # Spara raderad objektdata för att inkludera i svaret
    return jsonify({"message": "Object deleted successfully", "deleted_object": deleted_object}), 200  # Returnera bekräftelse och raderad data


@app.route('/export', methods=['POST'])
def export_data():
    """Exporterar data från SQLite-databasen till JSON-filen."""
    save_data_to_json()  # Kör funktionen för att spara databasen till JSON
    return jsonify({"message": "Data exported to JSON successfully"}), 200  # Returnera bekräftelsemeddelande


if __name__ == "__main__":
    init_db()  # Initiera databasen om den inte redan finns
    app.run()  # Starta Flask-applikationen
