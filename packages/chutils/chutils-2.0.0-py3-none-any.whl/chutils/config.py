"""
Модуль для работы с конфигурацией.

Обеспечивает автоматический поиск файла `config.yml`, `config.yaml` или `config.ini`
в корне проекта и предоставляет удобные функции для чтения настроек.
"""

import configparser
import logging
import os
import re
from pathlib import Path
from typing import Any, Optional, List, Dict

import yaml

# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)

# --- Глобальное состояние для "ленивой" инициализации ---
_BASE_DIR: Optional[str] = None
_CONFIG_FILE_PATH: Optional[str] = None
_paths_initialized = False

_config_object: Optional[Dict] = None
_config_loaded = False


def find_project_root(start_path: Path, markers: List[str]) -> Optional[Path]:
    """Ищет корень проекта, двигаясь вверх по дереву каталогов."""
    current_path = start_path.resolve()
    # Идем вверх до тех пор, пока не достигнем корня файловой системы
    while current_path != current_path.parent:
        for marker in markers:
            if (current_path / marker).exists():
                logger.debug(f"Найден маркер '{marker}' в директории: {current_path}")
                return current_path
        current_path = current_path.parent
    logger.debug("Корень проекта не найден.")
    return None


def _initialize_paths():
    """Автоматически находит и кэширует пути к корню проекта и файлу конфигурации."""
    global _BASE_DIR, _CONFIG_FILE_PATH, _paths_initialized
    if _paths_initialized:
        return

    # Приоритет поиска: сначала YAML, потом INI, потом общий маркер проекта.
    markers = ['config.yml', 'config.yaml', 'config.ini', 'pyproject.toml']
    project_root = find_project_root(Path.cwd(), markers)

    if project_root:
        _BASE_DIR = str(project_root)
        # Находим, какой именно конфигурационный файл был найден
        for marker in markers:
            if (project_root / marker).is_file() and marker.startswith('config'):
                _CONFIG_FILE_PATH = str(project_root / marker)
                break
        logger.info(f"Корень проекта автоматически определен: {_BASE_DIR}")
    else:
        logger.warning("Не удалось автоматически найти корень проекта.")

    _paths_initialized = True


def _get_config_path(cfg_file: Optional[str] = None) -> str:
    """
    Внутренняя функция-шлюз для получения пути к файлу конфигурации.

    Если путь не был установлен, запускает автоматический поиск.
    Если путь не передан явно и автоматический поиск не дал результатов,
    выбрасывает исключение с понятным сообщением.
    """
    # Если путь к файлу передан явно, используем его.
    if cfg_file:
        return cfg_file

    # Если пути еще не инициализированы, запускаем поиск.
    if not _paths_initialized:
        _initialize_paths()

    # Если после инициализации путь все еще не определен, это ошибка.
    if _CONFIG_FILE_PATH is None:
        raise FileNotFoundError(
            "Файл конфигурации не найден. Не удалось автоматически определить корень проекта. "
            "Убедитесь, что в корне вашего проекта есть 'config.yml' или 'config.ini' или 'pyproject.toml', "
            "либо укажите путь к конфигу вручную через chutils.init(base_dir=...)"
        )
    return _CONFIG_FILE_PATH


def get_config() -> Dict:
    """
    Загружает конфигурацию из файла (YAML или INI) и возвращает ее как словарь.
    Результат кэшируется для последующих вызовов.

    Returns:
        Dict: Загруженный объект конфигурации.
    """
    global _config_object, _config_loaded
    if _config_loaded and _config_object is not None:
        return _config_object

    path = _get_config_path()
    if not os.path.exists(path):
        logger.critical(f"Файл конфигурации НЕ НАЙДЕН: {path}")
        _config_object = {}
        _config_loaded = True
        return _config_object

    file_ext = Path(path).suffix.lower()

    try:
        with open(path, 'r', encoding='utf-8') as f:
            if file_ext in ['.yml', '.yaml']:
                _config_object = yaml.safe_load(f)
                logger.info(f"Конфигурация успешно загружена из YAML: {path}")
            elif file_ext == '.ini':
                parser = configparser.ConfigParser()
                parser.read_string(f.read())
                # Преобразуем объект ConfigParser в словарь
                _config_object = {s: dict(parser.items(s)) for s in parser.sections()}
                logger.info(f"Конфигурация успешно загружена из INI: {path}")
            else:
                _config_object = {}
                logger.warning(f"Неподдерживаемый формат файла конфигурации: {path}")

    except (yaml.YAMLError, configparser.Error) as e:
        logger.critical(f"Ошибка чтения файла конфигурации {path}: {e}")
        _config_object = {}

    if _config_object is None:
        _config_object = {}

    _config_loaded = True
    return _config_object


def save_config_value(section: str, key: str, value: str, cfg_file: Optional[str] = None) -> bool:
    """
    Сохраняет одно значение в конфигурационном файле.
    ВАЖНО: Эта функция работает только для файлов `.ini` и спроектирована так,
    чтобы сохранять комментарии и структуру исходного файла.
    При работе с `.yml` файлами она вернет `False`.
    """
    path = _get_config_path(cfg_file)
    file_ext = Path(path).suffix.lower()

    # Защита: работаем только с .ini файлами
    if file_ext != '.ini':
        logger.warning(f"Сохранение поддерживается только для .ini файлов. Файл {path} не будет изменен.")
        return False

    if not os.path.exists(path):
        logger.error(f"Невозможно сохранить значение: файл конфигурации {path} не найден.")
        return False

    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except IOError as e:
        logger.error(f"Ошибка чтения файла {path} для сохранения: {e}")
        return False

    updated = False
    in_target_section = False
    section_found = False
    key_found_in_section = False
    section_pattern = re.compile(r'^\s*\[\s*(?P<section_name>[^]]+)\s*\]\s*')
    key_pattern = re.compile(rf'^\s*({re.escape(key)})\s*=\s*(.*)', re.IGNORECASE)

    new_lines = []
    for line in lines:
        section_match = section_pattern.match(line)
        if section_match:
            current_section_name = section_match.group('section_name').strip()
            if current_section_name.lower() == section.lower():
                in_target_section = True
                section_found = True
            else:
                in_target_section = False
            new_lines.append(line)
            continue

        if in_target_section and not key_found_in_section:
            key_match = key_pattern.match(line)
            if key_match:
                original_key = key_match.group(1)
                new_line_content = f"{original_key} = {value}\n"
                new_lines.append(new_line_content)
                key_found_in_section = True
                updated = True
                logger.info(f"Ключ '{key}' в секции '[{section}]' будет обновлен на '{value}' в файле {path}")
                continue

        new_lines.append(line)

    if not section_found:
        logger.warning(f"Секция '[{section}]' не найдена в файле {path}. Значение НЕ сохранено.")
        return False
    if section_found and not key_found_in_section:
        logger.warning(f"Ключ '{key}' не найден в секции '[{section}]' файла {path}. Значение НЕ сохранено.")
        return False

    if updated:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            logger.info(f"Файл конфигурации {path} успешно обновлен.")
            return True
        except IOError as e:
            logger.error(f"Ошибка записи в файл {path} при сохранении: {e}")
            return False
    else:
        logger.debug(f"Обновление для ключа '{key}' в секции '[{section}]' не потребовалось.")
        return False


# --- Функции-обертки для удобного получения значений ---

def get_config_value(section: str, key: str, fallback: Any = "", config: Optional[Dict] = None) -> Any:
    """Получает значение из конфигурации."""
    if config is None: config = get_config()
    return config.get(section, {}).get(key, fallback)


def get_config_int(section: str, key: str, fallback: int = 0, config: Optional[Dict] = None) -> int:
    """Получает целочисленное значение."""
    value = get_config_value(section, key, fallback, config)
    try:
        return int(value)
    except (ValueError, TypeError):
        return fallback


def get_config_float(section: str, key: str, fallback: float = 0.0, config: Optional[Dict] = None) -> float:
    """Получает дробное значение."""
    value = get_config_value(section, key, fallback, config)
    try:
        return float(value)
    except (ValueError, TypeError):
        return fallback


def get_config_boolean(section: str, key: str, fallback: bool = False, config: Optional[Dict] = None) -> bool:
    """Получает булево значение."""
    value = get_config_value(section, key, fallback, config)
    if isinstance(value, bool):
        return value
    if str(value).lower() in ['true', '1', 't', 'y', 'yes']:
        return True
    if str(value).lower() in ['false', '0', 'f', 'n', 'no']:
        return False
    return fallback


def get_config_list(
        section: str,
        key: str,
        fallback: Optional[List[Any]] = None,
        config: Optional[Dict] = None) -> List[Any]:
    """Получает значение как список."""
    value = get_config_value(section, key, fallback, config)
    if isinstance(value, list):
        return value
    if fallback is None:
        return []
    return fallback


def get_config_section(section_name: str, fallback: Optional[Dict] = None, config: Optional[Dict] = None) -> Dict[
    str,
    Any]:
    """Получает всю секцию как словарь."""
    if config is None: config = get_config()
    return config.get(section_name, fallback if fallback is not None else {})
