import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk, ImageDraw
import requests
import os

class APIClientApp:
    def __init__(self, root):
        """Initierar huvudfönstret och layouten för applikationen."""
        self.root = root
        self.root.title("API Client - Main Menu")
        
        # Skapa en topppanel för att hålla ikonen och huvudmenyn
        top_frame = ttk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=10)

        # Ladda och bearbeta ikonen om den finns
        icon_path = "api.png"
        if os.path.exists(icon_path):
            original_icon = Image.open(icon_path).convert("RGBA")
            resized_icon = original_icon.resize((50, 50), Image.LANCZOS)

            # Skapa en cirkelmask för ikonen för att ge den en rund form
            mask = Image.new("L", (50, 50), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 50, 50), fill=255)

            # Tillämpa masken och skapa en cirkulär ikon
            circular_icon = Image.new("RGBA", (50, 50))
            circular_icon.paste(resized_icon, (0, 0), mask=mask)
            self.icon_image = ImageTk.PhotoImage(circular_icon)

            # Lägg till ikonen i top_frame
            icon_label = tk.Label(top_frame, image=self.icon_image)
            icon_label.pack(side="left", padx=5)
        else:
            print("Ikonfilen api.png hittades inte")
        
        # Skapa ett PanedWindow för layout
        paned_window = ttk.PanedWindow(root, orient="horizontal")
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Vänster sektion - Huvudmenyn
        menu_frame = ttk.LabelFrame(paned_window, text="Huvud Meny", padding="10 10 10 10")
        paned_window.add(menu_frame, weight=1)

        # Lägg till knappar för CRUD-funktioner
        button_width = 20
        ttk.Button(menu_frame, text="Lägg till ny användare", command=self.add_new_user, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Lista alla användare", command=self.list_all_users, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Visa användare med ID", command=self.show_user_by_id, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Updatera användare", command=self.update_user, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Ta bort användare", command=self.delete_user, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Exportera till JSON", command=self.export_to_json, width=button_width).pack(pady=5, anchor="w")

        # Höger sektion - Resultat
        result_frame = ttk.LabelFrame(paned_window, text="Result", padding="10 10 10 10")
        paned_window.add(result_frame, weight=3)
        
        # Textfält för att visa resultat, med en scrollbar
        self.text_result = tk.Text(result_frame, height=20, width=50, wrap="word")
        self.text_result.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Lägg till en scrollbar på höger sida
        scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.text_result.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_result["yscrollcommand"] = scroll.set
        
    def format_data(self, data):
        """Formaterar JSON-data till ett läsbart format för visning."""
        if isinstance(data, list):
            # Om data är en lista av objekt, formatera varje objekt individuellt
            result = ""
            for item in data:
                # Formatera varje objekts data
                result += f"ID: {item.get('id', 'N/A')}\nNamn: {item.get('name', 'N/A')}\nVärde: {item.get('value', 'N/A')}\n\n"
            return result.strip()
        elif isinstance(data, dict):
            # Om data är ett enskilt objekt, kolla först om det är ett felmeddelande
            if "error" in data:
                return f"Error: {data['error']}"  # Returnera felmeddelandet
            # Om det inte är ett felmeddelande, formatera objektet som en post
            return f"ID: {data.get('id', 'N/A')}\nNamn: {data.get('name', 'N/A')}\nVärde: {data.get('value', 'N/A')}"
        else:
            # Om data inte är en lista eller ett objekt, returnera den som en sträng
            return str(data)

    def show_message(self, message):
        """Visar meddelande i textfältet med formatering."""
        self.text_result.delete("1.0", tk.END)  # Rensa tidigare innehåll i textfältet
        formatted_message = self.format_data(message)  # Formatera meddelandet
        self.text_result.insert(tk.END, formatted_message)  # Sätt in det formaterade meddelandet

    def add_new_user(self):
        """Lägger till en ny användare i API:et."""
        # Fråga användaren efter namn och värde
        name = simpledialog.askstring("Input", "Ange ett namn:")
        value = simpledialog.askstring("Input", "Ange ett värde:")
        
        # Kontrollera om användaren angav båda fälten, annars visa ett felmeddelande
        if not name or not value:
            messagebox.showerror("Error", "Var snäll att skriva nått i alla fällt.")
            return
        
        # Skicka en POST-begäran till servern med det nya objektet
        data = {"name": name, "value": value}
        response = requests.post("http://127.0.0.1:5000/insert", json=data)
        # Visa resultatet från servern i textfältet
        self.show_message(response.json())

    def list_all_users(self):
        """Listar alla användare från API:et."""
        response = requests.get("http://127.0.0.1:5000/select_all")  # Skicka GET-begäran för alla användare
        self.show_message(response.json())  # Visa resultatet

    def show_user_by_id(self):
        """Visar en specifik användare baserat på ID."""
        user_id = simpledialog.askstring("Input", "Ange User ID:")  # Fråga användaren om ID
        if not user_id:
            messagebox.showerror("Error", "Var god att ange ett ID.")
            return
        
        response = requests.get(f"http://127.0.0.1:5000/select_one/{user_id}")  # Skicka GET-begäran för en användare
        if response.status_code == 200:
            self.show_message(response.json())  # Visa användaren om hittad
        else:
            self.show_message({"error": "Hittade ingen användare med det ID:t."})  # Visa felmeddelande om ej hittad

    def update_user(self):
        """Uppdaterar en användares information."""
        user_id = simpledialog.askstring("Input", "Ange användarens ID som ska uppdateras:")  # Fråga om ID
        if not user_id:
            messagebox.showerror("Error", "Var god att ange ett ID.")
            return
        
        name = simpledialog.askstring("Input", "Skriv ett nytt namn (lämna blank om du vill behålla det gamla namnet):")
        value = simpledialog.askstring("Input", "Ange ett nytt värde (eller lämna blankt för att behålla det gamla värdet):")
        
        # Skapa ett dictionary för att bara inkludera de värden som faktiskt har ändrats
        data = {}
        if name:
            data["name"] = name
        if value:
            data["value"] = value
            
        # Skicka en PUT-begäran till servern för att uppdatera objektet
        response = requests.put(f"http://127.0.0.1:5000/update/{user_id}", json=data)
        self.show_message(response.json())  # Visa resultatet

    def delete_user(self):
        """Tar bort en användare baserat på ID."""
        user_id = simpledialog.askstring("Input", "Ange ett ID som ska tas bort:")  # Fråga om ID
        if not user_id:
            messagebox.showerror("Error", "Var god att ange ett ID.")
            return
        
        response = requests.delete(f"http://127.0.0.1:5000/delete/{user_id}")  # Skicka DELETE-begäran
        data = response.json()
        
        # Kontrollera om borttagningen var lyckad och visa relevant information
        if response.status_code == 200 and "deleted_object" in data:
            deleted_obj = data["deleted_object"]
            # Skapa ett meddelande som visar att borttagningen var lyckad och detaljer om objektet som raderades
            message = f"{data['message']}\n\nDe borttagna informationen:\nID: {deleted_obj['id']}\nNamn: {deleted_obj['name']}\nValue: {deleted_obj['value']}"
        else:
            # Visa ett felmeddelande om objektet inte kunde tas bort
            message = data.get("error", "Okänt fel inträffades.")
        
        self.show_message(message)  # Visa meddelandet

    def export_to_json(self):
        """Exporterar data från SQLite-databasen till JSON-filen."""
        try:
            response = requests.post("http://127.0.0.1:5000/export")  # Skicka POST-begäran för export
            response.raise_for_status()  # Kasta ett undantag om svaret inte är 200 OK
            if response.status_code == 200:
                messagebox.showinfo("Export", "Data exported to JSON successfully.")
            else:
                messagebox.showerror("Export Error", "Failed to export data.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Export Error", f"Request failed: {e}")

# Starta applikationen
if __name__ == "__main__":
    root = tk.Tk()
    app = APIClientApp(root)
    root.mainloop()
