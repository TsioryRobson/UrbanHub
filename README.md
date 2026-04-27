# urbanhub-ms-alerte

## Livrable L2 - Scripts complementaires

Les scripts suivants sont versionnes dans `ms-alerte-usager/scripts` pour industrialiser le build, les tests et le deploiement.

### Build

- Python: `python scripts/build.py --dev`
- Shell: `./scripts/build.sh --dev`

Options utiles:

- `--dev`: installe aussi `requirements-dev.txt`
- `--docker`: construit l'image Docker `ms-alerte-usager`

### Test

- Python: `python scripts/test.py`
- Shell: `./scripts/test.sh`

Ce script:

- installe les dependances runtime + dev
- execute `pytest` avec rapport JUnit et couverture
- execute `flake8` avec generation de `flake8-report.txt`

### Deploy (local Docker Compose)

- Python: `python scripts/deploy.py`
- Shell: `./scripts/deploy.sh`

Options utiles:

- `--down`: arret/suppression des conteneurs
- `--logs`: suivi des logs apres le `up`
- `--dry-run`: affiche les commandes sans execution

## Structure scripts

- `scripts/_common.py`: utilitaires d'execution de commandes et chemins projet
- `scripts/build.py`: build dependances et image Docker optionnelle
- `scripts/test.py`: qualite (tests + couverture + lint)
- `scripts/deploy.py`: deploiement local via Docker Compose
- `scripts/*.sh`: wrappers shell reutilisables

## Livrable L3 - Rapport de tests

Generation des artefacts demandes avec `pytest` + `coverage.py`:

- Python: `python scripts/report_tests.py`
- Shell: `./scripts/report_tests.sh`

Artefacts produits dans `ms-alerte-usager/`:

- `rapport_tests.txt`
- `rapport_tests.xml` (JUnit)
- `coverage_html/` (rapport HTML coverage)

## Livrable L4 - Rapport SonarQube + Snyk

Generation des exports SonarQube/Snyk et interpretation synthetique (faible/modere/critique):

- Python: `python scripts/security_report.py`
- Shell: `./scripts/security_report.sh`

Variables d'environnement attendues pour exports complets:

- `SONAR_TOKEN`
- `SONAR_HOST_URL` (optionnel, defaut: `https://sonarcloud.io`)
- `SONAR_PROJECT_KEY` (optionnel, defaut: `RobelManoa_urbanhub-ms-alerte`)
- `SNYK_TOKEN`

Artefacts produits dans `ms-alerte-usager/reports/security/`:

- `sonar_issues.json`
- `sonar_export_status.json`
- `snyk_issues.json`
- `snyk_export_status.json`
- `rapport_sonar_snyk.md`

## Livrable L5 - Documentation GitHub Wiki/Pages

Documentation prete a publier sur GitHub Wiki/Pages (6 sections):

- Point d'entree: `ms-alerte-usager/document/wiki/Home.md`
- 1) Vue d'ensemble: `ms-alerte-usager/document/wiki/01-vue-d-ensemble.md`
- 2) Etapes: `ms-alerte-usager/document/wiki/02-etapes.md`
- 3) Outils: `ms-alerte-usager/document/wiki/03-outils.md`
- 4) Prerequis: `ms-alerte-usager/document/wiki/04-prerequis.md`
- 5) Qualite et dette: `ms-alerte-usager/document/wiki/05-qualite-dette.md`
- 6) Integration UrbanHub: `ms-alerte-usager/document/wiki/06-integration-urbanhub.md`
