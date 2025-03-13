# Используем официальный Python 3.12 образ
FROM python:3.12

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# Указываем Poetry использовать системное окружение
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости через Poetry
RUN poetry install --no-root

# Создаем директорию storage для data.json
RUN mkdir -p storage

# Открываем порт 3000
EXPOSE 3000

# Запускаем сервер
CMD ["poetry", "run", "python", "main.py"]
