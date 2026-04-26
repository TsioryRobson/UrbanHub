# 4) Prerequis

## Environnement local

- Python installe et accessible dans PATH
- Docker Desktop actif
- Ports libres: 5432 (PostgreSQL), 5672 et 15672 (RabbitMQ)

## Variables d'environnement

### Runtime

- DATABASE_URL (defaut present dans src/main.py)
- RABBITMQ_HOST
- RABBITMQ_QUEUE

### SonarQube/Snyk (L4)

- SONAR_TOKEN
- SONAR_HOST_URL (optionnel, defaut: https://sonarcloud.io)
- SONAR_PROJECT_KEY (optionnel)
- SNYK_TOKEN

## Installation rapide

- Depuis ms-alerte-usager:
  - python scripts/build.py --dev
