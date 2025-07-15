#!/usr/bin/env python3
"""
Ollama Basic Chat GUI - Graficzny interfejs do rozmowy z modelami LLM
====================================================================

Pełny interfejs graficzny dla aplikacji ollama_basic_chat.
Używa modułowej architektury z src/ dla spójności kodu.

Autor: Ollama Testing Team
Wersja: 2.0.0 GUI
"""

import sys
import os
import threading
import time
from datetime import datetime
from queue import Queue
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

# Dodaj src do PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import get_available_models, ask_ollama, judge_with_gemini
from src.utils import (
    get_comprehensive_test_prompts, 
    get_quick_test_prompts,
    get_test_prompts_by_language,
    get_available_languages,
    get_language_display_name,
    get_timestamp,
    generate_summary
)
from src.config import DEFAULT_SLEEP_BETWEEN_MODELS


class OllamaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Basic Chat GUI v2.2")
        self.root.geometry("1200x800")
        
        # Zmienne
        self.models = []
        self.selected_model = tk.StringVar()
        self.selected_language = tk.StringVar(value="polish")
        self.selected_language_code = "polish"  # Kod języka używany przez funkcje
        self.use_judge = tk.BooleanVar(value=True)  # Opcja sędziego LLM
        self.gemini_api_key = self.load_gemini_api_key()  # Klucz API Gemini z ENV lub pusty
        self.system_prompt_mode = tk.StringVar(value="Standardowy")  # Tryb systemowy dla promptów
        
        # Predefiniowane tryby systemowe (persona)
        self.system_prompt_modes = {
            "Standardowy": "",
            "Profesjonalny programista": "Jesteś profesjonalnym programistą z wieloletnim doświadczeniem. Odpowiadaj precyzyjnie, podawaj przykłady kodu i najlepsze praktyki. Wyjaśniaj złożone koncepty w przystępny sposób.",
            "Asystent naukowy": "Jesteś asystentem naukowym o szerokich kompetencjach. Odpowiadaj obiektywnie, posiłkuj się faktami i badaniami. Wyjaśniaj złożone tematy krok po kroku.",
            "Kreatywny pisarz": "Jesteś kreatywnym pisarzem i storytellerem. Używaj żywego języka, metafor i obrazowych opisów. Pobudź wyobraźnię i stwórz angażujące narracje.",
            "Analityk biznesowy": "Jesteś doświadczonym analitykiem biznesowym. Myśl strategicznie, analizuj problemy z perspektywy biznesowej i proponuj praktyczne rozwiązania.",
            "Nauczyciel": "Jesteś cierpliwym i doświadczonym nauczycielem. Wyjaśniaj zagadnienia krok po kroku, używaj prostego języka i podawaj przykłady. Zadawaj pytania kontrolne.",
            "Ekspert IT": "Jesteś ekspertem IT z szeroką wiedzą techniczną. Doradzaj w kwestiach architektury, bezpieczeństwa i najlepszych praktyk. Myśl o skalowalności i wydajności.",
            "Konsultant prawny": "Jesteś konsultantem prawnym. Analizuj kwestie z perspektywy prawnej, wskazuj potencjalne ryzyka i proponuj zgodne z prawem rozwiązania. Zawsze zaznaczaj potrzebę weryfikacji przez prawnika.",
            "Psycholog": "Jesteś empatycznym psychologiem. Słuchaj uważnie, zadawaj przemyślane pytania i oferuj wsparcie. Zachowaj profesjonalny dystans i nie diagnozuj.",
            "Własny prompt": "CUSTOM"  # Specjalna wartość dla własnego prompta
        }
        self.custom_system_prompt = ""  # Własny prompt użytkownika
        self.current_chat_file = None
        self.is_testing = False
        self.stop_testing = False  # Flaga do zatrzymywania testów
        self.test_queue = Queue()
        
        # Style
        self.setup_styles()
        
        # Interface
        self.setup_interface()
        
        # Załaduj modele
        self.load_models()
        
        # Start monitoring queue
        self.monitor_queue()
    
    def load_gemini_api_key(self):
        """Ładuje klucz API Gemini ze zmiennej środowiskowej"""
        return os.getenv("GEMINI_API_KEY", "")

    def stop_test(self):
        """Zatrzymuje aktualnie działający test"""
        if self.is_testing:
            self.stop_testing = True
            if hasattr(self, 'test_status_var'):
                self.test_status_var.set("Zatrzymywanie testów...")
            if hasattr(self, 'stop_test_btn'):
                self.stop_test_btn.config(state="disabled")
            if hasattr(self, 'status_label'):
                self.status_label.config(text="🛑 Zatrzymywanie testów...", style='Warning.TLabel')
        else:
            messagebox.showinfo("Info", "Żaden test obecnie nie jest uruchomiony")

    def setup_styles(self):
        """Ustawia style interfejsu"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Kolory
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
        style.configure('Info.TLabel', foreground='blue')
    
    def setup_interface(self):
        """Tworzy główny interfejs"""
        # Główny kontener
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfiguracja rozciągania
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # === NAGŁÓWEK ===
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(header_frame, text="🤖 Ollama Basic Chat GUI", 
                 style='Header.TLabel').pack(side=tk.LEFT)
        
        # Status połączenia
        self.status_label = ttk.Label(header_frame, text="Ładowanie modeli...", 
                                     style='Info.TLabel')
        self.status_label.pack(side=tk.RIGHT)
        
        # === PANEL BOCZNY ===
        sidebar_frame = ttk.LabelFrame(main_frame, text="Ustawienia", padding="10")
        sidebar_frame.grid(row=1, column=0, rowspan=2, sticky=(tk.W, tk.N, tk.S), 
                          padx=(0, 10))
        
        # Wybór modelu
        ttk.Label(sidebar_frame, text="Wybierz model:").pack(anchor=tk.W, pady=(0, 5))
        self.model_combo = ttk.Combobox(sidebar_frame, textvariable=self.selected_model,
                                       state="readonly", width=30)
        self.model_combo.pack(anchor=tk.W, pady=(0, 10))
        
        # Wybór języka testów
        lang_frame = ttk.Frame(sidebar_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(lang_frame, text="🌍 Język testów:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(0, 2))
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.selected_language,
                                          state="readonly", width=28)
        self.language_combo.pack(anchor=tk.W)
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_changed)
        
        # Opcja sędziego LLM
        judge_frame = ttk.Frame(sidebar_frame)
        judge_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.judge_checkbox = ttk.Checkbutton(
            judge_frame, 
            text="🤖 Sędzia AI (Gemini)", 
            variable=self.use_judge,
            command=self.on_judge_changed
        )
        self.judge_checkbox.pack(anchor=tk.W)
        
        # Status sędziego
        self.judge_status_var = tk.StringVar(value="🤖 Sędzia AI wyłączony")
        self.judge_status_label = ttk.Label(
            judge_frame, 
            textvariable=self.judge_status_var,
            font=('Arial', 8),
            style='Info.TLabel'
        )
        self.judge_status_label.pack(anchor=tk.W, pady=(2, 0))
        
        ttk.Button(judge_frame, text="🔑 Klucz API", 
                  command=self.configure_gemini_api).pack(anchor=tk.W, pady=(2, 0))
        
        ttk.Separator(sidebar_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Przyciski akcji
        ttk.Button(sidebar_frame, text="🔄 Odśwież modele", 
                  command=self.load_models).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Separator(sidebar_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Zarządzanie czatem
        ttk.Label(sidebar_frame, text="Czat:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        ttk.Button(sidebar_frame, text="🗑️ Wyczyść czat", 
                  command=self.clear_chat).pack(fill=tk.X, pady=2)
        
        ttk.Button(sidebar_frame, text="💾 Zapisz czat", 
                  command=self.save_chat).pack(fill=tk.X, pady=2)
        
        ttk.Button(sidebar_frame, text="📁 Wczytaj czat", 
                  command=self.load_chat).pack(fill=tk.X, pady=2)
        
        # === GŁÓWNY OBSZAR ===
        # Notebook z zakładkami
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Zakładka czatu
        self.setup_chat_tab()
        
        # Zakładka testów
        self.setup_test_tab()
        
        # === PASEK STANU ===
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        self.progress_var = tk.StringVar(value="Gotowy")
        ttk.Label(status_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
    
    def setup_chat_tab(self):
        """Tworzy zakładkę czatu"""
        chat_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(chat_frame, text="💬 Czat")
        
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Obszar rozmowy
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, height=20, width=80,
            font=('Consolas', 10), state=tk.DISABLED
        )
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S),
                              pady=(0, 10))
        
        # Konfiguracja tagów dla kolorowania
        self.chat_display.tag_configure("user", foreground="blue", font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure("model", foreground="green")
        self.chat_display.tag_configure("system", foreground="gray", font=('Consolas', 9, 'italic'))
        self.chat_display.tag_configure("error", foreground="red")
        
        # Panel trybu systemowego
        system_frame = ttk.LabelFrame(chat_frame, text="🎭 Tryb systemowy (Persona)", padding="5")
        system_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        system_frame.columnconfigure(1, weight=1)
        
        ttk.Label(system_frame, text="Tryb:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.system_mode_combo = ttk.Combobox(
            system_frame, 
            textvariable=self.system_prompt_mode,
            values=list(self.system_prompt_modes.keys()),
            state="readonly",
            width=25
        )
        self.system_mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.system_mode_combo.bind('<<ComboboxSelected>>', self.on_system_mode_changed)
        
        self.edit_prompt_btn = ttk.Button(
            system_frame, 
            text="📝 Edytuj", 
            command=self.edit_system_prompt
        )
        self.edit_prompt_btn.grid(row=0, column=2, padx=(5, 0))
        
        self.clear_prompt_btn = ttk.Button(
            system_frame, 
            text="🗑️ Reset", 
            command=self.clear_system_prompt
        )
        self.clear_prompt_btn.grid(row=0, column=3, padx=(5, 0))
        
        # Pole wprowadzania
        input_frame = ttk.Frame(chat_frame)
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        input_frame.columnconfigure(0, weight=1)
        
        self.message_entry = tk.Text(input_frame, height=3, width=60, wrap=tk.WORD,
                                    font=('Arial', 10))
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Przycisk wysyłania
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.send_button = ttk.Button(button_frame, text="📤 Wyślij", 
                                     command=self.send_message)
        self.send_button.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(button_frame, text="🛑 Stop", 
                  command=self.stop_generation).pack(fill=tk.X)
        
        # Bind Enter do wysyłania (Ctrl+Enter)
        self.message_entry.bind("<Control-Return>", lambda e: self.send_message())
    
    def setup_test_tab(self):
        """Tworzy zakładkę testów"""
        test_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(test_frame, text="🧪 Testy")
        
        test_frame.columnconfigure(0, weight=1)
        test_frame.rowconfigure(1, weight=1)
        
        # Panel kontrolny testów
        control_frame = ttk.LabelFrame(test_frame, text="Kontrola testów", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        
        # Przyciski sterowania testami - zsynchronizowane z lewym panelem
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_quick_test_btn = ttk.Button(
            button_frame, 
            text="🚀 Szybki test", 
            command=self.run_quick_test_async
        )
        self.start_quick_test_btn.pack(side="left", padx=(0, 5))
        
        self.start_comprehensive_test_btn = ttk.Button(
            button_frame, 
            text="� Test kompletny", 
            command=self.run_comprehensive_test_async
        )
        self.start_comprehensive_test_btn.pack(side="left", padx=(0, 5))
        
        self.start_custom_test_btn = ttk.Button(
            button_frame, 
            text="❓ Własne pytanie", 
            command=self.ask_all_models_dialog
        )
        self.start_custom_test_btn.pack(side="left", padx=(0, 10))
        
        self.stop_test_btn = ttk.Button(
            button_frame, 
            text="🛑 Zatrzymaj", 
            command=self.stop_test,
            state="disabled"
        )
        self.stop_test_btn.pack(side="left")
        
        # Status testów
        self.test_status_var = tk.StringVar(value="Nie uruchomiono testów")
        ttk.Label(control_frame, text="Status:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(control_frame, textvariable=self.test_status_var,
                 style='Info.TLabel').grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Postęp testów
        ttk.Label(control_frame, text="Postęp:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.test_progress = ttk.Progressbar(control_frame, mode='determinate')
        self.test_progress.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(5, 0))
        
        # Wyniki testów
        self.test_display = scrolledtext.ScrolledText(
            test_frame, wrap=tk.WORD, height=25, width=80,
            font=('Consolas', 9), state=tk.DISABLED
        )
        self.test_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tagi dla wyników testów
        self.test_display.tag_configure("header", font=('Consolas', 11, 'bold'), foreground="blue")
        self.test_display.tag_configure("model", font=('Consolas', 10, 'bold'), foreground="purple")
        self.test_display.tag_configure("success", foreground="green")
        self.test_display.tag_configure("error", foreground="red")
        self.test_display.tag_configure("summary", font=('Consolas', 10, 'bold'), background="lightyellow")
        
        # Załaduj języki po utworzeniu interfejsu
        self.load_languages()
        
        # Inicjalizuj status sędziego na podstawie klucza API z ENV
        self.initialize_judge_status()

    def initialize_judge_status(self):
        """Inicjalizuje status sędziego na podstawie dostępności klucza API"""
        if self.gemini_api_key:
            self.use_judge.set(True)
            self.judge_status_var.set("✅ Gotowy (z ENV)")
            self.judge_status_label.config(style='Success.TLabel')
            self.status_label.config(text="🤖 Sędzia AI gotowy (klucz z ENV)", style='Success.TLabel')
        else:
            self.judge_status_var.set("🤖 Wyłączony")
            self.judge_status_label.config(style='Info.TLabel')

    def load_models(self):
        """Ładuje dostępne modele i języki"""
        def load_in_thread():
            try:
                self.root.after(0, lambda: self.status_label.config(text="Ładowanie modeli..."))
                models = get_available_models()
                
                if models:
                    self.root.after(0, lambda: self.update_models(models))
                else:
                    self.root.after(0, lambda: self.status_label.config(
                        text="❌ Brak dostępnych modeli", style='Error.TLabel'))
                    
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"❌ Błąd: {str(e)}", style='Error.TLabel'))
        
        threading.Thread(target=load_in_thread, daemon=True).start()
    
    def load_languages(self):
        """Ładuje dostępne języki testów"""
        try:
            languages = get_available_languages()
            language_options = [get_language_display_name(lang) for lang in languages]
            
            self.language_combo['values'] = language_options
            
            # Ustaw domyślny język (polski)
            if "Polish / Polski" in language_options:
                self.language_combo.set("Polish / Polski")
                self.selected_language_code = "polish"
            elif language_options:
                self.language_combo.current(0)
                # Mapowanie pierwszego dostępnego języka
                language_map = {
                    "English / Angielski": "english",
                    "Polish / Polski": "polish"
                }
                first_display = language_options[0]
                self.selected_language_code = language_map.get(first_display, "polish")
            else:
                # Fallback jeśli nie ma języków
                self.language_combo['values'] = ["Polish / Polski", "English / Angielski"]
                self.language_combo.set("Polish / Polski")
                self.selected_language_code = "polish"
                
        except Exception as e:
            print(f"Error loading languages: {e}")
            # Fallback setup
            self.language_combo['values'] = ["Polish / Polski", "English / Angielski"]
            self.language_combo.set("Polish / Polski")
            self.selected_language_code = "polish"
    
    def on_language_changed(self, event=None):
        """Obsługuje zmianę języka"""
        selected_display = self.selected_language.get()
        
        # Mapowanie wyświetlanych nazw na kody języków
        language_map = {
            "Polish / Polski": "polish",
            "English / Angielski": "english"
        }
        
        actual_language = language_map.get(selected_display, "polish")
        
        # Zapisz wybór użytkownika
        self.selected_language_code = actual_language
        
        # Opcjonalnie: powiadom o zmianie
        if hasattr(self, 'status_label'):
            lang_name = get_language_display_name(actual_language)
            self.status_label.config(text=f"🌍 Język testów: {lang_name}", style='Info.TLabel')
    
    def on_judge_changed(self):
        """Obsługuje zmianę stanu sędziego LLM"""
        if self.use_judge.get():
            if not self.gemini_api_key:
                self.judge_status_var.set("⚠️ Brak klucza API")
                self.judge_status_label.config(style='Warning.TLabel')
                self.status_label.config(
                    text="⚠️ Sędzia włączony, ale brak klucza API", 
                    style='Warning.TLabel'
                )
                # Pokaż dialog konfiguracji tylko jeśli nie ma klucza w ENV
                if not os.getenv("GEMINI_API_KEY"):
                    self.root.after(100, self.configure_gemini_api)
            else:
                self.judge_status_var.set("✅ Gotowy")
                self.judge_status_label.config(style='Success.TLabel')
                self.status_label.config(
                    text="🤖 Sędzia AI włączony", 
                    style='Success.TLabel'
                )
        else:
            self.judge_status_var.set("🤖 Wyłączony")
            self.judge_status_label.config(style='Info.TLabel')
            self.status_label.config(
                text="🤖 Sędzia AI wyłączony", 
                style='Info.TLabel'
            )
    
    def check_judge_status(self):
        """Sprawdza status sędziego i wyświetla odpowiedni komunikat"""
        if self.use_judge.get():
            if self.gemini_api_key:
                return True, "🤖 Sędzia AI gotowy"
            else:
                return False, "⚠️ Sędzia AI: brak klucza API"
        else:
            return False, "🤖 Sędzia AI wyłączony"

    def configure_gemini_api(self):
        """Dialog do konfiguracji klucza API Gemini"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Konfiguracja Sędziego AI (Gemini)")
        dialog.geometry("600x420")  # Powiększone z 500x300
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Wycentruj dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        ttk.Label(dialog, text="🤖 Konfiguracja Sędziego AI", 
                 font=('Arial', 12, 'bold')).pack(pady=15)
        
        ttk.Label(dialog, text="Klucz API Gemini:", 
                 font=('Arial', 10)).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        api_frame = ttk.Frame(dialog)
        api_frame.pack(fill=tk.X, padx=20, pady=5)
        
        api_entry = ttk.Entry(api_frame, width=60, show="*")  # Powiększone z 50
        api_entry.pack(fill=tk.X)
        api_entry.insert(0, self.gemini_api_key)
        api_entry.focus()
        
        info_text = """
ℹ️ Informacje:
• Sędzia AI ocenia odpowiedzi modeli w skali 1-5
• Wymaga klucza API Google Gemini
• Pobierz klucz z: https://makersuite.google.com/app/apikey
• Klucz jest przechowywany tylko w sesji (nie zapisywany na dysk)
• Bez klucza API sędzia nie będzie działać podczas testów
        """
        
        ttk.Label(dialog, text=info_text, justify=tk.LEFT,
                 font=('Arial', 9)).pack(anchor=tk.W, padx=20, pady=15)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=30)  # Zwiększone z 20
        
        def save_api_key():
            key = api_entry.get().strip()
            if key:
                self.gemini_api_key = key
                self.use_judge.set(True)
                self.judge_status_var.set("✅ Gotowy")
                self.judge_status_label.config(style='Success.TLabel')
                self.status_label.config(text="🤖 Sędzia AI skonfigurowany", style='Success.TLabel')
                dialog.destroy()
            else:
                messagebox.showerror("Błąd", "Wprowadź klucz API!")
        
        def disable_judge():
            self.gemini_api_key = ""
            self.use_judge.set(False)
            self.judge_status_var.set("🤖 Wyłączony")
            self.judge_status_label.config(style='Info.TLabel')
            self.status_label.config(text="🤖 Sędzia AI wyłączony", style='Info.TLabel')
            dialog.destroy()
        
        ttk.Button(button_frame, text="💾 Zapisz klucz", 
                  command=save_api_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Wyłącz sędziego", 
                  command=disable_judge).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🚫 Anuluj", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter
        api_entry.bind("<Return>", lambda e: save_api_key())
    
    def update_models(self, models):
        """Aktualizuje listę modeli w GUI"""
        self.models = models
        self.model_combo['values'] = models
        
        if models:
            self.model_combo.current(0)
            self.status_label.config(text=f"✅ Załadowano {len(models)} modeli", 
                                   style='Success.TLabel')
        else:
            self.status_label.config(text="❌ Brak modeli", style='Error.TLabel')
    
    def send_message(self):
        """Wysyła wiadomość do modelu"""
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return
        
        if not self.selected_model.get():
            messagebox.showerror("Błąd", "Wybierz model przed wysłaniem wiadomości!")
            return
        
        # Wyczyść pole wprowadzania
        self.message_entry.delete("1.0", tk.END)
        
        # Dodaj wiadomość użytkownika do czatu
        self.add_to_chat(f"[Ty]: {message}", "user")
        
        # Wyślij do modelu w osobnym wątku
        def send_in_thread():
            model = self.selected_model.get()
            self.root.after(0, lambda: self.add_to_chat(f"[{model}]: ", "model"))
            self.root.after(0, lambda: self.progress_var.set("Generowanie odpowiedzi..."))
            self.root.after(0, lambda: self.progress_bar.start())
            
            try:
                # Przygotuj plik czatu jeśli nie istnieje
                if not self.current_chat_file:
                    timestamp = get_timestamp()
                    safe_model = model.replace(':', '_')
                    self.current_chat_file = f"chat_{safe_model}_{timestamp}.txt"
                
                # Zapisz pytanie do pliku
                with open(self.current_chat_file, 'a', encoding='utf-8') as f:
                    f.write(f"[Ty]: {message}\n[{model}]: ")
                
                # Uzyskaj odpowiedź z promptem systemowym
                system_prompt = self.get_current_system_prompt()
                result = ask_ollama(
                    model, 
                    message, 
                    "Czat GUI", 
                    self.current_chat_file, 
                    temperature=0.7,
                    system_prompt=system_prompt
                )
                
                if result and 'response' in result:
                    response = result['response']
                    self.root.after(0, lambda: self.add_to_chat(response, "model"))
                else:
                    self.root.after(0, lambda: self.add_to_chat("❌ Błąd podczas generowania odpowiedzi", "error"))
                
            except Exception as e:
                self.root.after(0, lambda: self.add_to_chat(f"❌ Błąd: {str(e)}", "error"))
            
            finally:
                self.root.after(0, lambda: self.progress_bar.stop())
                self.root.after(0, lambda: self.progress_var.set("Gotowy"))
        
        threading.Thread(target=send_in_thread, daemon=True).start()
    
    def add_to_chat(self, text, tag=None):
        """Dodaje tekst do obszaru czatu"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text + "\n", tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def clear_chat(self):
        """Czyści obszar czatu"""
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz wyczyścić czat?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.current_chat_file = None
            self.add_to_chat("💬 Czat wyczyszczony", "system")
    
    def save_chat(self):
        """Zapisuje czat do pliku"""
        content = self.chat_display.get("1.0", tk.END)
        if not content.strip():
            messagebox.showwarning("Ostrzeżenie", "Czat jest pusty!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")],
            title="Zapisz czat"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Sukces", f"Czat zapisany do: {filename}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można zapisać pliku: {str(e)}")
    
    def load_chat(self):
        """Wczytuje czat z pliku"""
        filename = filedialog.askopenfilename(
            filetypes=[("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")],
            title="Wczytaj czat"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete("1.0", tk.END)
                self.chat_display.insert("1.0", content)
                self.chat_display.config(state=tk.DISABLED)
                
                messagebox.showinfo("Sukces", f"Czat wczytany z: {filename}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można wczytać pliku: {str(e)}")
    
    def on_system_mode_changed(self, event=None):
        """Obsługuje zmianę trybu systemowego"""
        selected_mode = self.system_prompt_mode.get()
        
        if selected_mode == "Własny prompt":
            # Jeśli wybrano własny prompt, otwórz dialog edycji
            self.edit_system_prompt()
        else:
            # Wyświetl informację o wybranym trybie
            if selected_mode != "Standardowy":
                prompt_text = self.system_prompt_modes[selected_mode]
                self.add_to_chat(f"🎭 Ustawiono tryb: {selected_mode}", "system")
                self.add_to_chat(f"💭 Prompt systemowy: {prompt_text[:100]}...", "system")
            else:
                self.add_to_chat("🎭 Tryb standardowy (bez promptu systemowego)", "system")
    
    def edit_system_prompt(self):
        """Dialog do edycji własnego promptu systemowego"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edycja trybu systemowego")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Wycentruj dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        ttk.Label(dialog, text="🎭 Edycja trybu systemowego (Persona)", 
                 font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Combo box z trybami
        mode_frame = ttk.Frame(dialog)
        mode_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(mode_frame, text="Predefiniowany tryb:").pack(anchor=tk.W)
        
        temp_mode_var = tk.StringVar(value=self.system_prompt_mode.get())
        mode_combo = ttk.Combobox(
            mode_frame, 
            textvariable=temp_mode_var,
            values=list(self.system_prompt_modes.keys()),
            state="readonly"
        )
        mode_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Obszar edycji prompta
        ttk.Label(dialog, text="Prompt systemowy:", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=20, pady=(20, 5))
        
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        prompt_text = scrolledtext.ScrolledText(
            text_frame, 
            height=12, 
            wrap=tk.WORD, 
            font=('Arial', 10)
        )
        prompt_text.pack(fill=tk.BOTH, expand=True)
        
        # Załaduj obecny prompt
        current_mode = self.system_prompt_mode.get()
        if current_mode == "Własny prompt":
            prompt_text.insert("1.0", self.custom_system_prompt)
        elif current_mode in self.system_prompt_modes:
            current_prompt = self.system_prompt_modes[current_mode]
            if current_prompt != "CUSTOM":
                prompt_text.insert("1.0", current_prompt)
        
        def on_mode_combo_changed(event=None):
            """Aktualizuje tekst prompta gdy zmieni się tryb"""
            selected = temp_mode_var.get()
            if selected in self.system_prompt_modes:
                prompt_value = self.system_prompt_modes[selected]
                if prompt_value == "CUSTOM":
                    prompt_text.delete("1.0", tk.END)
                    prompt_text.insert("1.0", self.custom_system_prompt)
                elif prompt_value:
                    prompt_text.delete("1.0", tk.END)
                    prompt_text.insert("1.0", prompt_value)
                else:  # Standardowy
                    prompt_text.delete("1.0", tk.END)
        
        mode_combo.bind('<<ComboboxSelected>>', on_mode_combo_changed)
        
        # Przyciski
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def save_prompt():
            new_mode = temp_mode_var.get()
            new_prompt = prompt_text.get("1.0", tk.END).strip()
            
            if new_mode == "Własny prompt":
                self.custom_system_prompt = new_prompt
                self.system_prompt_mode.set("Własny prompt")
                self.add_to_chat("🎭 Ustawiono własny tryb systemowy", "system")
                if new_prompt:
                    self.add_to_chat(f"💭 Prompt: {new_prompt[:100]}...", "system")
            else:
                self.system_prompt_mode.set(new_mode)
                if new_mode == "Standardowy":
                    self.add_to_chat("🎭 Przywrócono tryb standardowy", "system")
                else:
                    self.add_to_chat(f"🎭 Ustawiono tryb: {new_mode}", "system")
            
            dialog.destroy()
        
        def preview_prompt():
            """Podgląd aktualnego prompta"""
            current_prompt = prompt_text.get("1.0", tk.END).strip()
            if current_prompt:
                messagebox.showinfo("Podgląd prompta", f"Aktualny prompt systemowy:\n\n{current_prompt}")
            else:
                messagebox.showinfo("Podgląd prompta", "Brak prompta systemowego (tryb standardowy)")
        
        ttk.Button(button_frame, text="💾 Zapisz", 
                  command=save_prompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="👁️ Podgląd", 
                  command=preview_prompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Anuluj", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus na text area
        prompt_text.focus()
    
    def clear_system_prompt(self):
        """Resetuje tryb systemowy do standardowego"""
        self.system_prompt_mode.set("Standardowy")
        self.custom_system_prompt = ""
        self.add_to_chat("🎭 Zresetowano do trybu standardowego", "system")
    
    def get_current_system_prompt(self):
        """Zwraca aktualny prompt systemowy"""
        current_mode = self.system_prompt_mode.get()
        
        if current_mode == "Standardowy":
            return ""
        elif current_mode == "Własny prompt":
            return self.custom_system_prompt
        elif current_mode in self.system_prompt_modes:
            prompt = self.system_prompt_modes[current_mode]
            return prompt if prompt != "CUSTOM" else self.custom_system_prompt
        else:
            return ""
    
    def stop_generation(self):
        """Zatrzymuje generowanie odpowiedzi (placeholder)"""
        messagebox.showinfo("Info", "Funkcja zatrzymywania zostanie zaimplementowana w przyszłości")
    
    def ask_all_models_dialog(self):
        """Dialog do zadania pytania wszystkim modelom"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Pytanie do wszystkich modeli")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Wycentruj dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        ttk.Label(dialog, text="Wpisz pytanie do wszystkich modeli:",
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        prompt_text = tk.Text(text_frame, height=5, wrap=tk.WORD, font=('Arial', 10))
        prompt_text.pack(fill=tk.BOTH, expand=True)
        prompt_text.focus()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def submit():
            prompt = prompt_text.get("1.0", tk.END).strip()
            if prompt:
                dialog.destroy()
                self.ask_all_models(prompt)
            else:
                messagebox.showerror("Błąd", "Wpisz pytanie!")
        
        ttk.Button(button_frame, text="Wyślij", command=submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Anuluj", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter
        prompt_text.bind("<Control-Return>", lambda e: submit())
    
    def ask_all_models(self, prompt):
        """Zadaje pytanie wszystkim modelom"""
        if not self.models:
            messagebox.showerror("Błąd", "Brak dostępnych modeli!")
            return
        
        if self.is_testing:
            messagebox.showwarning("Ostrzeżenie", "Test już jest uruchomiony!")
            return
        
        # Ustaw stan testowania
        self.is_testing = True
        self.stop_testing = False
        self.update_test_buttons_state(testing=True)
        
        # Przełącz na zakładkę testów
        self.notebook.select(1)
        
        def test_in_thread():
            try:
                # Pobierz aktualnie wybrany język
                current_language = getattr(self, 'selected_language_code', 'polish')
                
                timestamp = get_timestamp()
                lang_suffix = f"_{current_language}" if current_language != "polish" else ""
                output_file = f"single_test{lang_suffix}_{timestamp}.txt"
                
                self.root.after(0, lambda: self.test_display.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.test_display.delete("1.0", tk.END))
                
                lang_name = get_language_display_name(current_language)
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"🚀 Test własnego pytania - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", "header"))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"Język: {lang_name}\n", "header"))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"Pytanie: {prompt}\n", "header"))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"Modele: {', '.join(self.models)}\n\n", "header"))
                
                self.root.after(0, lambda: self.test_progress.config(maximum=len(self.models)))
                
                for i, model in enumerate(self.models):
                    if self.stop_testing:
                        break
                        
                    self.root.after(0, lambda m=model: self.test_status_var.set(f"Testowanie: {m}"))
                    self.root.after(0, lambda i=i: self.test_progress.config(value=i))
                    
                    self.root.after(0, lambda m=model: self.test_display.insert(tk.END, 
                        f"🤖 Model: {m}\n", "model"))
                    
                    try:
                        test_name = "Single Question GUI" if current_language == "english" else "Pojedyncze pytanie GUI"
                        result = ask_ollama(model, prompt, test_name, output_file)
                        if result and 'response' in result:
                            response = result['response'][:500] + "..." if len(result['response']) > 500 else result['response']
                            self.root.after(0, lambda r=response: self.test_display.insert(tk.END, 
                                f"Odpowiedź: {r}\n\n", "success"))
                        else:
                            error_text = "❌ Error in response\n\n" if current_language == "english" else "❌ Błąd w odpowiedzi\n\n"
                            self.root.after(0, lambda: self.test_display.insert(tk.END, error_text, "error"))
                    except Exception as e:
                        error_prefix = "❌ Error: " if current_language == "english" else "❌ Błąd: "
                        self.root.after(0, lambda e=str(e): self.test_display.insert(tk.END, 
                            f"{error_prefix}{e}\n\n", "error"))
                    
                    if not self.stop_testing:
                        time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
                
                self.root.after(0, lambda: self.test_progress.config(value=len(self.models)))
                
                if self.stop_testing:
                    completion_text = "Test zatrzymany" if current_language == "polish" else "Test stopped"
                    saved_text = "Test zatrzymany!" if current_language == "polish" else "Test stopped!"
                else:
                    completion_text = "Test zakończony" if current_language == "polish" else "Test completed"
                    saved_text = "Test zakończony! Wyniki zapisane w:" if current_language == "polish" else "Test completed! Results saved in:"
                    
                self.root.after(0, lambda: self.test_status_var.set(completion_text))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"✅ {saved_text} {output_file}\n", "summary"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"❌ Krytyczny błąd: {str(e)}\n", "error"))
                self.root.after(0, lambda: self.test_status_var.set("Błąd testu"))
            
            finally:
                # Przywróć stan GUI
                self.is_testing = False
                self.stop_testing = False
                self.root.after(0, lambda: self.update_test_buttons_state(testing=False))
                self.root.after(0, lambda: self.test_display.config(state=tk.DISABLED))
                self.root.after(0, lambda: self.test_display.see(tk.END))
                self.root.after(0, lambda: self.status_label.config(text="✅ Gotowy", style='Success.TLabel'))
            
            timestamp = get_timestamp()
            lang_suffix = f"_{current_language}" if current_language != "polish" else ""
            output_file = f"single_test{lang_suffix}_{timestamp}.txt"
            
            self.root.after(0, lambda: self.test_display.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.test_display.delete("1.0", tk.END))
            
            lang_name = get_language_display_name(current_language)
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"🚀 Test własnego pytania - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", "header"))
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"Język: {lang_name}\n", "header"))
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"Pytanie: {prompt}\n", "header"))
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"Modele: {', '.join(self.models)}\n\n", "header"))
            
            self.root.after(0, lambda: self.test_progress.config(maximum=len(self.models)))
            
            for i, model in enumerate(self.models):
                self.root.after(0, lambda m=model: self.test_status_var.set(f"Testowanie: {m}"))
                self.root.after(0, lambda i=i: self.test_progress.config(value=i))
                
                self.root.after(0, lambda m=model: self.test_display.insert(tk.END, 
                    f"🤖 Model: {m}\n", "model"))
                
                try:
                    test_name = "Single Question GUI" if current_language == "english" else "Pojedyncze pytanie GUI"
                    result = ask_ollama(model, prompt, test_name, output_file)
                    if result and 'response' in result:
                        response = result['response'][:500] + "..." if len(result['response']) > 500 else result['response']
                        self.root.after(0, lambda r=response: self.test_display.insert(tk.END, 
                            f"Odpowiedź: {r}\n\n", "success"))
                    else:
                        error_text = "❌ Error in response\n\n" if current_language == "english" else "❌ Błąd w odpowiedzi\n\n"
                        self.root.after(0, lambda: self.test_display.insert(tk.END, error_text, "error"))
                except Exception as e:
                    error_prefix = "❌ Error: " if current_language == "english" else "❌ Błąd: "
                    self.root.after(0, lambda e=str(e): self.test_display.insert(tk.END, 
                        f"{error_prefix}{e}\n\n", "error"))
                
                time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
            
            self.root.after(0, lambda: self.test_progress.config(value=len(self.models)))
            completion_text = "Test completed" if current_language == "english" else "Test zakończony"
            saved_text = "Test completed! Results saved in:" if current_language == "english" else "Test zakończony! Wyniki zapisane w:"
            self.root.after(0, lambda: self.test_status_var.set(completion_text))
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"✅ {saved_text} {output_file}\n", "summary"))
            self.root.after(0, lambda: self.test_display.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.test_display.see(tk.END))
        
        threading.Thread(target=test_in_thread, daemon=True).start()
    
    def run_quick_test(self):
        """Uruchamia szybki test"""
        if not self.models:
            messagebox.showerror("Błąd", "Brak dostępnych modeli!")
            return
        
        # Pobierz aktualnie wybrany język
        current_language = getattr(self, 'selected_language_code', 'polish')
        test_prompts = get_test_prompts_by_language(current_language, "quick")
        self.run_test(test_prompts, "szybki", current_language)
    
    def run_comprehensive_test(self):
        """Uruchamia kompletny test"""
        if not self.models:
            messagebox.showerror("Błąd", "Brak dostępnych modeli!")
            return
        
        # Pobierz aktualnie wybrany język
        current_language = getattr(self, 'selected_language_code', 'polish')
        test_prompts = get_test_prompts_by_language(current_language, "comprehensive")
        self.run_test(test_prompts, "kompletny", current_language)
    
    def run_test(self, test_prompts, test_type, language="polish"):
        """Uruchamia test z podanymi promptami"""
        # Przełącz na zakładkę testów
        self.notebook.select(1)
        
        def test_in_thread():
            timestamp = get_timestamp()
            lang_suffix = f"_{language}" if language != "polish" else ""
            output_file = f"{test_type}_test{lang_suffix}_{timestamp}.txt"
            
            total_tests = len(test_prompts) * len(self.models)
            current_test = 0
            
            self.root.after(0, lambda: self.test_display.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.test_display.delete("1.0", tk.END))
            
            lang_name = get_language_display_name(language)
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"🚀 Test {test_type} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", "header"))
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"Język: {lang_name}\n", "header"))
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"Modele: {', '.join(self.models)}\n", "header"))
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"Zadania: {len(test_prompts)}\n\n", "header"))
            
            self.root.after(0, lambda: self.test_progress.config(maximum=total_tests))
            
            results = []
            
            for i, test in enumerate(test_prompts, 1):
                self.root.after(0, lambda t=test['name'], i=i: self.test_display.insert(tk.END, 
                    f"📝 Zadanie {i}: {t}\n", "header"))
                
                for j, model in enumerate(self.models, 1):
                    current_test += 1
                    self.root.after(0, lambda m=model, c=current_test, t=total_tests: 
                        self.test_status_var.set(f"Test {c}/{t}: {m}"))
                    self.root.after(0, lambda c=current_test: self.test_progress.config(value=c))
                    
                    self.root.after(0, lambda m=model: self.test_display.insert(tk.END, 
                        f"  🤖 {m}: ", "model"))
                    
                    try:
                        result = ask_ollama(model, test['prompt'], test['name'], output_file, 
                                          **test.get('options', {}))
                        if result:
                            results.append(result)
                            
                            # Używaj sędziego LLM jeśli włączony
                            if self.use_judge.get() and 'response' in result and self.gemini_api_key:
                                try:
                                    self.root.after(0, lambda: self.test_display.insert(tk.END, 
                                        "🔄 Ocena AI...", "model"))
                                    
                                    rating, justification = judge_with_gemini(
                                        result['response'],  # odpowiedź modelu
                                        test['prompt'],      # oryginalne pytanie  
                                        self.gemini_api_key  # klucz API
                                    )
                                    
                                    # Dodaj ocenę do wyniku
                                    result['judge_rating'] = rating
                                    result['judge_justification'] = justification
                                    
                                    self.root.after(0, lambda r=rating, j=justification: self.test_display.insert(tk.END, 
                                        f" ⭐{r}/5 [szczegóły]\n", "success"))
                                    
                                    # Dodaj uzasadnienie jako ukryty tekst (można rozwinąć klikając)
                                    # TODO: Implementować rozwijane szczegóły
                                    
                                except Exception as judge_error:
                                    self.root.after(0, lambda e=str(judge_error): self.test_display.insert(tk.END, 
                                        f" ❌ Błąd sędziego: {e[:50]}...\n", "error"))
                            else:
                                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                                    "✅ OK\n", "success"))
                        else:
                            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                                "❌ Błąd\n", "error"))
                    except Exception as e:
                        self.root.after(0, lambda e=str(e): self.test_display.insert(tk.END, 
                            f"❌ {e}\n", "error"))
                
                # Podsumowanie
                summary = generate_summary(results, output_file)
                
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"📊 PODSUMOWANIE:\n{summary}\n", "summary"))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"✅ Test zakończony! Wyniki zapisane w: {output_file}\n", "summary"))
            
            self.root.after(0, lambda: self.test_status_var.set("Test zakończony"))
            self.root.after(0, lambda: self.test_display.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.test_display.see(tk.END))
        
        threading.Thread(target=test_in_thread, daemon=True).start()
    
    def run_quick_test_async(self):
        """Uruchamia szybki test asynchronicznie z możliwością zatrzymania"""
        if self.is_testing:
            messagebox.showwarning("Ostrzeżenie", "Test już jest uruchomiony!")
            return
            
        if not self.models:
            messagebox.showerror("Błąd", "Brak dostępnych modeli!")
            return
        
        # Sprawdź czy sędzia jest włączony ale nie ma klucza API
        if self.use_judge.get() and not self.gemini_api_key:
            response = messagebox.askyesno(
                "Brak klucza API", 
                "Sędzia AI jest włączony, ale nie wprowadzono klucza API.\n"
                "Testy będą uruchomione bez oceny AI.\n\n"
                "Czy kontynuować?"
            )
            if not response:
                return
        
        # Ustaw stan testowania
        self.is_testing = True
        self.stop_testing = False
        self.update_test_buttons_state(testing=True)
        
        # Pobierz aktualnie wybrany język
        current_language = getattr(self, 'selected_language_code', 'polish')
        test_prompts = get_test_prompts_by_language(current_language, "quick")
        self.run_test_async(test_prompts, "szybki", current_language)
    
    def run_comprehensive_test_async(self):
        """Uruchamia test kompletny asynchronicznie z możliwością zatrzymania"""
        if self.is_testing:
            messagebox.showwarning("Ostrzeżenie", "Test już jest uruchomiony!")
            return
            
        if not self.models:
            messagebox.showerror("Błąd", "Brak dostępnych modeli!")
            return
        
        # Sprawdź czy sędzia jest włączony ale nie ma klucza API
        if self.use_judge.get() and not self.gemini_api_key:
            response = messagebox.askyesno(
                "Brak klucza API", 
                "Sędzia AI jest włączony, ale nie wprowadzono klucza API.\n"
                "Testy będą uruchomione bez oceny AI.\n\n"
                "Czy kontynuować?"
            )
            if not response:
                return
        
        # Ustaw stan testowania
        self.is_testing = True
        self.stop_testing = False
        self.update_test_buttons_state(testing=True)
        
        # Pobierz aktualnie wybrany język
        current_language = getattr(self, 'selected_language_code', 'polish')
        test_prompts = get_test_prompts_by_language(current_language, "comprehensive")
        self.run_test_async(test_prompts, "kompletny", current_language)
    
    def run_test_async(self, test_prompts, test_type, language="polish"):
        """Uruchamia test z podanymi promptami asynchronicznie z możliwością zatrzymania"""
        # Przełącz na zakładkę testów
        self.notebook.select(1)
        
        def test_in_thread():
            try:
                timestamp = get_timestamp()
                lang_suffix = f"_{language}" if language != "polish" else ""
                output_file = f"{test_type}_test{lang_suffix}_{timestamp}.txt"
                
                total_tests = len(test_prompts) * len(self.models)
                current_test = 0
                
                self.root.after(0, lambda: self.test_display.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.test_display.delete("1.0", tk.END))
                
                lang_name = get_language_display_name(language)
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"🚀 Test {test_type} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", "header"))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"Język: {lang_name}\n", "header"))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"Modele: {', '.join(self.models)}\n", "header"))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"Zadania: {len(test_prompts)}\n\n", "header"))
                
                self.root.after(0, lambda: self.test_progress.config(maximum=total_tests))
                
                results = []
                
                for i, test in enumerate(test_prompts, 1):
                    if self.stop_testing:
                        break
                        
                    self.root.after(0, lambda t=test['name'], i=i: self.test_display.insert(tk.END, 
                        f"📝 Zadanie {i}: {t}\n", "header"))
                    
                    for j, model in enumerate(self.models, 1):
                        if self.stop_testing:
                            break
                            
                        current_test += 1
                        self.root.after(0, lambda m=model, c=current_test, t=total_tests: 
                            self.test_status_var.set(f"Test {c}/{t}: {m}"))
                        self.root.after(0, lambda c=current_test: self.test_progress.config(value=c))
                        
                        self.root.after(0, lambda m=model: self.test_display.insert(tk.END, 
                            f"  🤖 {m}: ", "model"))
                        
                        try:
                            result = ask_ollama(model, test['prompt'], test['name'], output_file, 
                                              **test.get('options', {}))
                            if result:
                                results.append(result)
                                
                                # Używaj sędziego LLM jeśli włączony i dostępny
                                if self.use_judge.get() and 'response' in result and self.gemini_api_key:
                                    try:
                                        self.root.after(0, lambda: self.test_display.insert(tk.END, 
                                            "🔄 Ocena AI...", "model"))
                                        
                                        rating, justification = judge_with_gemini(
                                            result['response'],  # odpowiedź modelu
                                            test['prompt'],      # oryginalne pytanie  
                                            self.gemini_api_key  # klucz API
                                        )
                                        
                                        # Dodaj ocenę do wyniku
                                        result['judge_rating'] = rating
                                        result['judge_justification'] = justification
                                        
                                        self.root.after(0, lambda r=rating: self.test_display.insert(tk.END, 
                                            f" ⭐{r}/5\n", "success"))
                                        
                                    except Exception as judge_error:
                                        self.root.after(0, lambda e=str(judge_error): self.test_display.insert(tk.END, 
                                            f" ❌ Błąd sędziego: {e[:50]}...\n", "error"))
                                elif self.use_judge.get() and not self.gemini_api_key:
                                    self.root.after(0, lambda: self.test_display.insert(tk.END, 
                                        " ⚠️ Sędzia: brak klucza API\n", "error"))
                                else:
                                    self.root.after(0, lambda: self.test_display.insert(tk.END, 
                                        "✅ OK\n", "success"))
                            else:
                                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                                    "❌ Błąd\n", "error"))
                        except Exception as e:
                            self.root.after(0, lambda e=str(e): self.test_display.insert(tk.END, 
                                f"❌ {e}\n", "error"))
                        
                        if not self.stop_testing:
                            time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
                    
                    if not self.stop_testing:
                        self.root.after(0, lambda: self.test_display.insert(tk.END, "\n"))
                
                # Podsumowanie
                if self.stop_testing:
                    self.root.after(0, lambda: self.test_display.insert(tk.END, 
                        f"🛑 Test został zatrzymany przez użytkownika\n", "error"))
                    self.root.after(0, lambda: self.test_display.insert(tk.END, 
                        f"📊 Częściowe wyniki ({len(results)} testów):\n", "summary"))
                else:
                    self.root.after(0, lambda: self.test_display.insert(tk.END, 
                        f"📊 PODSUMOWANIE:\n", "summary"))
                
                if results:
                    summary = generate_summary(results, output_file)
                    self.root.after(0, lambda: self.test_display.insert(tk.END, 
                        f"{summary}\n", "summary"))
                    self.root.after(0, lambda: self.test_display.insert(tk.END, 
                        f"✅ Wyniki zapisane w: {output_file}\n", "summary"))
                
                final_status = "Test zatrzymany" if self.stop_testing else "Test zakończony"
                self.root.after(0, lambda: self.test_status_var.set(final_status))
                
            except Exception as e:
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"❌ Krytyczny błąd: {str(e)}\n", "error"))
                self.root.after(0, lambda: self.test_status_var.set("Błąd testu"))
            
            finally:
                # Przywróć stan GUI
                self.is_testing = False
                self.stop_testing = False
                self.root.after(0, lambda: self.update_test_buttons_state(testing=False))
                self.root.after(0, lambda: self.test_display.config(state=tk.DISABLED))
                self.root.after(0, lambda: self.test_display.see(tk.END))
                self.root.after(0, lambda: self.status_label.config(text="✅ Gotowy", style='Success.TLabel'))
        
        threading.Thread(target=test_in_thread, daemon=True).start()
    
    def update_test_buttons_state(self, testing=False):
        """Aktualizuje stan wszystkich przycisków testów"""
        if testing:
            # Podczas testowania - dezaktywuj przyciski start, aktywuj stop
            if hasattr(self, 'start_quick_test_btn'):
                self.start_quick_test_btn.config(state="disabled")
            if hasattr(self, 'start_comprehensive_test_btn'):
                self.start_comprehensive_test_btn.config(state="disabled")
            if hasattr(self, 'start_custom_test_btn'):
                self.start_custom_test_btn.config(state="disabled")
            if hasattr(self, 'stop_test_btn'):
                self.stop_test_btn.config(state="normal")
        else:
            # Po zakończeniu testów - przywróć normalny stan
            if hasattr(self, 'start_quick_test_btn'):
                self.start_quick_test_btn.config(state="normal")
            if hasattr(self, 'start_comprehensive_test_btn'):
                self.start_comprehensive_test_btn.config(state="normal")
            if hasattr(self, 'start_custom_test_btn'):
                self.start_custom_test_btn.config(state="normal")
            if hasattr(self, 'stop_test_btn'):
                self.stop_test_btn.config(state="disabled")

    def stop_generation(self):
        """Zatrzymuje generowanie odpowiedzi (placeholder)"""
        messagebox.showinfo("Info", "Funkcja zatrzymywania zostanie zaimplementowana w przyszłości")
    
    def ask_all_models_dialog(self):
        """Dialog do zadania pytania wszystkim modelom"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Pytanie do wszystkich modeli")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Wycentruj dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        ttk.Label(dialog, text="Wpisz pytanie do wszystkich modeli:",
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        prompt_text = tk.Text(text_frame, height=5, wrap=tk.WORD, font=('Arial', 10))
        prompt_text.pack(fill=tk.BOTH, expand=True)
        prompt_text.focus()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def submit():
            prompt = prompt_text.get("1.0", tk.END).strip()
            if prompt:
                dialog.destroy()
                self.ask_all_models(prompt)
            else:
                messagebox.showerror("Błąd", "Wpisz pytanie!")
        
        ttk.Button(button_frame, text="Wyślij", command=submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Anuluj", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter
        prompt_text.bind("<Control-Return>", lambda e: submit())
    
    def ask_all_models(self, prompt):
        """Zadaje pytanie wszystkim modelom"""
        if not self.models:
            messagebox.showerror("Błąd", "Brak dostępnych modeli!")
            return
        
        if self.is_testing:
            messagebox.showwarning("Ostrzeżenie", "Test już jest uruchomiony!")
            return
        
        # Ustaw stan testowania
        self.is_testing = True
        self.stop_testing = False
        self.update_test_buttons_state(testing=True)
        
        # Przełącz na zakładkę testów
        self.notebook.select(1)
        
        def test_in_thread():
            try:
                # Pobierz aktualnie wybrany język
                current_language = getattr(self, 'selected_language_code', 'polish')
                
                timestamp = get_timestamp()
                lang_suffix = f"_{current_language}" if current_language != "polish" else ""
                output_file = f"single_test{lang_suffix}_{timestamp}.txt"
                
                self.root.after(0, lambda: self.test_display.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.test_display.delete("1.0", tk.END))
                
                lang_name = get_language_display_name(current_language)
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"🚀 Test własnego pytania - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", "header"))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"Język: {lang_name}\n", "header"))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"Pytanie: {prompt}\n", "header"))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"Modele: {', '.join(self.models)}\n\n", "header"))
                
                self.root.after(0, lambda: self.test_progress.config(maximum=len(self.models)))
                
                for i, model in enumerate(self.models):
                    if self.stop_testing:
                        break
                        
                    self.root.after(0, lambda m=model: self.test_status_var.set(f"Testowanie: {m}"))
                    self.root.after(0, lambda i=i: self.test_progress.config(value=i))
                    
                    self.root.after(0, lambda m=model: self.test_display.insert(tk.END, 
                        f"🤖 Model: {m}\n", "model"))
                    
                    try:
                        test_name = "Single Question GUI" if current_language == "english" else "Pojedyncze pytanie GUI"
                        result = ask_ollama(model, prompt, test_name, output_file)
                        if result and 'response' in result:
                            response = result['response'][:500] + "..." if len(result['response']) > 500 else result['response']
                            self.root.after(0, lambda r=response: self.test_display.insert(tk.END, 
                                f"Odpowiedź: {r}\n\n", "success"))
                        else:
                            error_text = "❌ Error in response\n\n" if current_language == "english" else "❌ Błąd w odpowiedzi\n\n"
                            self.root.after(0, lambda: self.test_display.insert(tk.END, error_text, "error"))
                    except Exception as e:
                        error_prefix = "❌ Error: " if current_language == "english" else "❌ Błąd: "
                        self.root.after(0, lambda e=str(e): self.test_display.insert(tk.END, 
                            f"{error_prefix}{e}\n\n", "error"))
                    
                    if not self.stop_testing:
                        time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
                
                self.root.after(0, lambda: self.test_progress.config(value=len(self.models)))
                
                if self.stop_testing:
                    completion_text = "Test zatrzymany" if current_language == "polish" else "Test stopped"
                    saved_text = "Test zatrzymany!" if current_language == "polish" else "Test stopped!"
                else:
                    completion_text = "Test zakończony" if current_language == "polish" else "Test completed"
                    saved_text = "Test zakończony! Wyniki zapisane w:" if current_language == "polish" else "Test completed! Results saved in:"
                    
                self.root.after(0, lambda: self.test_status_var.set(completion_text))
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"✅ {saved_text} {output_file}\n", "summary"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.test_display.insert(tk.END, 
                    f"❌ Krytyczny błąd: {str(e)}\n", "error"))
                self.root.after(0, lambda: self.test_status_var.set("Błąd testu"))
            
            finally:
                # Przywróć stan GUI
                self.is_testing = False
                self.stop_testing = False
                self.root.after(0, lambda: self.update_test_buttons_state(testing=False))
                self.root.after(0, lambda: self.test_display.config(state=tk.DISABLED))
                self.root.after(0, lambda: self.test_display.see(tk.END))
                self.root.after(0, lambda: self.status_label.config(text="✅ Gotowy", style='Success.TLabel'))
            
            timestamp = get_timestamp()
            lang_suffix = f"_{current_language}" if current_language != "polish" else ""
            output_file = f"single_test{lang_suffix}_{timestamp}.txt"
            
            self.root.after(0, lambda: self.test_display.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.test_display.delete("1.0", tk.END))
            
            lang_name = get_language_display_name(current_language)
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"🚀 Test własnego pytania - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", "header"))
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"Język: {lang_name}\n", "header"))
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"Pytanie: {prompt}\n", "header"))
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"Modele: {', '.join(self.models)}\n\n", "header"))
            
            self.root.after(0, lambda: self.test_progress.config(maximum=len(self.models)))
            
            for i, model in enumerate(self.models):
                self.root.after(0, lambda m=model: self.test_status_var.set(f"Testowanie: {m}"))
                self.root.after(0, lambda i=i: self.test_progress.config(value=i))
                
                self.root.after(0, lambda m=model: self.test_display.insert(tk.END, 
                    f"🤖 Model: {m}\n", "model"))
                
                try:
                    test_name = "Single Question GUI" if current_language == "english" else "Pojedyncze pytanie GUI"
                    result = ask_ollama(model, prompt, test_name, output_file)
                    if result and 'response' in result:
                        response = result['response'][:500] + "..." if len(result['response']) > 500 else result['response']
                        self.root.after(0, lambda r=response: self.test_display.insert(tk.END, 
                            f"Odpowiedź: {r}\n\n", "success"))
                    else:
                        error_text = "❌ Error in response\n\n" if current_language == "english" else "❌ Błąd w odpowiedzi\n\n"
                        self.root.after(0, lambda: self.test_display.insert(tk.END, error_text, "error"))
                except Exception as e:
                    error_prefix = "❌ Error: " if current_language == "english" else "❌ Błąd: "
                    self.root.after(0, lambda e=str(e): self.test_display.insert(tk.END, 
                        f"{error_prefix}{e}\n\n", "error"))
                
                time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
            
            self.root.after(0, lambda: self.test_progress.config(value=len(self.models)))
            completion_text = "Test completed" if current_language == "english" else "Test zakończony"
            saved_text = "Test completed! Results saved in:" if current_language == "english" else "Test zakończony! Wyniki zapisane w:"
            self.root.after(0, lambda: self.test_status_var.set(completion_text))
            self.root.after(0, lambda: self.test_display.insert(tk.END, 
                f"✅ {saved_text} {output_file}\n", "summary"))
            self.root.after(0, lambda: self.test_display.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.test_display.see(tk.END))
        
        threading.Thread(target=test_in_thread, daemon=True).start()
    
    def monitor_queue(self):
        """Monitoruje kolejkę wiadomości"""
        try:
            while True:
                message = self.test_queue.get_nowait()
                # Przetwarzaj wiadomości z kolejki
                pass
        except:
            pass
        
        # Planuj następne sprawdzenie
        self.root.after(100, self.monitor_queue)

def main():
    """Główna funkcja aplikacji GUI"""
    root = tk.Tk()
    app = OllamaGUI(root)
    
    # Obsługa zamykania
    def on_closing():
        if messagebox.askokcancel("Wyjście", "Czy na pewno chcesz zamknąć aplikację?"):
            root.quit()
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()


if __name__ == "__main__":
    main()
