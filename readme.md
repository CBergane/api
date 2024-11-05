# CRUD API Project with SQLite and JSON Backup

## Beskrivning
Detta projekt är ett CRUD API som byggts med Flask och använder SQLite som den primära databasen för att hantera objekt. API:et tillhandahåller funktionalitet för att skapa, läsa, uppdatera och ta bort poster. Det finns även en funktion för att exportera data från SQLite-databasen till en JSON-fil som säkerhetskopia.

## Funktionalitet
- **Skapa** en ny post (namn och värde).
- **Läsa** alla poster eller en specifik post baserat på ID.
- **Uppdatera** en post baserat på ID.
- **Radera** en post baserat på ID.
- **Exportera** all data från SQLite-databasen till en JSON-fil.

## Installation och uppstart

1. Klona eller ladda ner projektet till din lokala miljö.
2. Navigera till projektmappen i terminalen.
3. Installera beroenden:
    ```bash
    pip install -r requirements.txt
    ```
4. Starta Flask-servern:
    ```bash
    python api_server.py
    ```
5. Öppna klientapplikationen med Tkinter:
    ```bash
    python client_gui.py
    ```

Nu är API:et tillgängligt på `http://127.0.0.1:5000` och klientapplikationen är redo att användas.

## API Endpoints

- `POST /insert` - Skapa en ny post.
- `GET /select_all` - Läs alla poster.
- `GET /select_one/<id>` - Läs en specifik post.
- `PUT /update/<id>` - Uppdatera en post baserat på ID.
- `DELETE /delete/<id>` - Radera en post baserat på ID.
- `POST /export` - Exportera data från SQLite till JSON.

## Noteringar
Export-funktionen (`POST /export`) skapar en JSON-säkerhetskopia från den aktuella datan i SQLite-databasen till en fil (`data.json`).

## Förbättringar
För att förbättra läsbarheten och konsistensen i endpoints kan vissa utvecklare föredra att sätta alla endpoints under `/<action>` (t.ex. `POST /insert`, `DELETE /delete/<id>`). Detta följer standardpraxis men kan också justeras till att använda root (`/`) tillsammans med specifika HTTP-metoder (t.ex. `POST /`, `DELETE /`) beroende på API-designpreferenser. Det är dock standard att använda explicita endpoints som `/delete/<id>` för tydlighet.