import os
import zipfile
from io import StringIO
from contextlib import redirect_stdout
from typing import Callable, Optional, Any
from datetime import date

def run_tests(tests_path: Optional[str] = None) -> Callable:
    """
    Запускаем тесты из zip архива или папки с тестами.
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)
        if tests_path is not None:
            tests_dir = os.path.join(os.path.dirname(tests_path), os.path.basename(tests_path).split('.')[0])
            if tests_path.endswith('zip'):
                with zipfile.ZipFile(tests_path, 'r') as zip_ref:
                    zip_ref.extractall(tests_dir)
            # запускаем тестовые данные
            no_wrong_answers = True
            test_pairs = tuple(file for file in sorted(os.listdir(tests_dir), key=lambda x: int(x.split('.')[0])) if os.path.basename(file).isdigit())
            for test_num in test_pairs:
                print(f'\n\033[1mRunning test {test_num}...\033[0m')
                with (
                    open(os.path.join(tests_dir, test_num), 'r', encoding='utf-8') as test_ref,
                    open(os.path.join(tests_dir, test_num + '.clue'), 'r', encoding='utf-8') as clue
                ):
                    test_code = test_ref.read()
                    with redirect_stdout(StringIO()) as f:
                        exec(test_code.replace(func.__name__, 'func'))
                    checked_value = clue.read()
                    if (f.getvalue().strip() == checked_value) == True:
                        print('\033[34mТЕСТ ПРОЙДЕН\033[0m')
                    else:
                        print('\033[31mТЕСТ ПРОВАЛЕН\033[0m')
                        print(f'Во время исполнения кода:\n{test_code}')
                        print(f'\nОжидаемый результат:\n{checked_value}\n')
                        no_wrong_answers = False
                        break
                    f.truncate(0)
            if no_wrong_answers:
                print('\033[34mВСЕ ТЕСТЫ ПРОЙДЕНЫ\033[0m')
                add_log(tests_path)
        return wrapper
    return decorator


def add_log(log_path):
    log_path = log_path.rstrip('.zip')
    path_parts = log_path.split('\\')
    log_text = f'{path_parts[2]} - {path_parts[3]} выполнена '
    with open(f'{path_parts[0]}\\Лог прохождения курса.txt', 'a+', encoding='utf-8') as log:
        log.seek(0)
        if log_text not in log.read():
            log.write(log_text+str(date.today().strftime('%d.%m.%Y'))+'\n')
            print('Задание записано в лог')
