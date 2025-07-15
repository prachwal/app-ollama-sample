"""
Chat Component for Ollama GUI
=============================
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from datetime import datetime

from ..config import CHAT_TAGS, SYSTEM_PROMPT_MODES


class ChatComponent:
    """Komponent odpowiedzialny za zakładkę czatu"""
    
    def __init__(self, parent_gui, notebook):
        self.parent = parent_gui
        self.notebook = notebook
        self.current_chat_file = None
        
        # Zmienne dla trybu systemowego
        self.system_prompt_mode = tk.StringVar(value="Standardowy")
        self.custom_system_prompt = ""
        
        self.setup_chat_tab()
    
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
        for tag, config in CHAT_TAGS.items():
            self.chat_display.tag_configure(tag, **config)
        
        # Panel trybu systemowego
        self.setup_system_prompt_panel(chat_frame)
        
        # Pole wprowadzania
        self.setup_input_area(chat_frame)
    
    def setup_system_prompt_panel(self, parent):
        """Tworzy panel trybu systemowego"""
        system_frame = ttk.LabelFrame(parent, text="🎭 Tryb systemowy (Persona)", padding="5")
        system_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        system_frame.columnconfigure(1, weight=1)
        
        ttk.Label(system_frame, text="Tryb:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.system_mode_combo = ttk.Combobox(
            system_frame, 
            textvariable=self.system_prompt_mode,
            values=list(SYSTEM_PROMPT_MODES.keys()),
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
    
    def setup_input_area(self, parent):
        """Tworzy obszar wprowadzania wiadomości"""
        input_frame = ttk.Frame(parent)
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
    
    def send_message(self):
        """Wysyła wiadomość do modelu"""
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return
        
        if not self.parent.selected_model.get():
            messagebox.showerror("Błąd", "Wybierz model przed wysłaniem wiadomości!")
            return
        
        # Wyczyść pole wprowadzania
        self.message_entry.delete("1.0", tk.END)
        
        # Dodaj wiadomość użytkownika do czatu
        self.add_to_chat(f"[Ty]: {message}", "user")
        
        # Wyślij do modelu w osobnym wątku
        def send_in_thread():
            model = self.parent.selected_model.get()
            self.parent.root.after(0, lambda: self.add_to_chat(f"[{model}]: ", "model"))
            self.parent.root.after(0, lambda: self.parent.progress_var.set("Generowanie odpowiedzi..."))
            self.parent.root.after(0, lambda: self.parent.progress_bar.start())
            
            try:
                # Przygotuj plik czatu jeśli nie istnieje
                if not self.current_chat_file:
                    from src.utils import get_timestamp
                    timestamp = get_timestamp()
                    safe_model = model.replace(':', '_')
                    self.current_chat_file = f"chat_{safe_model}_{timestamp}.txt"
                
                # Zapisz pytanie do pliku
                with open(self.current_chat_file, 'a', encoding='utf-8') as f:
                    f.write(f"[Ty]: {message}\n[{model}]: ")
                
                # Uzyskaj odpowiedź z promptem systemowym
                from src.api import ask_ollama
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
                    self.parent.root.after(0, lambda: self.add_to_chat(response, "model"))
                else:
                    self.parent.root.after(0, lambda: self.add_to_chat("❌ Błąd podczas generowania odpowiedzi", "error"))
                
            except Exception as e:
                self.parent.root.after(0, lambda: self.add_to_chat(f"❌ Błąd: {str(e)}", "error"))
            
            finally:
                self.parent.root.after(0, lambda: self.parent.progress_bar.stop())
                self.parent.root.after(0, lambda: self.parent.progress_var.set("Gotowy"))
        
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
    
    def stop_generation(self):
        """Zatrzymuje generowanie odpowiedzi (placeholder)"""
        messagebox.showinfo("Info", "Funkcja zatrzymywania zostanie zaimplementowana w przyszłości")
    
    def on_system_mode_changed(self, event=None):
        """Obsługuje zmianę trybu systemowego"""
        selected_mode = self.system_prompt_mode.get()
        
        if selected_mode == "Własny prompt":
            # Jeśli wybrano własny prompt, otwórz dialog edycji
            self.edit_system_prompt()
        else:
            # Wyświetl informację o wybranym trybie
            if selected_mode != "Standardowy":
                prompt_text = SYSTEM_PROMPT_MODES[selected_mode]
                self.add_to_chat(f"🎭 Ustawiono tryb: {selected_mode}", "system")
                self.add_to_chat(f"💭 Prompt systemowy: {prompt_text[:100]}...", "system")
            else:
                self.add_to_chat("🎭 Tryb standardowy (bez promptu systemowego)", "system")
    
    def edit_system_prompt(self):
        """Dialog do edycji własnego promptu systemowego"""
        from ..dialogs.system_prompt_dialog import SystemPromptDialog
        dialog = SystemPromptDialog(self.parent.root, self)
        dialog.show()
    
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
        elif current_mode in SYSTEM_PROMPT_MODES:
            prompt = SYSTEM_PROMPT_MODES[current_mode]
            return prompt if prompt != "CUSTOM" else self.custom_system_prompt
        else:
            return ""
