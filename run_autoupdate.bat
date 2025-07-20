@echo off
echo Starting Cline AutoUpdater...
cd /d "%~dp0"

REM Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не найден! Установите Python 3.7+ и добавьте в PATH
    pause
    exit /b 1
)

REM Проверка и установка зависимостей
if not exist "requirements.txt" (
    echo Файл requirements.txt не найден!
    pause
    exit /b 1
)

echo Установка зависимостей...
pip install -r requirements.txt --quiet

REM Создание необходимых директорий
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "templates" mkdir templates

echo Запуск системы автообновления...
python main.py

if %errorlevel% neq 0 (
    echo Ошибка при выполнении! Проверьте логи в logs/cline_autoupdate.log
    pause
    exit /b 1
)

echo Автообновление завершено успешно!
pause
