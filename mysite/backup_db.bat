@echo off
chcp 65001 >nul
REM Устанавливаем кодировку UTF-8 и скрываем вывод команды

echo Запуск процесса резервного копирования [Ожидайте]

REM Проверка, существует ли виртуальное окружение
if not exist "C:\Users\niksw\OneDrive\Рабочий стол\Тех\ТРПО\5 семестр\Курсовая\Grasshopper\.venv" (
    echo Создание виртуального окружения... [Ожидайте]
    py -m venv "C:\Users\niksw\OneDrive\Рабочий стол\Тех\ТРПО\5 семестр\Курсовая\Grasshopper\.venv"
    if %ERRORLEVEL% neq 0 (
        echo %date% %time%: Не удалось создать виртуальное окружение >> backup.log
        exit /b %ERRORLEVEL%
    )
    echo Виртуальное окружение создано [Успешно]
)

REM Активируем виртуальное окружение
echo Активация виртуального окружения [Ожидайте]
call "C:\Users\niksw\OneDrive\Рабочий стол\Тех\ТРПО\5 семестр\Курсовая\Grasshopper\.venv\Scripts\activate"
if %ERRORLEVEL% neq 0 (
    echo %date% %time%: Не удалось активировать виртуальное окружение >> backup.log
    exit /b %ERRORLEVEL%
)

REM Установка зависимостей (предполагается, что есть requirements.txt)
echo Установка зависимостей [Ожидайте]
if not exist "C:\Users\niksw\OneDrive\Рабочий стол\Тех\ТРПО\5 семестр\Курсовая\Grasshopper\requirements.txt" (
    echo Создание файла requirements.txt с django-dbbackup [Ожидайте]
    echo django-dbbackup > "C:\Users\niksw\OneDrive\Рабочий стол\Тех\ТРПО\5 семестр\Курсовая\Grasshopper\requirements.txt"
)
pip install -r "C:\Users\niksw\OneDrive\Рабочий стол\Тех\ТРПО\5 семестр\Курсовая\Grasshopper\requirements.txt"
if %ERRORLEVEL% neq 0 (
    echo %date% %time%: Не удалось установить зависимости >> backup.log
    exit /b %ERRORLEVEL%
)
echo Зависимости установлены [Успешно]

REM Переход в директорию mysite
echo Переход в директорию проекта [Ожидайте]
cd /d "C:\Users\niksw\OneDrive\Рабочий стол\Тех\ТРПО\5 семестр\Курсовая\Grasshopper\mysite"
if %ERRORLEVEL% neq 0 (
    echo %date% %time%: Не удалось перейти в директорию mysite >> backup.log
    exit /b %ERRORLEVEL%
)

REM Выполнение резервного копирования
echo Создание резервной копии базы данных [Ожидайте]
"C:\Users\niksw\OneDrive\Рабочий стол\Тех\ТРПО\5 семестр\Курсовая\Grasshopper\.venv\Scripts\python.exe" manage.py dbbackup
if %ERRORLEVEL% neq 0 (
    echo %date% %time%: Ошибка при создании резервной копии, код %ERRORLEVEL% >> backup.log
    exit /b %ERRORLEVEL%
)

REM Успешное завершение
echo %date% %time%: Резервная копия успешно создана в папке BackUp [Успешно] >> backup.log
echo Резервное копирование завершено [Успешно]
pause