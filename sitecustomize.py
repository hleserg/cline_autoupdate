"""
sitecustomize.py
Python автоматически импортирует этот модуль при КАЖДОМ старте интерпретатора,
если он находится в PYTHONPATH.  Модуль запускает Cline AutoUpdater в фоне,
чтобы пользователь вообще ничего не запускал вручную.
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
import threading
from pathlib import Path
from types import ModuleType
from typing import Any

# -----------------------------------------------------------------------------
# Константы и настройка логирования
# -----------------------------------------------------------------------------
_LOG_FILE = Path.cwd() / "logs" / "sitecustomize.log"
_LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(_LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Флаги окружения
# -----------------------------------------------------------------------------
_DISABLE_ENV = "CLINE_NO_AUTOUPDATE"      # если выставлено → автообновление отключено
_SENTINEL_ENV = "CLINE_AUTOUPDATE_RUNNING"  # предотвращает двойной запуск


def _run_autoupdater() -> None:
    """
    Импортирует main.ClineAutoUpdater и запускает его в фоне.
    Все исключения ловятся и логируются, чтобы не прерывать основной процесс.
    """
    try:
        logger.info("🛠️  Инициализация Cline AutoUpdater (background)")
        # Импорт main модуля
        main_mod: ModuleType = importlib.import_module("main")
        if not hasattr(main_mod, "ClineAutoUpdater"):
            logger.error("main.py не содержит ClineAutoUpdater. Автообновление пропущено.")
            return

        updater_cls: Any = getattr(main_mod, "ClineAutoUpdater")
        updater = updater_cls()
        updater.run()
        logger.info("✅ AutoUpdater завершил работу")
    except Exception as exc:  # noqa: BLE001
        logger.exception("❌ Ошибка AutoUpdater: %s", exc)


def _start_background_thread() -> None:
    """Запускает AutoUpdater в отдельном демоническом потоке."""
    thread = threading.Thread(target=_run_autoupdater, name="cline-autoupdater", daemon=True)
    thread.start()
    logger.info("🚀 AutoUpdater запущен в фоне (%s)", thread.name)


def _bootstrap() -> None:
    """Главная точка входа sitecustomize."""
    # Уже запущен? (чтобы не запускать дважды при вложенных интерпретаторах)
    if os.environ.get(_SENTINEL_ENV):
        return
    os.environ[_SENTINEL_ENV] = "1"

    # Пользователь явно отключил автообновление
    if os.environ.get(_DISABLE_ENV):
        logger.info("AutoUpdater отключён переменной окружения %s", _DISABLE_ENV)
        return

    # Не запускать в интерактивной REPL/IDLE, чтобы не мешать
    if sys.flags.interactive:
        logger.info("Интерактивный режим Python – AutoUpdater пропущен")
        return

    # Старт
    _start_background_thread()


# -----------------------------------------------------------------------------
# Точка входа при импорте
# -----------------------------------------------------------------------------
_bootstrap()
