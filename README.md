# Telegram Bot для продажи файлов после оплаты

Бот для автоматической отправки файлов после успешной оплаты через Telegram Payments (инвойсы в чате).

## Возможности

- ✅ Инвойсы Telegram Payments (оплата прямо в боте)
- ✅ Автоматическая генерация уникальных отчетов
- ✅ Отправка файлов после подтверждения оплаты
- ✅ Кэширование отправленных файлов
- ✅ Повторная отправка оплаченных заказов по кнопке
- ✅ Админ-команда /proj: выдача без оплаты или по ID платежа
- ✅ Асинхронная работа с базой данных

## Установка и запуск

### Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/EgorRU/vyatsu-data-analysis-bot.git
cd vyatsu-data-analysis-bot
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
```

3. **Активируйте виртуальное окружение:**
- Windows (PowerShell или CMD):
```cmd
venv\Scripts\activate
```
- Linux/macOS (bash/zsh):
```bash
source venv/bin/activate
```

4. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

5. **Создайте файл конфигурации `.env`:**
- Windows:
```cmd
copy env_example.txt .env
```
- Linux/macOS:
```bash
cp env_example.txt .env
```

6. **Отредактируйте файл `.env` с вашими настройками:**
```env
# Настройки Telegram бота
BOT_TOKEN=1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsFas
PROVIDER_TOKEN=TEST:000000000000000000000000000000000000

# Цена в рублях
PRICE_RUB=500

# Ссылка на поддержку
SUPPORT_LINK=https://t.me/support

# Администраторы (через запятую)
ADMIN_IDS=123456789,987654321

# URL базы данных
DATABASE_URL=sqlite+aiosqlite:///database.db
```

### Запуск
```bash
python src/main.py
```

### Альтернативные способы запуска

Через Makefile:
```bash
make run
```

Через Docker Compose:
```bash
docker-compose up -d
```

## Настройка

### 1. Telegram Bot

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен бота
3. Укажите токен в переменной `BOT_TOKEN`

### 2. Telegram Payments

1. Получите provider token у [@BotFather](https://t.me/BotFather)
2. Укажите его в `PROVIDER_TOKEN`

### 3. Цена и поддержка

- Установите цену в переменной `PRICE_RUB`
- Укажите ссылку на поддержку в `SUPPORT_LINK`

## Команды

- Пользовательские
  - **/start**: старт, показать кнопки оплаты и проверки заказов
  - Кнопки: «Оплатить N ₽», «Проверить все заказы»

- Админские (ID администратора указывается в `ADMIN_IDS`)
  - **/proj**: сгенерировать новый проект и отправить администратору
  - **/proj <payment_id>**: отправить файл по `telegram_payment_charge_id`;
    если файл ещё не был зафиксирован, он будет сгенерирован и привязан к платежу

## Структура проекта

```
vyatsu-data-analysis-bot/
├── data/                # Данные и шаблон отчета
│   ├── ds_salaries.csv  # Датасет (входные данные)
│   └── project.docx     # DOCX-шаблон с плейсхолдерами
├── src/                 # Приложение бота
│   ├── backend.py       # Генерация отчета: чтение data, графики (matplotlib/seaborn), ML (sklearn)
│   ├── main.py          # Точка входа (python src/main.py)
│   ├── settings.py      # Загрузка переменных из .env (pydantic-settings)
│   ├── models.py        # SQLAlchemy: движок/сессии и модель PaymentRecord, init_db()
│   ├── payments.py      # Цена, кэширование file_id, выборка успешных платежей
│   ├── user.py          # Хендлеры пользователя: /start, инвойс, выдача проектов
│   └── admin.py         # Хендлеры админа: выдача без оплаты, выдача по ID оплаты
├── requirements.txt     # Зависимости Python
├── pyproject.toml       # Конфигурация проекта
├── README.md            # Документация
├── LICENSE              # Лицензия MIT
├── Makefile             # Команда запуска (make run)
├── Dockerfile           # Минимальный Docker-образ
├── docker-compose.yml   # Минимальный Compose для запуска
├── .env                 # Конфигурация (создать из env_example.txt)
├── .editorconfig        # Настройки редактора
├── .gitattributes       # Настройки Git
├── .gitignore           # Игнорируемые файлы
├── .dockerignore        # Игнорируемые Docker файлы
└── env_example.txt      # Пример .env
```

## Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для получения дополнительной информации.
