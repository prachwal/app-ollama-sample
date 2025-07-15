"""
System Prompt Dialog
===================
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ..config import SYSTEM_PROMPT_MODES


class SystemPromptDialog:
    """Dialog do edycji własnego promptu systemowego"""
    
    def __init__(self, parent, chat_component):
        self.parent = parent
        self.chat_component = chat_component
        self.dialog = None
        self.result = None
        
    def show(self):
        """Pokazuje dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🎭 Edycja promptu systemowego")
        self.dialog.geometry("600x400")
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
            text="Wprowadź własny prompt systemowy, który będzie wysyłany przed każdym pytaniem:",
            wraplength=580
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
            height=15, 
            width=70,
            font=('Arial', 10)
        )
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        # Wstaw aktualny tekst
        current_prompt = self.chat_component.custom_system_prompt
        if current_prompt:
            self.text_area.insert("1.0", current_prompt)
        
        # Przykłady
        examples_frame = ttk.LabelFrame(main_frame, text="Przykłady promptów", padding="5")
        examples_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        examples_text = ("Przykłady:\n"
                        "• Jesteś ekspertem programistą Python. Odpowiadaj krótko i konkretnie.\n"
                        "• Odpowiadaj w stylu Shakespearea, używając archaicznego języka.\n"
                        "• Jesteś przyjaznym nauczycielem. Wyjaśniaj rzeczy w prosty sposób.")
        
        ttk.Label(examples_frame, text=examples_text, wraplength=580).pack(anchor=tk.W)
        
        # Przyciski
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(buttons_frame, text="💾 Zapisz", command=self.save_prompt).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="❌ Anuluj", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(buttons_frame, text="🗑️ Wyczyść", command=self.clear_text).pack(side=tk.LEFT)
        
        # Bind Ctrl+Enter do zapisania
        self.dialog.bind("<Control-Return>", lambda e: self.save_prompt())
        self.dialog.bind("<Escape>", lambda e: self.cancel())
    
    def save_prompt(self):
        """Zapisuje prompt i zamyka dialog"""
        prompt_text = self.text_area.get("1.0", tk.END).strip()
        
        if not prompt_text:
            if messagebox.askyesno("Potwierdzenie", "Prompt jest pusty. Czy chcesz ustawić pusty prompt?"):
                self.chat_component.custom_system_prompt = ""
                self.chat_component.system_prompt_mode.set("Standardowy")
                self.result = "cleared"
                self.dialog.destroy()
            return
        
        # Zapisz prompt
        self.chat_component.custom_system_prompt = prompt_text
        self.chat_component.system_prompt_mode.set("Własny prompt")
        
        # Powiadom o zmianie
        self.chat_component.add_to_chat(f"🎭 Ustawiono własny prompt systemowy ({len(prompt_text)} znaków)", "system")
        
        self.result = "saved"
        self.dialog.destroy()
    
    def cancel(self):
        """Anuluje i zamyka dialog"""
        self.result = "cancelled"
        self.dialog.destroy()
    
    def clear_text(self):
        """Czyści pole tekstowe"""
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz wyczyścić tekst?"):
            self.text_area.delete("1.0", tk.END)
