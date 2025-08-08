# Telegram Bot для продажи файлов после оплаты

Бот для автоматической отправки файлов после успешной оплаты через YooKassa.

## Возможности

- ✅ Интеграция с YooKassa для приема платежей
- ✅ Автоматическая генерация уникальных отчетов
- ✅ Отправка файлов после подтверждения оплаты
- ✅ Кэширование отправленных файлов
- ✅ Проверка статуса платежей
- ✅ Асинхронная работа с базой данных

## Установка и запуск

### Windows

#### Требования
- Python 3.8+ ([скачать](https://www.python.org/downloads/))
- Git ([скачать](https://git-scm.com/download/win))

#### Установка

1. **Клонируйте репозиторий:**
```cmd
git clone https://github.com/EgorRU/vyatsu-data-analysis-bot.git
cd vyatsu-data-analysis-bot
```

2. **Создайте виртуальное окружение:**
```cmd
python -m venv venv
venv\Scripts\activate
```

3. **Установите зависимости:**
```cmd
pip install -r requirements.txt
```

4. **Создайте файл конфигурации:**
```cmd
copy env_example.txt .env
```

5. **Отредактируйте файл `.env` с вашими настройками:**
```env
# Настройки Telegram бота
BOT_TOKEN=1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsFas
BOT_URL=https://t.me/your_bot_username

# Настройки YooKassa
YOOKASSA_SHOP_ID=123456
YOOKASSA_SECRET_KEY=test_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef

# Цена в рублях
PRICE_RUB=500.0

# Ссылка на поддержку
SUPPORT_LINK=https://t.me/support
```

6. **Запустите бота:**
```cmd
python main.py
```

### Альтернативные способы запуска:

**Через Makefile:**
```cmd
make run
```

**Через Docker:**
```cmd
docker-compose up -d
```

### Linux/macOS

#### Требования
- Python 3.8+
- Git

#### Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/EgorRU/vyatsu-data-analysis-bot.git
cd vyatsu-data-analysis-bot
```

2. **Создайте виртуальное окружение:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Создайте файл конфигурации:**
```bash
cp env_example.txt .env
```

5. **Отредактируйте файл `.env` с вашими настройками:**
```env
# Настройки Telegram бота
BOT_TOKEN=1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsFas
BOT_URL=https://t.me/your_bot_username

# Настройки YooKassa
YOOKASSA_SHOP_ID=123456
YOOKASSA_SECRET_KEY=test_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef

# Цена в рублях
PRICE_RUB=500.0

# Ссылка на поддержку
SUPPORT_LINK=https://t.me/support
```

6. **Запустите бота:**
```bash
python main.py
```

### Альтернативные способы запуска:

**Через Makefile:**
```bash
make run
```

**Через Docker:**
```bash
docker-compose up -d
```

## Настройка

### 1. Telegram Bot

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен бота
3. Укажите токен в переменной `BOT_TOKEN`

### 2. YooKassa

1. Зарегистрируйтесь в [YooKassa](https://yookassa.ru/)
2. Получите Shop ID и Secret Key
3. Укажите их в переменных `YOOKASSA_SHOP_ID` и `YOOKASSA_SECRET_KEY`

### 3. Цена и поддержка

- Установите цену в переменной `PRICE_RUB`
- Укажите ссылку на поддержку в `SUPPORT_LINK`

## Структура проекта

```
vyatsu-data-analysis-bot/
├── main.py              # Точка входа приложения
├── settings.py          # Настройки и конфигурация
├── models.py            # Модели базы данных
├── payments.py          # Логика работы с платежами
├── user.py              # Обработчики команд пользователя
├── backend.py           # Генерация уникальных отчетов
├── requirements.txt     # Зависимости Python
├── pyproject.toml      # Конфигурация проекта
├── README.md           # Документация
├── LICENSE             # Лицензия MIT
├── Makefile            # Команды разработки
├── Dockerfile          # Контейнеризация
├── docker-compose.yml  # Docker Compose
├── .env                # Конфигурация (создать из env_example.txt)
├── .editorconfig       # Настройки редактора
├── .gitattributes      # Настройки Git
├── .gitignore          # Игнорируемые файлы
├── .dockerignore       # Игнорируемые Docker файлы
└── data/               # Данные для анализа
    ├── ds_salaries.csv # CSV файл с данными
    └── project.docx    # Шаблон отчета
```

## Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для получения дополнительной информации.
