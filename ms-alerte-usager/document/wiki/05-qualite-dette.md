# 5) Qualite et dette

## Dispositif qualite

- Tests unitaires: pytest
- Couverture: coverage XML + HTML
- Lint: flake8
- Analyse de code: SonarQube
- Securite dependances: Snyk

## Sorties de qualite

- rapport_tests.txt
- rapport_tests.xml
- coverage_html/
- reports/security/rapport_sonar_snyk.md

## Dette technique identifiee

- NotificationService est un stub (print) et non une integration provider.
- Repository retourne tous les utilisateurs (pas de filtrage metier cible).
- Gestion d'erreurs metier limitee dans le flux de consommation.
- Secrets locaux non fournis par defaut (exports Sonar/Snyk en mode fallback).

## Plan de reduction de dette

1. Brancher de vrais connecteurs email/sms.
2. Ajouter regles de ciblage usagers dans le repository.
3. Ajouter retries/monitoring sur la consommation RabbitMQ.
4. Exiger secrets en CI protegee et policy de qualite bloquante.
