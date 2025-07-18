# GitHub Actions Setup Guide

## Созданные файлы

✅ **CI/CD workflows готовы:**
- `.github/workflows/ci.yml` - Continuous Integration
- `.github/workflows/cd.yml` - Continuous Deployment  
- `.github/dependabot.yml` - Автоматическое обновление зависимостей

## Необходимые настройки GitHub

### 1. Настройка GitHub Secrets

Перейдите в настройки репозитория: **Settings → Secrets and Variables → Actions**

#### Общие секреты (Repository secrets):
```
CODECOV_TOKEN=<токен для codecov.io (опционально)>
GITHUB_TOKEN=<автоматически предоставляется GitHub>
```

#### Секреты для Staging окружения:
```
STAGING_HOST=<IP или домен staging сервера>
STAGING_USER=<SSH пользователь для staging>
STAGING_SSH_KEY=<приватный SSH ключ для staging>
STAGING_PORT=22
STAGING_DATABASE_URL=postgresql+asyncpg://user:pass@staging-db:5432/clinical_samples_staging
STAGING_SECRET_KEY=<уникальный секретный ключ для staging>
```

#### Секреты для Production окружения:
```
PRODUCTION_HOST=<IP или домен production сервера>
PRODUCTION_USER=<SSH пользователь для production>
PRODUCTION_SSH_KEY=<приватный SSH ключ для production>
PRODUCTION_PORT=22
PRODUCTION_DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/clinical_samples_prod
PRODUCTION_SECRET_KEY=<уникальный секретный ключ для production>
```

### 2. Настройка GitHub Environments

#### Создание окружений:
1. **Settings → Environments → New environment**
2. Создайте два окружения:
   - `staging` (автоматический деплой)
   - `production` (требует approve)

#### Настройка Protection Rules для Production:
- **Required reviewers**: добавьте себя
- **Wait timer**: 5 минут (опционально)
- **Deployment branches**: Only protected branches

### 3. Генерация SSH ключей

```bash
# Генерация SSH ключей для серверов
ssh-keygen -t rsa -b 4096 -f ~/.ssh/staging_deploy_key -N ""
ssh-keygen -t rsa -b 4096 -f ~/.ssh/production_deploy_key -N ""

# Копирование публичных ключей на серверы
ssh-copy-id -i ~/.ssh/staging_deploy_key.pub user@staging-server
ssh-copy-id -i ~/.ssh/production_deploy_key.pub user@production-server

# Приватные ключи добавьте в GitHub Secrets
cat ~/.ssh/staging_deploy_key      # → STAGING_SSH_KEY
cat ~/.ssh/production_deploy_key   # → PRODUCTION_SSH_KEY
```

### 4. Генерация секретных ключей

```bash
# Генерация SECRET_KEY для разных окружений
openssl rand -hex 32  # → STAGING_SECRET_KEY
openssl rand -hex 32  # → PRODUCTION_SECRET_KEY
```

## Как работают workflows

### CI Workflow (`ci.yml`)
**Триггеры:** push/PR в main/develop
**Выполняет:**
- Линтинг (flake8, mypy, black, isort)
- Тесты с coverage
- Загрузка отчетов в Codecov

### CD Workflow (`cd.yml`)
**Триггеры:** push тегов `v*` (например, `v1.0.0`)
**Выполняет:**
1. Сборка Docker образа → GitHub Container Registry
2. Деплой в staging (автоматически)
3. Деплой в production (с approve)

## Подготовка серверов

### Требования к серверам:
- Docker установлен
- SSH доступ
- Открытые порты: 8000 (staging), 80 (production)
- PostgreSQL база данных

### Быстрая установка Docker:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## Процесс деплоя

### Релиз новой версии:
```bash
# 1. Создание и push тега
git tag v1.0.0
git push origin v1.0.0

# 2. GitHub Actions автоматически:
# - Соберет Docker образ
# - Задеплоит в staging
# - Создаст кнопку для деплоя в production
```

### Мониторинг деплоя:
- **Actions tab** → выберите workflow
- **Environments** → проверьте статус деплоя
- Health check: `curl http://your-server/health`

## Безопасность

### ✅ Что НЕ нужно делать:
- ❌ Не добавляйте .env файлы в git
- ❌ Не коммитьте секреты в код
- ❌ Не используйте одинаковые секреты для разных окружений

### ✅ Что нужно делать:
- ✅ Используйте GitHub Secrets для всех секретов
- ✅ Генерируйте уникальные ключи для каждого окружения
- ✅ Регулярно ротируйте SSH ключи
- ✅ Используйте отдельные базы данных для staging/production

## Troubleshooting

### Проблема: SSH connection failed
```bash
# Проверьте SSH ключи
ssh -i ~/.ssh/staging_deploy_key user@staging-server

# Проверьте формат ключа в GitHub Secrets (должен включать заголовки)
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

### Проблема: Docker image not found
- Проверьте что GITHUB_TOKEN имеет права на packages
- Проверьте что образ собрался: **Packages tab** в репозитории

### Проблема: Health check fails
- Проверьте что контейнер запустился: `docker ps`
- Проверьте логи: `docker logs clinical-sample-service-staging`
- Проверьте переменные окружения в GitHub Secrets

## Следующие шаги

1. **Настройте секреты** в GitHub Settings
2. **Создайте SSH ключи** для серверов
3. **Подготовьте серверы** (установите Docker)
4. **Создайте первый тег** для тестирования деплоя
5. **Проверьте мониторинг** и настройте алерты

🎉 **Готово!** Теперь у вас есть полноценный CI/CD pipeline для безопасного деплоя медицинского приложения.