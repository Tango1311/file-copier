import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil
import os
import threading

class FileCopier:
    def __init__(self, root):
        self.root = root
        self.root.title("Копирование файлов - Вариант 9")
        self.root.geometry("600x450")
        
        # Выбор исходного файла
        tk.Label(root, text="Выберите файл для копирования:").pack(pady=5)
        self.source_frame = tk.Frame(root)
        self.source_frame.pack(pady=5)
        self.source_entry = tk.Entry(self.source_frame, width=50)
        self.source_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(self.source_frame, text="Обзор", command=self.select_source).pack(side=tk.LEFT)
        
        # Выбор папки назначения
        tk.Label(root, text="Выберите папку назначения:").pack(pady=5)
        self.dest_frame = tk.Frame(root)
        self.dest_frame.pack(pady=5)
        self.dest_entry = tk.Entry(self.dest_frame, width=50)
        self.dest_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(self.dest_frame, text="Обзор", command=self.select_destination).pack(side=tk.LEFT)
        
        # Прогресс-бар
        tk.Label(root, text="Прогресс:").pack(pady=(10,0))
        self.progress = ttk.Progressbar(root, length=400, mode='indeterminate')
        self.progress.pack(pady=5)
        
        # Кнопка копирования
        self.copy_button = tk.Button(root, text="Копировать", command=self.copy_file, 
                                       bg="green", fg="white", padx=20, pady=10)
        self.copy_button.pack(pady=20)
        
        # Статус
        self.status_label = tk.Label(root, text="Готов", fg="blue")
        self.status_label.pack(pady=10)
    
    def select_source(self):
        filename = filedialog.askopenfilename(title="Выберите файл")
        if filename:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, filename)
    
    def select_destination(self):
        folder = filedialog.askdirectory(title="Выберите папку")
        if folder:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder)
    
    def copy_file_thread(self, source, dest_path):
        try:
            self.progress.start(10)
            shutil.copy2(source, dest_path)
            self.progress.stop()
            self.root.after(0, self.copy_success, dest_path)
        except Exception as e:
            self.root.after(0, self.copy_error, str(e))
    
    def copy_success(self, dest_path):
        self.copy_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"Скопировано: {dest_path}", fg="green")
        messagebox.showinfo("Успех", f"Файл скопирован!")
    
    def copy_error(self, error_msg):
        self.copy_button.config(state=tk.NORMAL)
        self.progress.stop()
        self.status_label.config(text=f"Ошибка: {error_msg}", fg="red")
        messagebox.showerror("Ошибка", error_msg)
    
    def copy_file(self):
        source = self.source_entry.get()
        destination = self.dest_entry.get()
        
        if not source:
            self.status_label.config(text="Выберите файл!", fg="red")
            return
        if not destination:
            self.status_label.config(text="Выберите папку!", fg="red")
            return
        if not os.path.exists(source):
            self.status_label.config(text="Файл не найден!", fg="red")
            return
        
        try:
            if not os.path.exists(destination):
                os.makedirs(destination)
            
            filename = os.path.basename(source)
            dest_path = os.path.join(destination, filename)
            
            self.copy_button.config(state=tk.DISABLED)
            self.status_label.config(text="Копирование...", fg="orange")
            
            thread = threading.Thread(target=self.copy_file_thread, args=(source, dest_path))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.copy_button.config(state=tk.NORMAL)
            self.status_label.config(text=f"Ошибка: {str(e)}", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCopier(root)
    root.mainloop()