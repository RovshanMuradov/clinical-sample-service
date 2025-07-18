# TODO: Этап 1 - Базовая настройка и инфраструктура

## 1. Настройка окружения и конфигурации

### 1.1 Создание файла .env
- [x] Создать файл .env со следующими переменными:
  ```
  DATABASE_URL=postgresql+asyncpg://user:password@localhost/clinical_samples_db
  SECRET_KEY=your-secret-key-here
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  DEBUG=True
  LOG_LEVEL=INFO
  ```

### 1.2 Реализация core/config.py
- [x] Создать класс Settings с использованием pydantic-settings
- [x] Добавить валидацию переменных окружения
- [x] Настроить загрузку из .env файла
- [x] Включить следующие настройки:
  - Подключение к БД
  - JWT параметры
  - Настройки приложения (название, версия)
  - Настройки CORS

### 1.3 Настройка логирования в core/logging.py
- [x] Создать централизованную конфигурацию логирования
- [x] Настроить форматирование логов
- [x] Добавить ротацию файлов логов
- [x] Настроить уровни логирования из конфигурации

## 2. Настройка базы данных

### 2.1 Создание базового подключения к БД
- [x] Создать файл app/db/base.py ✓ (папка app/db/ создана)
- [x] Настроить SQLAlchemy engine
- [x] Создать SessionLocal и Base
- [x] Создать функцию get_db для dependency injection

### 2.2 Инициализация моделей
- [x] Создать app/db/__init__.py
- [x] Импортировать все модели для Alembic
- [x] Создать базовую структуру для моделей

### 2.3 Настройка Alembic
- [x] Инициализировать Alembic: `alembic init alembic`
- [x] Настроить alembic.ini с корректным DATABASE_URL
- [x] Обновить alembic/env.py для работы с нашими моделями
- [x] Создать первую миграцию ✓ (завершено в Этапе 2)

## 3. Docker окружение

### 3.1 Создание Dockerfile
- [x] Создать multi-stage Dockerfile
- [x] Настроить базовый образ Python 3.11 (используется в проекте)
- [x] Установить зависимости
- [x] Настроить рабочую директорию
- [x] Добавить healthcheck
- [x] Настроить запуск через uvicorn

### 3.2 Настройка docker-compose.yml
- [x] Создать сервис для приложения
- [x] Создать сервис для PostgreSQL
- [x] Настроить volumes для БД
- [x] Настроить сеть между сервисами
- [x] Добавить переменные окружения
- [x] Настроить порты

### 3.3 Создание вспомогательных скриптов
- [x] Создать скрипт для инициализации БД
- [x] Создать .dockerignore файл

## 4. Базовая структура приложения

### 4.1 Настройка main.py
- [x] Создать FastAPI приложение
- [x] Настроить CORS
- [x] Добавить middleware для логирования
- [x] Настроить обработку исключений
- [x] Добавить health check endpoint

### 4.2 Создание базовых зависимостей
- [x] Создать app/api/deps.py
- [x] Добавить зависимость для получения БД сессии
- [x] Подготовить структуру для будущих auth зависимостей

## Критерии завершения этапа
- [x] Приложение запускается локально через uvicorn
- [x] Приложение запускается через docker-compose
- [x] База данных успешно подключается
- [x] Логирование работает корректно
- [x] Health check endpoint возвращает 200 OK
- [x] Конфигурация загружается из .env файла
- [x] Alembic готов к созданию миграций

---

# TODO: Этап 2 - Модели данных и база данных

## 1. Создание моделей SQLAlchemy

### 1.1 Модель User для аутентификации
- [x] Создать User модель в app/models/user.py
- [x] Добавить поля: id, username, email, hashed_password, is_active, created_at, updated_at
- [x] Настроить индексы для email и username (уникальные)
- [x] Добавить relationships при необходимости
- [x] Импортировать модель в app/models/__init__.py

### 1.2 Модель Sample для клинических образцов  
- [x] Создать Sample модель в app/models/sample.py
- [x] Добавить поля: id, sample_id (UUID), sample_type, subject_id, collection_date, status, storage_location, created_at, updated_at
- [x] Настроить enum для sample_type (blood, saliva, tissue)
- [x] Настроить enum для status (collected, processing, archived)
- [x] Добавить валидацию и ограничения
- [x] Импортировать модель в app/models/__init__.py

## 2. Создание Pydantic схем

### 2.1 Схемы для аутентификации
- [x] Создать UserBase, UserCreate, UserUpdate, UserResponse в app/schemas/auth.py
- [x] Добавить UserLogin схему для входа
- [x] Добавить Token, TokenData схемы для JWT
- [x] Настроить валидацию email и пароля
- [x] Импортировать схемы в app/schemas/__init__.py

### 2.2 Схемы для Sample
- [x] Создать SampleBase, SampleCreate, SampleUpdate, SampleResponse в app/schemas/sample.py
- [x] Добавить схемы для фильтрации: SampleFilter
- [x] Настроить валидацию для типов и статусов
- [x] Добавить валидацию дат
- [x] Импортировать схемы в app/schemas/__init__.py

## 3. Создание и применение миграций базы данных

### 3.1 Создание первой миграции
- [x] Запустить: `make migrate-create MESSAGE="Create users and samples tables"`
- [x] Проверить сгенерированную миграцию в alembic/versions/
- [x] При необходимости отредактировать миграцию
- [x] Применить миграцию: `make migrate-up`

### 3.2 Проверка базы данных
- [x] Подключиться к БД и проверить созданные таблицы
- [x] Проверить индексы и ограничения
- [x] Протестировать rollback: `make migrate-down`

## Критерии завершения этапа 2
- [x] Все модели SQLAlchemy созданы и работают
- [x] Все Pydantic схемы созданы с валидацией
- [x] База данных создана с правильными таблицами
- [x] Миграции работают корректно (up/down)
- [x] Можно создавать/читать записи через SQLAlchemy

---

# TODO: Этап 3 - Аутентификация и безопасность

## 1. Реализация JWT аутентификации

### 1.1 Создание функций безопасности
- [x] Реализовать create_access_token() в app/core/security.py
- [x] Реализовать verify_token() для проверки JWT
- [x] Реализовать get_password_hash() для хеширования паролей
- [x] Реализовать verify_password() для проверки паролей
- [x] Добавить функцию decode_token() для получения данных из токена

### 1.2 Настройка JWT параметров
- [x] Использовать настройки из config.py (SECRET_KEY, ALGORITHM, EXPIRE_MINUTES)
- [x] Добавить обработку истекших токенов
- [x] Добавить обработку некорректных токенов

## 2. Создание endpoints для аутентификации

### 2.1 Регистрация пользователей
- [x] Реализовать POST /api/v1/auth/register в app/api/v1/endpoints/auth.py
- [x] Добавить валидацию уникальности email/username
- [x] Хешировать пароль при регистрации
- [x] Возвращать созданного пользователя (без пароля)

### 2.2 Вход в систему
- [x] Реализовать POST /api/v1/auth/login 
- [x] Проверять credentials пользователя
- [x] Создавать и возвращать JWT токен
- [x] Обрабатывать неверные credentials

### 2.3 Обновление токена
- [x] Реализовать POST /api/v1/auth/refresh
- [x] Проверять действующий токен
- [x] Создавать новый токен

## 3. Создание зависимостей для защиты маршрутов

### 3.1 Обновление app/api/deps.py
- [x] Обновить get_current_user() для реальной JWT проверки
- [x] Добавить получение пользователя из БД по токену
- [x] Обработать ошибки авторизации (401, 403)
- [x] Убрать placeholder логику

### 3.2 Создание репозитория пользователей
- [x] Создать UserRepository в app/repositories/user_repository.py
- [x] Реализовать get_user_by_email()
- [x] Реализовать get_user_by_id()
- [x] Реализовать create_user()
- [x] Реализовать update_user()

### 3.3 Создание сервиса аутентификации
- [x] Создать AuthService в app/services/auth_service.py
- [x] Реализовать register_user()
- [x] Реализовать authenticate_user()
- [x] Реализовать get_current_user_by_token()

## 4. Интеграция аутентификации с Sample endpoints

### 4.1 Обновление Sample endpoints
- [x] Добавить реальную аутентификацию к Sample endpoints в app/api/v1/endpoints/samples.py
- [x] Убрать placeholder логику  
- [x] Связать образцы с пользователями

## Критерии завершения этапа 3
- [x] JWT аутентификация полностью работает
- [x] Пользователи могут регистрироваться и входить
- [x] Токены создаются и проверяются корректно
- [x] Защищенные endpoints требуют валидного токена
- [x] Все auth endpoints возвращают правильные ошибки
- [x] Пароли хешируются безопасно

---

# TODO: Этап 4 - Основная бизнес-логика

## 1. Реализация репозиториев

### 1.1 SampleRepository для работы с базой данных
- [x] Создать SampleRepository в app/repositories/sample_repository.py
- [x] Реализовать create_sample()
- [x] Реализовать get_sample_by_id()
- [x] Реализовать get_samples_with_filters()
- [x] Реализовать update_sample()
- [x] Реализовать delete_sample()
- [x] Добавить методы для подсчета записей (count)

## 2. Реализация сервисного слоя

### 2.1 SampleService для бизнес-логики
- [x] Создать SampleService в app/services/sample_service.py
- [x] Реализовать create_sample() с валидацией
- [x] Реализовать get_sample_by_id() с проверкой прав
- [x] Реализовать get_samples() с фильтрацией и пагинацией
- [x] Реализовать update_sample() с валидацией
- [x] Реализовать delete_sample() с проверкой прав
- [x] Добавить бизнес-правила для Sample

## 3. Создание API endpoints для образцов

### 3.1 Реализация реальных CRUD endpoints
- [x] Заменить placeholder логику в app/api/v1/endpoints/samples.py
- [x] Реализовать POST /samples - создание нового образца
- [x] Реализовать GET /samples - получение всех образцов
- [x] Реализовать GET /samples/{id} - получение конкретного образца
- [x] Реализовать PUT /samples/{id} - обновление образца
- [x] Реализовать DELETE /samples/{id} - удаление образца

### 3.2 Интеграция с сервисами и репозиториями
- [x] Подключить SampleService к endpoints
- [x] Добавить dependency injection для сервисов
- [x] Настроить правильные HTTP статусы
- [x] Добавить proper error handling

## 4. Реализация фильтрации образцов (обязательно из ТЗ)

### 4.1 Расширенная фильтрация для GET /samples
- [x] Добавить query параметры для фильтрации в схемы
- [x] Реализовать фильтрацию по статусу (collected, processing, archived)
- [x] Реализовать фильтрацию по типу (blood, saliva, tissue)
- [x] Реализовать фильтрацию по subject_id
- [x] Реализовать фильтрацию по дате сбора (от/до)
- [x] Реализовать комбинированную фильтрацию
- [x] Добавить валидацию параметров фильтрации
- [x] Добавить пагинацию (skip, limit)

## 5. Связывание образцов с пользователями

### 5.1 Добавление поля user_id в Sample модель
- [x] Обновить модель Sample с полем user_id
- [x] Добавить Foreign Key к таблице users
- [x] Создать миграцию для добавления поля user_id
- [x] Применить миграцию
- [x] Обновить репозиторий для фильтрации по user_id
- [x] Обновить сервис для проверки прав доступа
- [x] Добавить data isolation (пользователи видят только свои образцы)

## 6. Дополнительные улучшения

### 6.1 Дополнительные endpoints
- [x] Реализовать GET /samples/subject/{subject_id} - получение образцов по subject ID
- [x] Реализовать GET /samples/stats/overview - статистика образцов

### 6.2 Завершение недоделанных задач из Этапа 3
- [x] Завершить реализацию POST /api/v1/auth/refresh
- [x] Добавить полную JWT token validation в refresh endpoint

## Критерии завершения этапа 4
- [x] Все CRUD операции полностью функциональны
- [x] Фильтрация работает по всем параметрам
- [x] Сервисный слой содержит бизнес-логику
- [x] Репозиторий абстрагирует работу с БД
- [x] API возвращает корректные HTTP статусы
- [x] Образцы связаны с пользователями (data isolation)
- [x] Авторизация работает на уровне данных

## 7. Исправление критических проблем безопасности

### 7.1 Обнаружение и исправление проблемы data isolation в статистике
- [x] **КРИТИЧЕСКОЕ**: Выявлена проблема - статистика показывала данные всех пользователей
- [x] Обновлен метод get_samples_by_status для поддержки user_id фильтрации
- [x] Добавлен метод get_samples_by_type с user_id фильтрацией
- [x] Исправлен метод get_sample_statistics для корректного data isolation
- [x] Реализована полная статистика by_type (была пустой)

### 7.2 Тестирование исправлений
- [x] Протестирована статистика с несколькими пользователями
- [x] Проверена консистентность данных (totals совпадают)
- [x] Протестированы edge cases (пустые данные, новые пользователи)
- [x] Подтверждена полная изоляция данных между пользователями

🔒 **БЕЗОПАСНОСТЬ ВОССТАНОВЛЕНА** - Data isolation теперь работает корректно во всех endpoints

---

# TODO: Этап 5 - Обработка ошибок и валидация

## 1. Создание кастомных исключений

### 1.1 Определение исключений приложения
- [x] Создать app/core/exceptions.py
- [x] Добавить NotFoundError для ресурсов не найденных
- [x] Добавить ValidationError для ошибок валидации
- [x] Добавить AuthenticationError для ошибок аутентификации
- [x] Добавить AuthorizationError для ошибок авторизации
- [x] Добавить DatabaseError для ошибок БД

## 2. Глобальная обработка ошибок

### 2.1 Обработчики исключений
- [x] Обновить глобальные exception handlers в app/main.py
- [x] Добавить handler для ValidationError -> 400
- [x] Добавить handler для NotFoundError -> 404
- [x] Добавить handler для AuthenticationError -> 401
- [x] Добавить handler для AuthorizationError -> 403
- [x] Добавить handler для DatabaseError -> 500

### 2.2 Стандартизация ответов об ошибках
- [x] Создать ErrorResponse схему
- [x] Стандартизировать формат JSON ошибок
- [x] Добавить error codes и messages
- [ ] Локализация ошибок (опционально)

## 3. Валидация входных данных

### 3.1 Расширенная валидация Pydantic
- [x] Добавить кастомные validators в схемы
- [x] Валидация business rules в схемах
- [x] Валидация cross-field dependencies
- [x] Добавить meaningful error messages

## 4. Логирование ошибок и операций

### 4.1 Структурированное логирование
- [x] Обновить логирование в app/core/logging.py
- [x] Добавить correlation IDs для трейсинга
- [x] Логировать все API запросы/ответы
- [x] Логировать ошибки с контекстом
- [x] Настроить разные уровни логирования

## 5. Security Hardening (критично для медицинских данных)

### 5.1 Дополнительная защита API
- [x] Добавить rate limiting для API endpoints (защита от DDoS)
- [x] Реализовать request timeout для всех endpoints
- [x] Добавить CORS настройки для production
- [x] Валидация Content-Type headers

### 5.2 Input Security & Validation
- [x] Валидация всех входных данных против injection attacks
- [x] Проверка на SQL injection (через ORM protection)
- [x] Input sanitization для всех user inputs
- [ ] Валидация file uploads (не применимо - нет загрузки файлов)
- [x] Проверка размеров payload

### 5.3 Secrets & Data Protection
- [x] Audit secrets management (проверить что токены/пароли не логируются)
- [x] Убедиться что sensitive data не возвращается в API responses
- [x] Проверить что DEBUG=False в production
- [x] Валидация прав доступа к данным на всех уровнях
- [x] Добавить security headers (X-Content-Type-Options, etc.)

## Критерии завершения этапа 5
- [x] Все ошибки обрабатываются gracefully
- [x] Клиенты получают понятные сообщения об ошибках
- [x] Все операции логируются с контекстом
- [x] Валидация работает на всех уровнях

## Дополнительные улучшения, выполненные сверх плана:

### 6.1 Middleware для логирования и безопасности
- [x] Создан LoggingMiddleware для корреляции запросов
- [x] Создан SecurityLoggingMiddleware для мониторинга атак
- [x] Создан PerformanceLoggingMiddleware для отслеживания производительности
- [x] Интегрированы middleware в основное приложение

### 6.2 Расширенная валидация схем
- [x] Валидация Subject ID (формат P001, S123)
- [x] Валидация дат (не в будущем, не старше 10 лет)
- [x] Валидация storage location (формат freezer-X-rowY)
- [x] Бизнес-правила (tissue samples должны быть в freezer)
- [x] Валидация паролей (спецсимволы, слабые пароли, схожесть с username)
- [x] Валидация email доменов для клинических данных
- [x] Валидация username (формат, зарезервированные слова)

### 6.3 Улучшения безопасности
- [x] Фильтрация чувствительных данных в логах
- [x] Обнаружение подозрительных запросов (SQL injection patterns)
- [x] Проверка размеров headers (защита от DoS)
- [x] Обнаружение подозрительных User-Agent
- [x] Логирование всех security событий

### 6.5 ✅ ВЫПОЛНЕНО (успешно реализовано):
- [x] Rate limiting для API endpoints
- [x] Request timeout для всех endpoints
- [x] Продвинутые CORS настройки для production
- [x] Валидация Content-Type headers
- [x] Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- [x] Полная проверка размеров payload (не только headers)

### 6.4 Тестирование и качество кода
- [x] Исправлены все ошибки MyPy type checking
- [x] Исправлены все ошибки flake8 linting
- [x] Применено форматирование black + isort
- [x] Протестировано в production через Docker
- [x] Проверена работа всех валидаций в реальном окружении

---

## Этап 6 — Тестирование (Фокусированный подход)

**🎯 Цель:** покрыть 80 % критических рисков минимальным набором тестов (~15–20 вместо 50+).

---

### 1. Настройка тестового окружения

- [x] Обновить `pyproject.toml` с настройками pytest  
- [x] Создать `conftest.py` с фикстурами  
- [x] Настроить тестовую БД (SQLite in-memory)  
- [x] Создать `test_main.py` для базовых smoke-тестов  
- [x] Настроить отчёты coverage  

---

### 2. Приоритет 1 — Критическая безопасность и изоляция данных

#### Data Isolation

- [x] `test_user_can_only_see_own_samples()`  
- [x] `test_user_cannot_access_other_user_samples()`  
- [x] `test_statistics_only_show_user_data()`  
- [x] `test_filtering_respects_user_boundaries()`  
- [x] `test_subject_search_isolated_by_user()`  

#### Аутентификация

- [x] `test_password_hashing_and_verification()`  
- [x] `test_jwt_token_creation_and_validation()`  
- [x] `test_expired_token_rejection()`  
- [x] `test_invalid_token_rejection()`  

#### Авторизация

- [x] `test_cannot_update_other_user_sample()`  
- [x] `test_cannot_delete_other_user_sample()`  
- [x] `test_cannot_view_other_user_sample()`  
- [x] `test_sample_creation_assigns_correct_user()`  

---

### 3. Приоритет 2 — Базовая функциональность

#### Логика регистрации и входа

- [x] `test_duplicate_email_registration_blocked()`  
- [x] `test_duplicate_username_registration_blocked()`  
- [x] `test_login_with_wrong_password_fails()`  
- [x] `test_inactive_user_cannot_login()`  

#### CRUD для образцов

- [x] `test_create_sample_with_valid_data()`  
- [x] `test_update_sample_fields()`  
- [x] `test_update_preserves_user_isolation()`  
- [x] `test_delete_existing_sample()`  
- [x] `test_get_sample_by_id()`  
- [x] `test_sample_not_found_error()`  

---

### 4. Приоритет 3 — Edge-кейсы и дополнительные проверки

- [x] `test_pagination_parameters_handling()`  
- [x] `test_invalid_uuid_handling()`  

---

## Текущее состояние

- **Всего юнит-тестов:** 41 ✅  
- **Покрытие кода:** 23 % (нужно ≥ 70 %)  
- **Критические риски (Data Isolation, Auth, Authorization):** 95 % покрыто ✅  
- **API-эндоинты:** 0 % ❌  
- **Middleware:** 0 % ❌  
- **Integration-тесты:** отсутствуют ❌  

---

## План доработки

1. 🔴 **Приоритет 1 (к production):**  
   - [ ] Добавить integration-тесты для всех API-эндпоинтов  
   - [ ] Покрыть тестами `app/main.py` (FastAPI приложение)  
   - [ ] Протестировать все middleware (logging, security)  

2. 🟡 **Приоритет 2 (важно):**  
   - [ ] Тесты для `app/core/security.py` (JWT-функции)  
   - [ ] Тесты для exception handlers  
   - [ ] Проверка dependency injection (`app/api/deps.py`)  

3. 🟢 **Приоритет 3 (желательно):**  
   - [ ] Полное покрытие репозиторного слоя  
   - [ ] Performance-тесты  
   - [ ] E2E-тесты через TestClient  


---

# TODO: Этап 7 - Документация и финализация

## 1. Создание подробного README.md (ВЫСШИЙ ПРИОРИТЕТ - критично для оценки!)

### 1.1 Критические элементы README согласно требованиям ТЗ
- [ ] Инструкции по запуску приложения (локально)
- [ ] Инструкции по запуску с Docker
- [ ] Инструкции по тестированию
- [ ] Описание технологий и обоснование выбора
- [ ] Список реализованных функций
- [ ] Список пропущенных функций
- [ ] Что можно улучшить с большим временем
- [ ] Компромиссы и trade-offs в принятых решениях
- [ ] (Опционально) Высокоуровневая архитектурная диаграмма

## 2. Базовая Swagger документация (СРЕДНИЙ ПРИОРИТЕТ)

### 2.1 Улучшение автогенерируемой документации API
- [ ] Настроить детальные описания всех endpoints
- [ ] Добавить примеры запросов и ответов
- [ ] Документировать аутентификацию
- [ ] Описать все модели данных с примерами
- [ ] Добавить теги и группировку endpoints
- [ ] Документировать error responses

## 3. Добавление комментариев к коду (НИЗКИЙ ПРИОРИТЕТ)

### 3.1 Документация кода
- [ ] Добавить docstrings ко всем функциям и классам
- [ ] Документировать сложные алгоритмы
- [ ] Добавить type hints везде где отсутствуют
- [ ] Документировать бизнес-правила в комментариях
- [ ] Добавить примеры использования в docstrings

## 4. Оптимизация производительности (ОПЦИОНАЛЬНО - если останется время)

### 4.1 Database оптимизации
- [ ] Добавить индексы для часто используемых полей
- [ ] Оптимизировать N+1 queries
- [ ] Добавить database connection pooling
- [ ] Реализовать eager/lazy loading где нужно

### 4.2 API оптимизации
- [ ] Добавить response caching где применимо
- [ ] Оптимизировать размер response payload
- [ ] Добавить compression middleware
- [ ] Реализовать pagination для больших списков

## 5. Финальная проверка безопасности (ВЫСОКИЙ ПРИОРИТЕТ)

### 5.1 Pre-production Security аудит
- [ ] Проверить все endpoints на авторизацию
- [ ] Валидировать все user inputs
- [ ] Проверить password policies
- [ ] Аудит секретных ключей и токенов
- [ ] Проверить HTTPS настройки (для продакшена)
- [x] Rate limiting для API endpoints

### 5.2 Data protection
- [ ] Убедиться что пароли не логируются
- [ ] Проверить что sensitive data не возвращается в API
- [ ] Валидация прав доступа к данным
- [ ] SQL injection protection через ORM

## Критерии завершения этапа 7 (приоритизированные)

### Обязательно для сдачи:
- [ ] README.md содержит всю необходимую информацию из ТЗ
- [ ] Базовая Swagger документация работает
- [ ] Безопасность проверена и настроена

### Желательно (если есть время):
- [ ] API детально документирован в Swagger
- [ ] Код хорошо документирован
- [ ] Производительность оптимизирована

### Рекомендации по времени:
- **60% времени**: README.md (это ключ к хорошей оценке!)
- **30% времени**: Security аудит
- **10% времени**: Улучшения документации

---

# TODO: Этап 8 - Добавление CI/CD (GitHub Actions)

## 1. Continuous Integration (CI)
- [ ] Создать файл `.github/workflows/ci.yml`
- [ ] Настроить триггеры: `on: [push, pull_request]`
- [ ] Шаг: `actions/checkout@v4`
- [ ] Шаг: `actions/setup-python@v5` с `python-version: '3.11'` и кешем pip
- [ ] Установить dev-зависимости: `pip install -r requirements.dev.txt`
- [ ] Запустить линтеры и статический анализ:
  - [ ] `flake8 .`
  - [ ] `mypy app/`
- [ ] Запустить тесты с покрытием:
  - [ ] `pytest --cov=app --cov-report=xml`
- [ ] Опубликовать отчёт покрытия (например, через `codecov/codecov-action`)
- [ ] (Опционально) Собрать Docker-образ и запушить в GHCR

## 2. Continuous Deployment (CD)
- [ ] Создать файл `.github/workflows/cd.yml`
- [ ] Настроить триггер: `on.push.tags: ['v*']`
- [ ] Job: **deploy-staging**
  - [ ] Настроить environment: `staging`
  - [ ] SSH-доступ к серверу (через `appleboy/ssh-action`)
  - [ ] Pull нужного Docker-образа из GHCR
  - [ ] Запустить `docker-compose up -d --force-recreate`
- [ ] Job: **deploy-production**
  - [ ] Требует `approve` в environment: `production`
  - [ ] Аналогичный скрипт деплоя на прод
- [ ] Добавить и сохранить в GitHub Secrets:
  - `GHCR_TOKEN`, `STAGE_HOST`, `STAGE_USER`, `STAGE_KEY`
  - `PROD_HOST`, `PROD_USER`, `PROD_KEY`

## 3. Дополнительно
- [ ] Настроить Dependabot (`.github/dependabot.yml`) для обновления зависимостей
- [ ] Добавить CodeQL-анализ (`.github/workflows/codeql.yml`)
- [ ] Кэширование Docker-слоёв (`actions/cache` + `docker/setup-buildx-action`)

---

## Текстовый план

1. **CI: автоматизация проверки качества**  
   - При любом пуше и открытии PR GitHub Actions запустит линтеры и MyPy, затем выполнит все unit- и integration-тесты.  
   - Отчёт о покрытии собирается и посылается в Codecov, а шаг `--cov-fail-under=70` гарантирует, что пулл-реквест не примут, пока покрытие не вырастет до 70 %.

2. **CD: автоматический деплой по тегам**  
   - Когда вы пушите тег вида `v1.2.3`, срабатывает workflow `cd.yml`.  
   - Сначала разворачивается staging-окружение без вмешательства человека.  
   - После успешного деплоя в staging создаётся кнопка Approve в GitHub UI; по её нажатию запускается деплой в production.

3. **Секреты и безопасность**  
   - Все SSH-ключи и токены хранятся в GitHub Secrets, а Actions получают доступ через безопасный OIDC.  
   - Dependabot периодически обновляет зависимости, а CodeQL проверяет уязвимости в коде.

4. **Результаты и преимущества**  
   - **Fail fast**: ошибки линтинга, тестов или падение coverage моментально ругаются в PR.  
   - **Быстрый релиз**: один git-tag – и новая версия автоматически попадёт на staging, а после одобрения – в продакшн.  
   - **Прозрачность**: в истории изменений останутся все логи сборки, тестов и деплоя.  

Этот план позволит вам настроить надёжный CI/CD-конвейер, сократить ручные операции и повысить качество релизов.
