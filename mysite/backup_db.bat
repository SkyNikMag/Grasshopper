@echo off
chcp 65001 >nul
echo Запуск резервного копирования [Ожидайте]
cd /d "%~dp0"
if not exist "..\.venv" (
    echo Создание виртуального окружения [Ожидайте]
    py -m venv "..\.venv"
)
echo Активация окружения [Ожидайте]
call "..\.venv\Scripts\activate"
echo Установка зависимостей [Ожидайте]
pip install -r "..\requirements.txt"
echo Создание резервной копии [Ожидайте]
"..\.venv\Scripts\python.exe" manage.py dbbackup
if %ERRORLEVEL% neq 0 (
    echo %date% %time%: Ошибка резервного копирования >> backup.log
) else (
    echo %date% %time%: Резервная копия создана [Успешно] >> backup.log
)
pause