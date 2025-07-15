"""
Main GUI Window for Ollama Application
======================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os

from .config import WINDOW_CONFIG, GUI_STYLES, GUI_FONTS
from .components.chat_component import ChatComponent
from .components.testing_component import TestingComponent


class OllamaGUI:
    """Główna klasa interfejsu graficznego"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_gui()
        self.load_models()
    
    def setup_window(self):
        """Konfiguruje główne okno"""
        self.root.title(WINDOW_CONFIG['title'])
        self.root.geometry(f"{WINDOW_CONFIG['width']}x{WINDOW_CONFIG['height']}")
        self.root.resizable(True, True)
        
        # Ikona (jeśli istnieje)
        if os.path.exists("icon.ico"):
            self.root.iconbitmap("icon.ico")
    
    def setup_variables(self):
        """Inicjalizuje zmienne"""
        self.selected_model = tk.StringVar()
        self.progress_var = tk.StringVar(value="Gotowy")
        self.status_var = tk.StringVar(value="Ładowanie modeli...")
    
    def setup_gui(self):
        """Tworzy interfejs użytkownika"""
        # Główny kontener
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Nagłówek z wyborem modelu
        self.setup_header(main_frame)
        
        # Notebook z zakładkami
        self.setup_notebook(main_frame)
        
        # Pasek statusu
        self.setup_status_bar(main_frame)
    
    def setup_header(self, parent):
        """Tworzy sekcję nagłówka"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(2, weight=1)
        
        # Tytuł
        title_label = ttk.Label(
            header_frame, 
            text="🦙 Ollama Chat & Test GUI", 
            font=GUI_FONTS['header_font']
        )
        title_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        # Wybór modelu
        ttk.Label(header_frame, text="Model:").grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        
        self.model_combo = ttk.Combobox(
            header_frame, 
            textvariable=self.selected_model,
            state="readonly",
            width=30
        )
        self.model_combo.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(0, 10))
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_selected)
        
        # Przycisk odświeżania modeli
        ttk.Button(
            header_frame, 
            text="🔄", 
            command=self.refresh_models,
            width=3
        ).grid(row=0, column=3)
        
        # Menu
        self.setup_menu()
    
    def setup_menu(self):
        """Tworzy menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Plik
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Plik", menu=file_menu)
        file_menu.add_command(label="Nowy czat", command=self.new_chat)
        file_menu.add_command(label="Zapisz czat...", command=self.save_chat)
        file_menu.add_command(label="Wczytaj czat...", command=self.load_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Wyjście", command=self.root.quit)
        
        # Menu Test
        test_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Test", menu=test_menu)
        test_menu.add_command(label="Test szybki...", command=self.quick_test)
        test_menu.add_command(label="Utwórz test...", command=self.create_test)
        test_menu.add_command(label="Wczytaj test...", command=self.load_test)
        test_menu.add_separator()
        test_menu.add_command(label="Wyczyść wyniki", command=self.clear_test_results)
        test_menu.add_command(label="Zapisz wyniki...", command=self.save_test_results)
        
        # Menu Pomoc
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Pomoc", menu=help_menu)
        help_menu.add_command(label="O programie", command=self.show_about)
        help_menu.add_command(label="Pomoc", command=self.show_help)
    
    def setup_notebook(self, parent):
        """Tworzy notebook z zakładkami"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Komponenty
        self.chat_component = ChatComponent(self, self.notebook)
        self.testing_component = TestingComponent(self, self.notebook)
    
    def setup_status_bar(self, parent):
        """Tworzy pasek statusu"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        # Pasek postępu
        self.progress_bar = ttk.Progressbar(
            status_frame, 
            mode='indeterminate',
            style='TProgressbar'
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status
        status_label_frame = ttk.Frame(status_frame)
        status_label_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        status_label_frame.columnconfigure(0, weight=1)
        
        ttk.Label(status_label_frame, textvariable=self.progress_var).pack(side=tk.LEFT)
        ttk.Label(status_label_frame, textvariable=self.status_var).pack(side=tk.RIGHT)
    
    def load_models(self):
        """Ładuje listę dostępnych modeli"""
        def load_in_thread():
            try:
                self.root.after(0, lambda: self.progress_bar.start())
                self.root.after(0, lambda: self.progress_var.set("Ładowanie modeli..."))
                
                from src.api import get_available_models
                models = get_available_models()
                
                self.root.after(0, lambda: self.model_combo.configure(values=models))
                
                if models:
                    self.root.after(0, lambda: self.selected_model.set(models[0]))
                    self.root.after(0, lambda: self.status_var.set(f"Załadowano {len(models)} modeli"))
                else:
                    self.root.after(0, lambda: self.status_var.set("Brak dostępnych modeli"))
                
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Błąd ładowania modeli: {str(e)}"))
                self.root.after(0, lambda: messagebox.showerror("Błąd", f"Nie można załadować modeli:\n{str(e)}"))
            
            finally:
                self.root.after(0, lambda: self.progress_bar.stop())
                self.root.after(0, lambda: self.progress_var.set("Gotowy"))
        
        threading.Thread(target=load_in_thread, daemon=True).start()
    
    def refresh_models(self):
        """Odświeża listę modeli"""
        self.load_models()
    
    def on_model_selected(self, event=None):
        """Obsługuje wybór modelu"""
        model = self.selected_model.get()
        if model:
            self.status_var.set(f"Wybrany model: {model}")
    
    # Menu callbacks
    def new_chat(self):
        """Nowy czat"""
        self.chat_component.clear_chat()
    
    def save_chat(self):
        """Zapisz czat"""
        self.chat_component.save_chat()
    
    def load_chat(self):
        """Wczytaj czat"""
        self.chat_component.load_chat()
    
    def quick_test(self):
        """Test szybki"""
        self.notebook.select(1)  # Przełącz na zakładkę testów
        self.testing_component.run_quick_test()
    
    def create_test(self):
        """Utwórz test"""
        self.notebook.select(1)  # Przełącz na zakładkę testów
        self.testing_component.create_custom_test()
    
    def load_test(self):
        """Wczytaj test"""
        self.notebook.select(1)  # Przełącz na zakładkę testów
        self.testing_component.load_test()
    
    def clear_test_results(self):
        """Wyczyść wyniki testów"""
        self.testing_component.clear_results()
    
    def save_test_results(self):
        """Zapisz wyniki testów"""
        self.testing_component.save_test_results()
    
    def show_about(self):
        """O programie"""
        about_text = """Ollama Chat & Test GUI v2.2
        
Interfejs graficzny do interakcji z modelami Ollama.

Funkcje:
• Chat z modelami AI
• Tryby systemowe (persony)
• Testowanie modeli
• Porównywanie odpowiedzi

Autor: Assistant
Data: 2024"""
        
        messagebox.showinfo("O programie", about_text)
    
    def show_help(self):
        """Pomoc"""
        help_text = """Pomoc - Ollama GUI

CZAT:
• Wybierz model z listy
• Ustaw tryb systemowy (persona)
• Wpisz wiadomość i naciśnij Ctrl+Enter

TESTY:
• Test szybki - wielokrotne wysłanie tego samego pytania
• Test własny - zaawansowane testowanie z parametrami
• Możliwość zapisywania i wczytywania testów

TRYBY SYSTEMOWE:
• Ustawiają kontekst dla modelu
• 9 predefiniowanych trybów + własny
• Wpływają na styl odpowiedzi"""
        
        messagebox.showinfo("Pomoc", help_text)
    
    def run(self):
        """Uruchamia aplikację"""
        self.root.mainloop()


def main():
    """Funkcja główna"""
    app = OllamaGUI()
    app.run()


if __name__ == "__main__":
    main()
