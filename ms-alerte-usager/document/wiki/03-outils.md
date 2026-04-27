# 3) Outils

## Developpement

- Python 3.12+
- pip
- pytest
- coverage.py (via pytest-cov)
- flake8

## Runtime

- PostgreSQL 16
- RabbitMQ 3.13 (management)
- Docker / Docker Compose

## Qualite et securite

- GitHub Actions pour CI
- SonarQube/SonarCloud pour l'analyse de code
- Snyk pour la securite des dependances

## Scripts versionnes

- scripts/build.py
- scripts/test.py
- scripts/report_tests.py
- scripts/security_report.py
- scripts/deploy.py
