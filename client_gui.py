import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, Label
from PIL import Image, ImageTk, ImageDraw
import requests
import os

class APIClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("API Client - Main Menu")
        
         # Skapa en topppanel för att hålla ikonen och huvudmenyn
        top_frame = ttk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=10)

        # Ladda och bearbeta ikonen
        icon_path = "api.png"
        if os.path.exists(icon_path):
            original_icon = Image.open(icon_path).convert("RGBA")
            resized_icon = original_icon.resize((50, 50), Image.LANCZOS)

            # Skapa en cirkelmask för ikonen
            mask = Image.new("L", (50, 50), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 50, 50), fill=255)

            # Tillämpa masken för att göra ikonen cirkulär
            circular_icon = Image.new("RGBA", (50, 50))
            circular_icon.paste(resized_icon, (0, 0), mask=mask)
            self.icon_image = ImageTk.PhotoImage(circular_icon)

            # Lägg till ikonen i top_frame
            icon_label = tk.Label(top_frame, image=self.icon_image)
            icon_label.pack(side="left", padx=5)
        else:
            print("Ikonfilen api.png hittades inte")
        
        # Skapa ett PanedWindow för att dela upp fönstret i två sektioner
        paned_window = ttk.PanedWindow(root, orient="horizontal")
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Vänster sektion - Main Menu
        menu_frame = ttk.LabelFrame(paned_window, text="Huvud Meny", padding="10 10 10 10")
        paned_window.add(menu_frame, weight=1)

        # Lägg till knappar i menyn
        button_width = 20
        ttk.Button(menu_frame, text="Lägg till ny användare", command=self.add_new_user, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Lista alla användare", command=self.list_all_users, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Visa användare med ID", command=self.show_user_by_id, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Updatera användare", command=self.update_user, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Ta bort användare", command=self.delete_user, width=button_width).pack(pady=5, anchor="w")

        # Höger sektion - Resultat
        result_frame = ttk.LabelFrame(paned_window, text="Result", padding="10 10 10 10")
        paned_window.add(result_frame, weight=3)
        
        self.text_result = tk.Text(result_frame, height=20, width=50, wrap="word")
        self.text_result.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Skapa Text-widget för att visa resultat, med scroll-funktionalitet
        scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.text_result.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_result["yscrollcommand"] = scroll.set
        
        
    def format_data(self, data):
        """Formaterar JSON-data till ett läsbart format."""
        if isinstance(data, list):
            # Om datan är en lista av objekt, formatera varje objekt individuellt
            result = ""
            for item in data:
                # Skapa en sträng med varje objekts ID, namn och värde
                result += f"ID: {item.get('id', 'N/A')}\nNamn: {item.get('name', 'N/A')}\nVärde: {item.get('value', 'N/A')}\n\n"
            return result.strip()  # Ta bort eventuella tomma rader i slutet
        elif isinstance(data, dict):
            # Om datan är ett enskilt objekt, kolla först om det är ett felmeddelande
            if "error" in data:
                return f"Error: {data['error']}"  # Returnera felmeddelandet
            # Om det inte är ett felmeddelande, formatera objektet som en post
            return f"ID: {data.get('id', 'N/A')}\nNamn: {data.get('name', 'N/A')}\nVärde: {data.get('value', 'N/A')}"
        else:
            # Om datan inte är en lista eller ett objekt, returnera den som en sträng
            return str(data)

    def show_message(self, message):
        """Visar resultat i textfältet med bättre formatering."""
        # Rensa tidigare innehåll i textfältet
        self.text_result.delete("1.0", tk.END)
        # Formatera meddelandet och sätt in det i textfältet
        formatted_message = self.format_data(message)
        self.text_result.insert(tk.END, formatted_message)

    def add_new_user(self):
        """Lägger till en ny användare."""
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
        """Listar alla användare."""
        # Skicka en GET-begäran till servern för att hämta alla objekt
        response = requests.get("http://127.0.0.1:5000/select_all")
        # Visa listan med alla objekt i textfältet
        self.show_message(response.json())

    def show_user_by_id(self):
        """Visar en användare baserat på ID."""
        # Fråga användaren om ID för objektet som ska visas
        user_id = simpledialog.askstring("Input", "Ange User ID:")
        if not user_id:
            messagebox.showerror("Error", "Var god att ange ett ID.")
            return
        
        # Skicka en GET-begäran till servern för att hämta objektet med det angivna ID:t
        response = requests.get(f"http://127.0.0.1:5000/select_one/{user_id}")
        
        if response.status_code == 200:
            # Om objektet hittades, visa det i textfältet
            self.show_message(response.json())
        else:
            # Om objektet inte hittades, visa ett felmeddelande
            self.show_message({"error": "Hittade ingen användare med det ID:t."})

    def update_user(self):
        """Uppdaterar en användare."""
        # Fråga användaren om ID för objektet som ska uppdateras
        user_id = simpledialog.askstring("Input", "Ange användarens ID som ska uppdateras:")
        if not user_id:
            messagebox.showerror("Error", "Var god att ange ett ID.")
            return
        
        # Fråga efter nya värden för namn och värde, eller låt fälten vara tomma för att behålla aktuella värden
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
        # Visa resultatet från servern i textfältet
        self.show_message(response.json())

    def delete_user(self):
        """Tar bort en användare och visar resultatet."""
        # Fråga användaren om ID för objektet som ska raderas
        user_id = simpledialog.askstring("Input", "Ange ett ID som ska tas bort:")
        if not user_id:
            messagebox.showerror("Error", "Var god att ange ett ID.")
            return
        
        # Skicka en DELETE-begäran till servern för att ta bort objektet
        response = requests.delete(f"http://127.0.0.1:5000/delete/{user_id}")
        data = response.json()
        
        # Kontrollera om borttagningen var lyckad och visa relevant information
        if response.status_code == 200 and "deleted_object" in data:
            deleted_obj = data["deleted_object"]
            # Skapa ett meddelande som visar att borttagningen var lyckad och detaljer om objektet som raderades
            message = f"{data['message']}\n\nDe borttagna informationen:\nID: {deleted_obj['id']}\nNamn: {deleted_obj['name']}\nValue: {deleted_obj['value']}"
        else:
            # Visa ett felmeddelande om objektet inte kunde tas bort
            message = data.get("error", "Okänt fel inträffades.")
        
        # Visa meddelandet i textfältet
        self.show_message(message)

# Starta applikationen
if __name__ == "__main__":
    root = tk.Tk()
    app = APIClientApp(root)
    root.mainloop()
