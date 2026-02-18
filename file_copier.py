#!/usr/bin/env python3
"""
Скрипт для копирования конкретного файла по пути папки в локальный репозиторий
Вариант 9 из лабораторной работы
"""

import os
import shutil
import sys
from pathlib import Path
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class FileCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Копировщик файлов в репозиторий")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Переменные
        self.source_file = tk.StringVar()
        self.repo_path = tk.StringVar()
        self.dest_folder = tk.StringVar(value="copied_files")
        self.copy_history = []
        
        # Стили
        self.root.configure(bg='#f0f0f0')
        
        self.setup_ui()
        self.load_history()
    
    def setup_ui(self):
        """Создание интерфейса"""
        
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text="Копирование файлов в локальный репозиторий Git",
            font=("Arial", 14, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        title_label.pack(pady=10)
        
        # Основной фрейм
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Выбор исходного файла
        file_frame = tk.LabelFrame(main_frame, text="Исходный файл", bg='#f0f0f0', padx=10, pady=10)
        file_frame.pack(fill=tk.X, pady=5)
        
        tk.Entry(file_frame, textvariable=self.source_file, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(
            file_frame, 
            text="Обзор...", 
            command=self.select_source_file,
            bg='#4CAF50',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        # Выбор папки репозитория
        repo_frame = tk.LabelFrame(main_frame, text="Папка локального репозитория", bg='#f0f0f0', padx=10, pady=10)
        repo_frame.pack(fill=tk.X, pady=5)
        
        tk.Entry(repo_frame, textvariable=self.repo_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(
            repo_frame, 
            text="Обзор...", 
            command=self.select_repo_folder,
            bg='#2196F3',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        # Папка назначения внутри репозитория
        dest_frame = tk.LabelFrame(main_frame, text="Папка назначения (внутри репозитория)", bg='#f0f0f0', padx=10, pady=10)
        dest_frame.pack(fill=tk.X, pady=5)
        
        tk.Entry(dest_frame, textvariable=self.dest_folder, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(
            dest_frame, 
            text="Создать", 
            command=self.create_dest_folder,
            bg='#FF9800',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        # Кнопка копирования
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Копировать файл в репозиторий",
            command=self.copy_file,
            bg='#9C27B0',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=20,
            pady=10
        ).pack()
        
        # Статус
        self.status_label = tk.Label(
            main_frame, 
            text="Готов к работе",
            bg='#f0f0f0',
            fg='#666'
        )
        self.status_label.pack(pady=5)
        
        # История копирований
        history_frame = tk.LabelFrame(main_frame, text="История копирований", bg='#f0f0f0', padx=10, pady=10)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Создаем текстовое поле с прокруткой для истории
        text_frame = tk.Frame(history_frame, bg='#f0f0f0')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_text = tk.Text(
            text_frame,
            height=6,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9),
            bg='white',
            fg='#333'
        )
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.history_text.yview)
        
        # Кнопка очистки истории
        tk.Button(
            history_frame,
            text="Очистить историю",
            command=self.clear_history,
            bg='#f44336',
            fg='white',
            font=("Arial", 8)
        ).pack(pady=5)
    
    def select_source_file(self):
        """Выбор исходного файла"""
        filename = filedialog.askopenfilename(
            title="Выберите файл для копирования",
            filetypes=[("Все файлы", "*.*"), ("Текстовые файлы", "*.txt"), ("Python файлы", "*.py")]
        )
        if filename:
            self.source_file.set(filename)
            self.update_status(f"Выбран файл: {os.path.basename(filename)}")
    
    def select_repo_folder(self):
        """Выбор папки локального репозитория"""
        folder = filedialog.askdirectory(title="Выберите папку локального репозитория Git")
        if folder:
            # Проверяем, является ли папка Git репозиторием
            if self.is_git_repo(folder):
                self.repo_path.set(folder)
                self.update_status(f"Выбран Git репозиторий: {folder}")
            else:
                if messagebox.askyesno(
                    "Не Git репозиторий",
                    "Выбранная папка не является Git репозиторием. "
                    "Хотите инициализировать здесь Git репозиторий?"
                ):
                    self.init_git_repo(folder)
                    self.repo_path.set(folder)
                else:
                    messagebox.showwarning("Предупреждение", "Выберите папку с Git репозиторием")
    
    def is_git_repo(self, path):
        """Проверка, является ли папка Git репозиторием"""
        git_dir = os.path.join(path, '.git')
        return os.path.exists(git_dir) and os.path.isdir(git_dir)
    
    def init_git_repo(self, path):
        """Инициализация Git репозитория"""
        try:
            import subprocess
            subprocess.run(['git', 'init'], cwd=path, check=True, capture_output=True)
            self.update_status(f"Git репозиторий инициализирован в {path}")
            messagebox.showinfo("Успешно", f"Git репозиторий создан в {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось инициализировать Git: {e}")
    
    def create_dest_folder(self):
        """Создание папки назначения в репозитории"""
        if not self.repo_path.get():
            messagebox.showwarning("Предупреждение", "Сначала выберите папку репозитория")
            return
        
        folder_name = self.dest_folder.get().strip()
        if not folder_name:
            messagebox.showwarning("Предупреждение", "Введите имя папки")
            return
        
        full_path = os.path.join(self.repo_path.get(), folder_name)
        try:
            os.makedirs(full_path, exist_ok=True)
            self.update_status(f"Папка создана: {full_path}")
            messagebox.showinfo("Успешно", f"Папка создана: {full_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать папку: {e}")
    
    def copy_file(self):
        """Копирование файла в репозиторий"""
        # Проверка введенных данных
        if not self.source_file.get():
            messagebox.showwarning("Предупреждение", "Выберите файл для копирования")
            return
        
        if not self.repo_path.get():
            messagebox.showwarning("Предупреждение", "Выберите папку репозитория")
            return
        
        if not os.path.exists(self.source_file.get()):
            messagebox.showerror("Ошибка", "Исходный файл не существует")
            return
        
        if not os.path.exists(self.repo_path.get()):
            messagebox.showerror("Ошибка", "Папка репозитория не существует")
            return
        
        # Запускаем копирование в отдельном потоке
        thread = threading.Thread(target=self._copy_file_thread)
        thread.daemon = True
        thread.start()
    
    def _copy_file_thread(self):
        """Поток для копирования файла"""
        try:
            self.root.after(0, lambda: self.update_status("Копирование..."))
            
            source = self.source_file.get()
            repo = self.repo_path.get()
            dest_folder_name = self.dest_folder.get().strip() or "copied_files"
            
            # Создаем папку назначения
            dest_folder = os.path.join(repo, dest_folder_name)
            os.makedirs(dest_folder, exist_ok=True)
            
            # Определяем имя файла назначения
            original_name = os.path.basename(source)
            destination = os.path.join(dest_folder, original_name)
            
            # Копируем файл
            shutil.copy2(source, destination)
            
            # Добавляем в историю
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_size = os.path.getsize(destination)
            history_entry = {
                'timestamp': timestamp,
                'source': source,
                'destination': destination,
                'size': file_size
            }
            
            self.root.after(0, lambda: self.add_to_history(history_entry))
            self.root.after(0, lambda: self.update_status(f"Файл скопирован: {original_name} ({file_size} байт)"))
            self.root.after(0, lambda: messagebox.showinfo("Успешно", 
                f"Файл скопирован в репозиторий:\n{destination}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Ошибка: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось скопировать файл: {e}"))
    
    def add_to_history(self, entry):
        """Добавление записи в историю"""
        self.copy_history.append(entry)
        self.save_history()
        self.update_history_display()
    
    def update_history_display(self):
        """Обновление отображения истории"""
        self.history_text.delete(1.0, tk.END)
        for entry in reversed(self.copy_history[-10:]):  # Показываем последние 10 записей
            self.history_text.insert(tk.END, 
                f"[{entry['timestamp']}] {os.path.basename(entry['source'])} → "
                f"{os.path.basename(entry['destination'])} ({entry['size']} байт)\n"
            )
    
    def save_history(self):
        """Сохранение истории в файл"""
        try:
            import json
            history_file = os.path.join(os.path.expanduser("~"), ".file_copier_history.json")
            with open(history_file, 'w') as f:
                json.dump(self.copy_history, f, indent=2, default=str)
        except:
            pass
    
    def load_history(self):
        """Загрузка истории из файла"""
        try:
            import json
            history_file = os.path.join(os.path.expanduser("~"), ".file_copier_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    self.copy_history = json.load(f)
                self.update_history_display()
        except:
            self.copy_history = []
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Очистить историю копирований?"):
            self.copy_history = []
            self.save_history()
            self.update_history_display()
            self.update_status("История очищена")
    
    def update_status(self, message):
        """Обновление статуса"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = FileCopierApp(root)
    
    # Центрируем окно
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
