"""
Testing Component for Ollama GUI
=================================
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import json
from datetime import datetime

from ..config import TEST_CONFIG


class TestingComponent:
    """Komponent odpowiedzialny za zakładkę testów"""
    
    def __init__(self, parent_gui, notebook):
        self.parent = parent_gui
        self.notebook = notebook
        
        # Test variables
        self.test_type = tk.StringVar(value="SIMPLE")
        self.question_input = ""
        self.expected_response = ""
        self.temperature = tk.DoubleVar(value=0.1)
        self.num_iterations = tk.IntVar(value=3)
        
        self.setup_test_tab()
    
    def setup_test_tab(self):
        """Tworzy zakładkę testów"""
        test_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(test_frame, text="🧪 Testy")
        
        test_frame.columnconfigure(0, weight=1)
        test_frame.rowconfigure(3, weight=1)
        
        # Typ testu
        test_type_frame = ttk.LabelFrame(test_frame, text="Typ testu", padding="5")
        test_type_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(test_type_frame, text="SIMPLE - Test podstawowy", 
                       variable=self.test_type, value="SIMPLE").pack(anchor=tk.W)
        ttk.Radiobutton(test_type_frame, text="EXPECTED - Test z oczekiwaną odpowiedzią", 
                       variable=self.test_type, value="EXPECTED").pack(anchor=tk.W)
        ttk.Radiobutton(test_type_frame, text="KEYWORD - Test obecności słów kluczowych", 
                       variable=self.test_type, value="KEYWORD").pack(anchor=tk.W)
        ttk.Radiobutton(test_type_frame, text="LENGTH - Test długości odpowiedzi", 
                       variable=self.test_type, value="LENGTH").pack(anchor=tk.W)
        
        # Parametry testu
        self.setup_test_parameters(test_frame)
        
        # Przyciski akcji
        self.setup_test_buttons(test_frame)
        
        # Wyniki testów
        self.setup_test_results(test_frame)
    
    def setup_test_parameters(self, parent):
        """Tworzy panel parametrów testu"""
        params_frame = ttk.LabelFrame(parent, text="Parametry testu", padding="5")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        params_frame.columnconfigure(1, weight=1)
        
        # Temperatura
        ttk.Label(params_frame, text="Temperatura:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        temp_frame = ttk.Frame(params_frame)
        temp_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        self.temp_scale = ttk.Scale(temp_frame, from_=0.0, to=2.0, 
                                   variable=self.temperature, orient=tk.HORIZONTAL)
        self.temp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.temp_label = ttk.Label(temp_frame, text="0.1")
        self.temp_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.temp_scale.configure(command=self.update_temp_label)
        
        # Liczba iteracji
        ttk.Label(params_frame, text="Iteracje:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        iterations_frame = ttk.Frame(params_frame)
        iterations_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.iterations_spinbox = ttk.Spinbox(iterations_frame, from_=1, to=10, 
                                             textvariable=self.num_iterations, width=10)
        self.iterations_spinbox.pack(side=tk.LEFT)
        
        ttk.Label(iterations_frame, text="(1-10 testów)").pack(side=tk.LEFT, padx=(5, 0))
    
    def setup_test_buttons(self, parent):
        """Tworzy przyciski akcji"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(buttons_frame, text="🏃 Uruchom Test Szybki", 
                  command=self.run_quick_test).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="⚙️ Utwórz Test Własny", 
                  command=self.create_custom_test).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="📂 Wczytaj Test", 
                  command=self.load_test).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🗑️ Wyczyść Wyniki", 
                  command=self.clear_results).pack(side=tk.RIGHT)
    
    def setup_test_results(self, parent):
        """Tworzy obszar wyników testów"""
        results_frame = ttk.LabelFrame(parent, text="Wyniki testów", padding="5")
        results_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_display = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, height=15, width=80,
            font=('Consolas', 9), state=tk.DISABLED
        )
        self.results_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfiguracja tagów dla kolorowania wyników
        self.results_display.tag_configure("success", foreground="green", font=('Consolas', 9, 'bold'))
        self.results_display.tag_configure("warning", foreground="orange", font=('Consolas', 9, 'bold'))
        self.results_display.tag_configure("error", foreground="red", font=('Consolas', 9, 'bold'))
        self.results_display.tag_configure("info", foreground="blue", font=('Consolas', 9, 'bold'))
        self.results_display.tag_configure("header", foreground="purple", font=('Consolas', 9, 'bold'))
    
    def update_temp_label(self, value):
        """Aktualizuje etykietę temperatury"""
        self.temp_label.config(text=f"{float(value):.1f}")
    
    def add_to_results(self, text, tag=None):
        """Dodaje tekst do obszaru wyników"""
        self.results_display.config(state=tk.NORMAL)
        self.results_display.insert(tk.END, text + "\n", tag)
        self.results_display.see(tk.END)
        self.results_display.config(state=tk.DISABLED)
    
    def clear_results(self):
        """Czyści obszar wyników"""
        self.results_display.config(state=tk.NORMAL)
        self.results_display.delete("1.0", tk.END)
        self.results_display.config(state=tk.DISABLED)
        self.add_to_results("🗑️ Wyniki testów wyczyszczone", "info")
    
    def run_quick_test(self):
        """Uruchamia szybki test"""
        if not self.parent.selected_model.get():
            messagebox.showerror("Błąd", "Wybierz model przed uruchomieniem testu!")
            return
        
        # Dialog do wprowadzenia pytania testowego
        from ..dialogs.quick_test_dialog import QuickTestDialog
        dialog = QuickTestDialog(self.parent.root, self)
        dialog.show()
    
    def run_test_with_question(self, question):
        """Uruchamia test z podanym pytaniem"""
        if not question.strip():
            messagebox.showerror("Błąd", "Wprowadź pytanie testowe!")
            return
        
        def test_in_thread():
            model = self.parent.selected_model.get()
            iterations = self.num_iterations.get()
            temperature = self.temperature.get()
            
            # Aktualizuj status
            self.parent.root.after(0, lambda: self.parent.progress_var.set("Wykonywanie testów..."))
            self.parent.root.after(0, lambda: self.parent.progress_bar.start())
            
            # Dodaj nagłówek testu
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.parent.root.after(0, lambda: self.add_to_results(
                f"=" * 80, "header"
            ))
            self.parent.root.after(0, lambda: self.add_to_results(
                f"🧪 URUCHOMIONO TEST SZYBKI - {timestamp}", "header"
            ))
            self.parent.root.after(0, lambda: self.add_to_results(
                f"Model: {model} | Iteracje: {iterations} | Temperatura: {temperature}", "info"
            ))
            self.parent.root.after(0, lambda: self.add_to_results(
                f"Pytanie: {question}", "info"
            ))
            self.parent.root.after(0, lambda: self.add_to_results(
                f"=" * 80, "header"
            ))
            
            try:
                from src.api import ask_ollama
                
                results = []
                total_chars = 0
                
                for i in range(iterations):
                    self.parent.root.after(0, lambda i=i: self.add_to_results(
                        f"\n📋 ITERACJA {i+1}/{iterations}", "info"
                    ))
                    
                    try:
                        # Wykonaj pytanie
                        result = ask_ollama(
                            model, 
                            question, 
                            f"Test_{i+1}", 
                            None,  # Nie zapisuj do pliku podczas testów
                            temperature=temperature
                        )
                        
                        if result and 'response' in result:
                            response = result['response']
                            char_count = len(response)
                            word_count = len(response.split())
                            
                            results.append({
                                'iteration': i + 1,
                                'response': response,
                                'char_count': char_count,
                                'word_count': word_count
                            })
                            
                            total_chars += char_count
                            
                            # Wyświetl wynik
                            self.parent.root.after(0, lambda response=response, c=char_count, w=word_count: self.add_to_results(
                                f"✅ Odpowiedź ({c} znaków, {w} słów):", "success"
                            ))
                            self.parent.root.after(0, lambda response=response: self.add_to_results(
                                f"{response[:200]}{'...' if len(response) > 200 else ''}", None
                            ))
                        else:
                            self.parent.root.after(0, lambda i=i: self.add_to_results(
                                f"❌ Błąd w iteracji {i+1}: Brak odpowiedzi", "error"
                            ))
                            
                    except Exception as e:
                        self.parent.root.after(0, lambda e=e, i=i: self.add_to_results(
                            f"❌ Błąd w iteracji {i+1}: {str(e)}", "error"
                        ))
                
                # Podsumowanie
                if results:
                    avg_chars = total_chars / len(results)
                    char_counts = [r['char_count'] for r in results]
                    min_chars = min(char_counts)
                    max_chars = max(char_counts)
                    
                    self.parent.root.after(0, lambda: self.add_to_results(
                        f"\n📊 PODSUMOWANIE TESTU", "header"
                    ))
                    self.parent.root.after(0, lambda: self.add_to_results(
                        f"✅ Udane iteracje: {len(results)}/{iterations}", "success"
                    ))
                    self.parent.root.after(0, lambda: self.add_to_results(
                        f"📏 Długość odpowiedzi - Min: {min_chars}, Max: {max_chars}, Średnia: {avg_chars:.1f}", "info"
                    ))
                    self.parent.root.after(0, lambda: self.add_to_results(
                        f"🎯 Spójność długości: {'Wysoka' if (max_chars - min_chars) < avg_chars * 0.3 else 'Niska'}", 
                        "success" if (max_chars - min_chars) < avg_chars * 0.3 else "warning"
                    ))
                
            except Exception as e:
                self.parent.root.after(0, lambda: self.add_to_results(
                    f"❌ Krytyczny błąd testu: {str(e)}", "error"
                ))
            
            finally:
                self.parent.root.after(0, lambda: self.parent.progress_bar.stop())
                self.parent.root.after(0, lambda: self.parent.progress_var.set("Gotowy"))
        
        threading.Thread(target=test_in_thread, daemon=True).start()
    
    def create_custom_test(self):
        """Otwiera dialog tworzenia własnego testu"""
        from ..dialogs.custom_test_dialog import CustomTestDialog
        dialog = CustomTestDialog(self.parent.root, self)
        dialog.show()
    
    def load_test(self):
        """Wczytuje test z pliku JSON"""
        filename = filedialog.askopenfilename(
            filetypes=[("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*")],
            title="Wczytaj test"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                
                self.run_loaded_test(test_data, filename)
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można wczytać testu: {str(e)}")
    
    def run_loaded_test(self, test_data, filename):
        """Uruchamia test z wczytanych danych"""
        if not self.parent.selected_model.get():
            messagebox.showerror("Błąd", "Wybierz model przed uruchomieniem testu!")
            return
        
        def test_in_thread():
            model = self.parent.selected_model.get()
            
            self.parent.root.after(0, lambda: self.parent.progress_var.set("Wykonywanie testu..."))
            self.parent.root.after(0, lambda: self.parent.progress_bar.start())
            
            try:
                # Nagłówek
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.parent.root.after(0, lambda: self.add_to_results(
                    f"=" * 80, "header"
                ))
                self.parent.root.after(0, lambda: self.add_to_results(
                    f"📁 URUCHOMIONO TEST Z PLIKU - {timestamp}", "header"
                ))
                self.parent.root.after(0, lambda: self.add_to_results(
                    f"Plik: {os.path.basename(filename)}", "info"
                ))
                self.parent.root.after(0, lambda: self.add_to_results(
                    f"Model: {model}", "info"
                ))
                
                # Wykonaj test
                from src.testing.test_runner import TestRunner
                runner = TestRunner()
                
                # Uruchom test i zbierz wyniki
                results = runner.run_test(test_data, model)
                
                # Wyświetl wyniki
                for result in results:
                    status = "✅" if result.get('passed', False) else "❌"
                    self.parent.root.after(0, lambda r=result, s=status: self.add_to_results(
                        f"\n{s} Test: {r.get('description', 'Brak opisu')}", 
                        "success" if r.get('passed', False) else "error"
                    ))
                    
                    if 'details' in result:
                        self.parent.root.after(0, lambda r=result: self.add_to_results(
                            f"   {r['details']}", None
                        ))
                
                # Podsumowanie
                passed = sum(1 for r in results if r.get('passed', False))
                total = len(results)
                self.parent.root.after(0, lambda: self.add_to_results(
                    f"\n📊 PODSUMOWANIE: {passed}/{total} testów przeszło pomyślnie", 
                    "success" if passed == total else "warning"
                ))
                
            except Exception as e:
                self.parent.root.after(0, lambda: self.add_to_results(
                    f"❌ Błąd podczas wykonywania testu: {str(e)}", "error"
                ))
            
            finally:
                self.parent.root.after(0, lambda: self.parent.progress_bar.stop())
                self.parent.root.after(0, lambda: self.parent.progress_var.set("Gotowy"))
        
        threading.Thread(target=test_in_thread, daemon=True).start()
    
    def save_test_results(self):
        """Zapisuje wyniki testów do pliku"""
        content = self.results_display.get("1.0", tk.END)
        if not content.strip():
            messagebox.showwarning("Ostrzeżenie", "Brak wyników do zapisania!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")],
            title="Zapisz wyniki testów"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Sukces", f"Wyniki zapisane do: {filename}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można zapisać pliku: {str(e)}")
