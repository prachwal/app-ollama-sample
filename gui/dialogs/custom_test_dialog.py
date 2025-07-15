"""
Custom Test Dialog
=================
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime


class CustomTestDialog:
    """Dialog do tworzenia własnego testu"""
    
    def __init__(self, parent, testing_component):
        self.parent = parent
        self.testing_component = testing_component
        self.dialog = None
        self.result = None
        
    def show(self):
        """Pokazuje dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("⚙️ Utwórz Test Własny")
        self.dialog.geometry("700x500")
        self.dialog.resizable(True, True)
        
        # Centruj dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        
        # Ustaw focus
        self.dialog.focus_set()
        
        # Czekaj na zamknięcie
        self.dialog.wait_window()
        
        return self.result
    
    def setup_dialog(self):
        """Konfiguruje interfejs dialogu"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Nazwa testu
        ttk.Label(main_frame, text="Nazwa testu:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.test_name = tk.StringVar(value=f"Test_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        ttk.Entry(main_frame, textvariable=self.test_name, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(5, 0))
        
        # Typ testu
        ttk.Label(main_frame, text="Typ testu:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.test_type = tk.StringVar(value="SIMPLE")
        test_type_frame = ttk.Frame(main_frame)
        test_type_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(5, 0))
        
        ttk.Radiobutton(test_type_frame, text="SIMPLE", variable=self.test_type, value="SIMPLE").pack(side=tk.LEFT)
        ttk.Radiobutton(test_type_frame, text="EXPECTED", variable=self.test_type, value="EXPECTED").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(test_type_frame, text="KEYWORD", variable=self.test_type, value="KEYWORD").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(test_type_frame, text="LENGTH", variable=self.test_type, value="LENGTH").pack(side=tk.LEFT, padx=(10, 0))
        
        # Pytanie
        ttk.Label(main_frame, text="Pytanie testowe:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(5, 0))
        question_frame = ttk.Frame(main_frame)
        question_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0), padx=(5, 0))
        question_frame.columnconfigure(0, weight=1)
        question_frame.rowconfigure(0, weight=1)
        
        self.question_text = tk.Text(question_frame, height=4, wrap=tk.WORD, font=('Arial', 10))
        self.question_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        q_scrollbar = ttk.Scrollbar(question_frame, orient=tk.VERTICAL, command=self.question_text.yview)
        q_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.question_text.configure(yscrollcommand=q_scrollbar.set)
        
        # Parametry dodatkowe
        ttk.Label(main_frame, text="Parametry dodatkowe:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=(10, 0))
        params_frame = ttk.Frame(main_frame)
        params_frame.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0), padx=(5, 0))
        params_frame.columnconfigure(0, weight=1)
        params_frame.rowconfigure(0, weight=1)
        
        self.params_text = tk.Text(params_frame, height=4, wrap=tk.WORD, font=('Arial', 10))
        self.params_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        p_scrollbar = ttk.Scrollbar(params_frame, orient=tk.VERTICAL, command=self.params_text.yview)
        p_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.params_text.configure(yscrollcommand=p_scrollbar.set)
        
        # Wstaw przykładowe parametry
        example_params = '''{"expected_response": "Przykładowa oczekiwana odpowiedź",
 "keywords": ["słowo1", "słowo2", "słowo3"],
 "min_length": 100,
 "max_length": 1000,
 "temperature": 0.7,
 "iterations": 3}'''
        self.params_text.insert("1.0", example_params)
        
        # Informacja
        info_frame = ttk.LabelFrame(main_frame, text="Informacje", padding="5")
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        info_text = ("SIMPLE: Podstawowy test wysyłania pytania\n"
                    "EXPECTED: Test z porównaniem do oczekiwanej odpowiedzi\n"
                    "KEYWORD: Test obecności określonych słów kluczowych\n"
                    "LENGTH: Test długości odpowiedzi (min_length, max_length)")
        
        ttk.Label(info_frame, text=info_text, wraplength=680).pack(anchor=tk.W)
        
        # Przyciski
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(buttons_frame, text="💾 Zapisz Test", command=self.save_test).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="🏃 Uruchom Test", command=self.run_test).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="❌ Anuluj", command=self.cancel).pack(side=tk.RIGHT)
        
        # Bind klawiszy
        self.dialog.bind("<Escape>", lambda e: self.cancel())
    
    def save_test(self):
        """Zapisuje test do pliku JSON"""
        test_data = self.build_test_data()
        if not test_data:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*")],
            title="Zapisz test",
            initialvalue=f"{self.test_name.get()}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(test_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Sukces", f"Test zapisany do: {filename}")
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można zapisać testu: {str(e)}")
    
    def run_test(self):
        """Uruchamia test bezpośrednio"""
        test_data = self.build_test_data()
        if not test_data:
            return
        
        self.result = test_data
        self.dialog.destroy()
        
        # Uruchom test w komponencie testowym
        self.testing_component.run_loaded_test(test_data, "Dialog")
    
    def build_test_data(self):
        """Buduje dane testowe z formularza"""
        name = self.test_name.get().strip()
        if not name:
            messagebox.showerror("Błąd", "Wprowadź nazwę testu!")
            return None
        
        question = self.question_text.get("1.0", tk.END).strip()
        if not question:
            messagebox.showerror("Błąd", "Wprowadź pytanie testowe!")
            return None
        
        # Parsuj parametry JSON
        params_text = self.params_text.get("1.0", tk.END).strip()
        try:
            if params_text:
                params = json.loads(params_text)
            else:
                params = {}
        except json.JSONDecodeError as e:
            messagebox.showerror("Błąd", f"Nieprawidłowy format JSON w parametrach: {str(e)}")
            return None
        
        # Buduj test
        test_data = {
            "name": name,
            "description": f"Test własny: {name}",
            "type": self.test_type.get(),
            "question": question,
            "created": datetime.now().isoformat(),
            **params
        }
        
        return test_data
    
    def cancel(self):
        """Anuluje i zamyka dialog"""
        self.result = None
        self.dialog.destroy()
