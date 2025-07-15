"""
Quick Test Dialog
================
"""

import tkinter as tk
from tkinter import ttk, messagebox


class QuickTestDialog:
    """Dialog do wprowadzenia pytania dla szybkiego testu"""
    
    def __init__(self, parent, testing_component):
        self.parent = parent
        self.testing_component = testing_component
        self.dialog = None
        self.result = None
        
    def show(self):
        """Pokazuje dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🏃 Test Szybki")
        self.dialog.geometry("500x300")
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
        main_frame.rowconfigure(1, weight=1)
        
        # Informacja
        info_label = ttk.Label(
            main_frame, 
            text="Wprowadź pytanie testowe, które zostanie wysłane kilkukrotnie do modelu:",
            wraplength=480
        )
        info_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Pole tekstowe
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.text_area = tk.Text(
            text_frame, 
            wrap=tk.WORD, 
            height=8, 
            width=60,
            font=('Arial', 10)
        )
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        # Przykłady
        examples_frame = ttk.LabelFrame(main_frame, text="Przykłady pytań testowych", padding="5")
        examples_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        examples_text = ("• Napisz funkcję Python do sortowania listy\n"
                        "• Wyjaśnij różnicę między HTTP a HTTPS\n"
                        "• Jak działa algorytm quicksort?")
        
        ttk.Label(examples_frame, text=examples_text, wraplength=480).pack(anchor=tk.W)
        
        # Przyciski
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(buttons_frame, text="🏃 Uruchom Test", command=self.run_test).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="❌ Anuluj", command=self.cancel).pack(side=tk.RIGHT)
        
        # Bind klawiszy
        self.dialog.bind("<Control-Return>", lambda e: self.run_test())
        self.dialog.bind("<Escape>", lambda e: self.cancel())
        
        # Focus na pole tekstowe
        self.text_area.focus_set()
    
    def run_test(self):
        """Uruchamia test z wprowadzonym pytaniem"""
        question = self.text_area.get("1.0", tk.END).strip()
        
        if not question:
            messagebox.showerror("Błąd", "Wprowadź pytanie testowe!")
            return
        
        self.result = question
        self.dialog.destroy()
        
        # Uruchom test w komponencie testowym
        self.testing_component.run_test_with_question(question)
    
    def cancel(self):
        """Anuluje i zamyka dialog"""
        self.result = None
        self.dialog.destroy()
