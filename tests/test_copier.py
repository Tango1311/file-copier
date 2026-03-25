import unittest
import os
import tempfile
import shutil
import sys

# Добавляем путь к основному приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestFileCopier(unittest.TestCase):
    
    def setUp(self):
        """Создаём временные файлы и папки для тестов"""
        # Создаём временную папку
        self.test_dir = tempfile.mkdtemp()
        
        # Создаём тестовый файл
        self.source_file = os.path.join(self.test_dir, "test.txt")
        with open(self.source_file, "w") as f:
            f.write("Test content")
        
        # Создаём папку назначения
        self.dest_dir = os.path.join(self.test_dir, "dest")
        os.makedirs(self.dest_dir)
    
    def tearDown(self):
        """Удаляем временные файлы после тестов"""
        shutil.rmtree(self.test_dir)
    
    def test_file_exists(self):
        """Тест: проверяем, что файл существует"""
        self.assertTrue(os.path.exists(self.source_file))
    
    def test_destination_folder_created(self):
        """Тест: проверяем, что папка назначения создана"""
        self.assertTrue(os.path.exists(self.dest_dir))
    
    def test_file_copy_operation(self):
        """Тест: проверяем копирование файла"""
        import shutil
        
        dest_file = os.path.join(self.dest_dir, "test.txt")
        shutil.copy2(self.source_file, dest_file)
        
        self.assertTrue(os.path.exists(dest_file))
        
        # Проверяем содержимое
        with open(dest_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "Test content")
    
    def test_import_app(self):
        """Тест: проверяем, что приложение импортируется"""
        try:
            from file_copier import FileCopier
            self.assertTrue(True)
        except ImportError:
            self.fail("Не удалось импортировать FileCopier")

if __name__ == "__main__":
    unittest.main()