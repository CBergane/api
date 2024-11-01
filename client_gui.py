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
        menu_frame = ttk.LabelFrame(paned_window, text="Main Menu", padding="10 10 10 10")
        paned_window.add(menu_frame, weight=1)

        # Lägg till knappar i menyn
        button_width = 20
        ttk.Button(menu_frame, text="Add New User", command=self.add_new_user, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="List All Users", command=self.list_all_users, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Show User by ID", command=self.show_user_by_id, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Update User", command=self.update_user, width=button_width).pack(pady=5, anchor="w")
        ttk.Button(menu_frame, text="Delete User", command=self.delete_user, width=button_width).pack(pady=5, anchor="w")

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
            # Formatera en lista av objekt
            result = ""
            for item in data:
                result += f"ID: {item.get('id', 'N/A')}\nName: {item.get('name', 'N/A')}\nValue: {item.get('value', 'N/A')}\n\n"
            return result.strip()
        elif isinstance(data, dict):
            # Kontrollera om datan är ett felmeddelande
            if "error" in data:
                return f"Error: {data['error']}"
            # Formatera en enskild post
            return f"ID: {data.get('id', 'N/A')}\nName: {data.get('name', 'N/A')}\nValue: {data.get('value', 'N/A')}"
        else:
            # Returnera textsträngen om datan inte är en lista eller ett objekt
            return str(data)

    def show_message(self, message):
        """Visar resultat i textfältet med bättre formatering."""
        self.text_result.delete("1.0", tk.END)
        formatted_message = self.format_data(message)
        self.text_result.insert(tk.END, formatted_message)

    def add_new_user(self):
        """Lägger till en ny användare."""
        name = simpledialog.askstring("Input", "Enter Name:")
        value = simpledialog.askstring("Input", "Enter Value:")
        
        if not name or not value:
            messagebox.showerror("Error", "Please enter all fields.")
            return
        
        data = {"name": name, "value": value}
        response = requests.post("http://127.0.0.1:5000/insert", json=data)
        self.show_message(response.json())

    def list_all_users(self):
        """Listar alla användare."""
        response = requests.get("http://127.0.0.1:5000/select_all")
        self.show_message(response.json())

    def show_user_by_id(self):
        """Visar en användare baserat på ID."""
        user_id = simpledialog.askstring("Input", "Enter User ID:")
        if not user_id:
            messagebox.showerror("Error", "Please enter an ID.")
            return
        
        response = requests.get(f"http://127.0.0.1:5000/select_one/{user_id}")
        
        if response.status_code == 200:
            self.show_message(response.json())
        else:
            # Om användaren inte hittades, visa felmeddelandet
            self.show_message({"error": "User not found"})

    def update_user(self):
        """Uppdaterar en användare."""
        user_id = simpledialog.askstring("Input", "Enter User ID to update:")
        if not user_id:
            messagebox.showerror("Error", "Please enter an ID.")
            return
        
        name = simpledialog.askstring("Input", "Enter new Name (or leave blank to keep current):")
        value = simpledialog.askstring("Input", "Enter new Value (or leave blank to keep current):")
        
        data = {}
        if name:
            data["name"] = name
        if value:
            data["value"] = value
            
        response = requests.put(f"http://127.0.0.1:5000/update/{user_id}", json=data)
        self.show_message(response.json())

    def delete_user(self):
        """Tar bort en användare och visar resultatet."""
        user_id = simpledialog.askstring("Input", "Enter User ID to delete:")
        if not user_id:
            messagebox.showerror("Error", "Please enter an ID.")
            return
        
        response = requests.delete(f"http://127.0.0.1:5000/delete/{user_id}")
        data = response.json()
        
        # Kolla om borttagningen var lyckad och visa relevant information
        if response.status_code == 200 and "deleted_object" in data:
            deleted_obj = data["deleted_object"]
            message = f"{data['message']}\n\nDeleted Object Details:\nID: {deleted_obj['id']}\nName: {deleted_obj['name']}\nValue: {deleted_obj['value']}"
        else:
            message = data.get("error", "Unknown error occurred.")
        
        self.show_message(message)


if __name__ == "__main__":
    root = tk.Tk()
    app = APIClientApp(root)
    root.mainloop()
