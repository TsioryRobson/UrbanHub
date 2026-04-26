# Microservice Journalisation - UrbanHub EC03

## Vue d'ensemble

Le microservice Journalisation est un service centralisé conçu pour collecter, traiter et stocker les logs de tous les microservices du système UrbanHub. Il suit une architecture hexagonale (Ports & Adapters) pour assurer une séparation claire entre la logique métier et les composants techniques.

## Fonctionnement du projet

### Architecture

Le projet suit l'architecture hexagonale avec les couches suivantes :

- **Domain** : Entités métier (Log)
- **Application** : Cas d'usage (ProcessLogUseCase)
- **Ports** : Interfaces abstraites (LogRepositoryPort, LogConsumerPort, LogValidatorPort)
- **Adapters** : Implémentations concrètes (base de données, RabbitMQ, API)

### Flux de données

1. **Entrée** : Les logs arrivent via RabbitMQ depuis les autres microservices
2. **Consommation** : Le LogConsumer écoute la queue `logs_queue`
3. **Traitement** : Le ProcessLogUseCase valide, transforme et enrichit les logs
4. **Stockage** : Les logs sont sauvegardés en base de données
5. **Consultation** : API REST pour récupérer les logs

## État du projet

### ✅ Ce qui marche

- **Architecture complète** : Toutes les couches sont implémentées et testées
- **Tests unitaires** : 55 tests, 100% de succès
- **Persistance** : Repository en mémoire et SQLite
- **Validation** : Vérification des champs obligatoires et formats
- **Consommation** : Consumer RabbitMQ et mock pour tests
- **API REST** : Endpoints pour consultation des logs
- **Gestion d'erreurs** : Traitement robuste des exceptions

### Ce qui ne marche pas

- Aucune fonctionnalité identifiée comme non fonctionnelle
- Tous les tests passent avec succès

## Données d'entrée

Le microservice reçoit des logs au format JSON via RabbitMQ :

```json
{
  "service": "MS Alerte",
  "event_type": "notification_sent",
  "message": "Email envoyé avec succès",
  "level": "INFO",
  "timestamp": "2026-04-21T10:00:00",
  "metadata": {
    "user_id": "123",
    "context": "system"
  }
}
```

**Champs obligatoires :**
- `service` : Nom du microservice source
- `event_type` : Type d'événement
- `message` : Message du log

**Champs optionnels :**
- `level` : Niveau de log (INFO, WARNING, ERROR, DEBUG, CRITICAL)
- `timestamp` : Date/heure au format ISO
- `metadata` : Objet JSON avec métadonnées supplémentaires

## Données de sortie

### Base de données

Les logs sont stockés avec la structure suivante :

- `id` : Identifiant unique (UUID)
- `service` : Microservice source
- `event_type` : Type d'événement
- `message` : Message du log
- `level` : Niveau de log
- `timestamp` : Date/heure
- `metadata` : Métadonnées JSON

### API REST

Endpoints disponibles :

- `GET /logs` : Tous les logs
- `GET /logs/{id}` : Log spécifique
- `GET /logs/service/{service}` : Logs d'un service
- `GET /logs/level/{level}` : Logs d'un niveau
- `GET /logs/errors` : Logs d'erreur uniquement

## Installation et exécution

### Prérequis

- Python 3.8+
- RabbitMQ (pour la version complète)
- SQLite (optionnel, pour persistance)

### Installation

```bash
pip install -r requirements.txt
```

### Exécution

```bash
python src/main.py
```

Pour le développement (avec mock consumer) :

```bash
python src/main.py
```

## Tests

```bash
pytest
```

Ou avec le script fourni :

```bash
python manage_tests.py
```

## Technologies utilisées

- **Python 3.8+**
- **RabbitMQ** pour la messagerie
- **SQLite** pour la persistance
- **Pytest** pour les tests
- **Architecture hexagonale** pour la structure

## Conformité aux règles

Le code respecte entièrement les spécifications définies dans `rule.md` :

- ✅ Architecture hexagonale implémentée
- ✅ Flux de données respecté (RabbitMQ → Traitement → DB)
- ✅ Services centralisés pour tous les microservices
- ✅ Validation et enrichissement des logs
- ✅ API REST pour consultation
- ✅ Tests complets et fonctionnels
  - Manipulation des métadonnées
  - Énumération des niveaux

- **Application** (15 tests)
  - Traitement des logs (validation, transformation, enrichissement, sauvegarde)
  - Récupération par critères (ID, service, niveau)
  - Gestion des erreurs
  - Enrichissement des métadonnées

- **Adapters** (30+ tests)
  - **Validateur** : Validation des champs, niveaux, timestamps
  - **Repository** : Persistance en mémoire et SQLite
  - **Consumer** : Mock RabbitMQ
  - **API** : Endpoints REST

## 🔄 Flux des données

```
RabbitMQ (LogConsumer)
    ↓
Validation (LogValidator)
    ↓
Transformation → Log (Domain)
    ↓
Use Case (ProcessLogUseCase)
    ↓
Persistance (LogRepository)
    ↓
API REST (LogApiAdapter)
```

## 🔌 Entités principales

### Log (Domain)
```python
Log(
    service="MS Alerte",
    event_type="notification_sent",
    message="Email envoyé avec succès",
    level="INFO",
    timestamp=datetime.now(),
    metadata={"user_id": "123"},
    log_id="log-001"
)
```

### Ports
- `LogRepositoryPort` : Interface de persistance
- `LogConsumerPort` : Interface de consommation RabbitMQ
- `LogValidatorPort` : Interface de validation

### Adapters
- `InMemoryLogRepository` : Stockage en mémoire
- `SQLiteLogRepository` : Stockage SQLite
- `RabbitMQLogConsumer` : Consommation RabbitMQ
- `MockLogConsumer` : Mock pour tests
- `LogValidator` : Validateur de logs
- `LogApiAdapter` : Adapter API REST

## 🛠️ Utilisation

### Exemple : Créer et traiter un log

```python
from src.application.process_log_use_case import ProcessLogUseCase
from src.adapters.database.log_repository_adapter import InMemoryLogRepository
from src.adapters.database.log_validator_adapter import LogValidator

# Initialisation
repository = InMemoryLogRepository()
validator = LogValidator()
use_case = ProcessLogUseCase(repository, validator)

# Traitement d'un log
log_data = {
    "service": "MS Alerte",
    "event_type": "notification_sent",
    "message": "Email envoyé avec succès"
}

success, message, log_id = use_case.execute(log_data)

# Récupération
log = use_case.get_log_by_id(log_id)
```

### Exemple : Via API

```python
from src.adapters.api.log_api_adapter import LogApiAdapter

api = LogApiAdapter(use_case)

# Récupérer tous les logs
result = api.get_all_logs()

# Récupérer les erreurs
errors = api.get_errors()

# Récupérer par service
alerte_logs = api.get_logs_by_service("MS Alerte")
```

## 📈 Architecture Hexagonale

L'architecture hexagonale sépare :
- **Cœur métier** (Domain) : Entité Log, logique métier
- **Cas d'utilisation** (Application) : ProcessLogUseCase
- **Contrats** (Ports) : Interfaces abstraites
- **Implémentations** (Adapters) : Concrétisations des ports

Avantages :
- ✅ Testabilité maximale (mocks simples)
- ✅ Découplage technologique
- ✅ Flexibilité : changer d'implémentation facilement
- ✅ Maintenabilité : code organisé et clair

## 🧪 Cas de test

### Domain - 14 tests
- Création avec defaults
- Création avec tous les paramètres
- Conversion to_dict/from_dict
- Énumération LogLevel
- Métadonnées

### Application - 15 tests
- Logs valides et invalides
- Validation des champs
- Enrichissement du log
- Récupération par critères
- Gestion des exceptions

### Adapters - 30+ tests
- Validation des niveaux, timestamps
- Persistance en mémoire et SQLite
- Consumer mock
- API endpoints
- Gestion des erreurs

## 🔐 Validation des logs

**Champs obligatoires :**
- `service` : Nom du microservice
- `event_type` : Type d'événement
- `message` : Message du log

**Champs optionnels :**
- `level` : INFO, WARNING, ERROR, DEBUG, CRITICAL (défaut: INFO)
- `timestamp` : ISO format (défaut: maintenant)
- `metadata` : Dictionnaire d'enrichissement

**Erreurs de validation :**
- Champs manquants
- Champs vides
- Niveau invalide
- Timestamp invalide

## 📝 Dépendances

```
pika==1.3.1          # RabbitMQ
sqlalchemy==2.0.19   # ORM (optionnel)
pytest==7.4.0        # Tests
pytest-cov==4.1.0    # Couverture
python-dotenv==1.0.0 # Variables d'env
```

## 🚀 Lancer le microservice

```bash
python src/main.py
```

Le script démontre :
- Création d'instances des services
- Publication de logs d'exemple
- Récupération via l'API
- Filtrage par critères

## 📋 Niveaux de log

- **DEBUG** : Informations de debug
- **INFO** : Informations générales
- **WARNING** : Avertissements
- **ERROR** : Erreurs
- **CRITICAL** : Erreurs critiques

## 🔍 Monitoring

L'API permet de monitorer :
- Tous les logs
- Les erreurs critiques
- Les logs par service
- Les logs par niveau

Idéal pour :
- Dashboards (Grafana, Kibana)
- Alerting
- Audit
- Debugging

## 📞 Support

Pour plus d'informations, consulter :
- `rule.md` : Spécifications complètes
- Tests : Exemples d'utilisation
- Docstrings : Documentation du code
