import os
import glob


def check_files_for_null_bytes():
    """Проверяет Python файлы на наличие null байтов"""
    python_files = glob.glob('**/*.py', recursive=True)

    damaged_files = []

    for file_path in python_files:
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                if b'\x00' in content:
                    damaged_files.append(file_path)
                    print(f'Найден поврежденный файл: {file_path}')
        except Exception as e:
            print(f'Ошибка при чтении {file_path}: {e}')

    return damaged_files


def fix_damaged_files(damaged_files):
    """Исправляет поврежденные файлы"""
    for file_path in damaged_files:
        try:
            # Создаем backup
            backup_path = file_path + '.backup'
            os.rename(file_path, backup_path)
            print(f'Создан backup: {backup_path}')

            # Читаем содержимое, игнорируя null байты
            with open(backup_path, 'rb') as f:
                content = f.read()

            # Удаляем null байты
            cleaned_content = content.replace(b'\x00', b'')

            # Записываем очищенное содержимое
            with open(file_path, 'wb') as f:
                f.write(cleaned_content)

            print(f'Исправлен: {file_path}')

        except Exception as e:
            print(f'Ошибка при исправлении {file_path}: {e}')


if __name__ == '__main__':
    print('Проверка файлов на null байты...')
    damaged = check_files_for_null_bytes()

    if damaged:
        print(f'\nНайдено поврежденных файлов: {len(damaged)}')
        fix_damaged_files(damaged)
        print('\nФайлы исправлены!')
    else:
        print('Поврежденных файлов не найдено.')
