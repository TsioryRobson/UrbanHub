# 2) Etapes

## Etape 1 - Build

- Installer les dependances:
  - python scripts/build.py --dev
- Option image Docker:
  - python scripts/build.py --docker

## Etape 2 - Test

- Lancer la qualite locale:
  - python scripts/test.py

## Etape 3 - Rapport de tests

- Generer les rapports L3:
  - python scripts/report_tests.py
- Artefacts:
  - rapport_tests.txt
  - rapport_tests.xml
  - coverage_html/

## Etape 4 - Securite SonarQube + Snyk

- Generer les exports L4:
  - python scripts/security_report.py
- Artefacts:
  - reports/security/sonar_issues.json
  - reports/security/snyk_issues.json
  - reports/security/rapport_sonar_snyk.md

## Etape 5 - Deploiement local

- Demarrer la stack:
  - python scripts/deploy.py
- Arreter la stack:
  - python scripts/deploy.py --down
