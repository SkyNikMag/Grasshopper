@echo off
chcp 65001 >nul
REM Проверка, существует ли виртуальное окружение
if not exist env (
    echo Создаю виртуальное окружение... [Ожидайте]
    py -m venv env
)

REM Активируем виртуальное окружение
echo Активация виртуального окружение [Ожидайте]
call env\Scripts\activate

REM Установка зависимостей
echo Установка зависимостей [Ожидайте]
pip install -r requirements.txt

cd mysite

REM Применяем миграции
echo Примение миграции БД [Ожидайте]
py manage.py migrate

REM Запускаем сервер разработки Django
echo Запуск веб-приложение перейдите по ссылке [УСПЕШНО]
py manage.py runserver

REM Удерживаем окно открытым
pause
