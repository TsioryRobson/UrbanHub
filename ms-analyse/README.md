# ms-analyse

`ms-analyse` est le microservice charge d'analyser les donnees trafic publiees par `ms-collecte-iot`.

Il recoit une fenetre de circulation normalisee via RabbitMQ, produit une analyse metier, republie les messages utiles sur RabbitMQ, persiste les analyses dashboard dans sa propre base PostgreSQL, et expose ces donnees via API REST.

## Role du microservice

`ms-analyse` transforme une fenetre de trafic en informations utiles pour plusieurs consommateurs:
- dashboard utilisateur via API
- microservice d'alerte via RabbitMQ
- notifications utilisateur via RabbitMQ
- logs techniques via RabbitMQ
- KPI metier via RabbitMQ
- historisation a brancher plus tard

Exemples d'analyses calculees:
- vitesse moyenne
- vitesse min / max
- debit de trafic par minute
- type de vehicule dominant
- nombre de vehicules lents
- nombre de poids lourds
- niveau de congestion
- message lisible pour l'utilisateur

## Architecture hexagonale

Le projet suit une architecture hexagonale simple:

- `src/domain`
  Entites metier et logique pure d'analyse trafic.
- `src/application`
  Use case `AnalyzeTrafficUseCase`.
- `src/ports`
  Interfaces metier pour les adaptateurs entrants et sortants.
- `src/adapters/api`
  Contrats HTTP FastAPI.
- `src/adapters/database`
  Modeles SQLAlchemy et repository de persistence PostgreSQL/SQL.
- `src/adapters/rabbitmq`
  Consumer d'entree et publisher de sortie RabbitMQ.
- `src/main.py`
  Composition de l'application FastAPI et demarrage du consumer RabbitMQ.

## Flux entrant

Le message entrant est publie par `ms-collecte-iot` dans la queue `collecte_queue`.

Format attendu:

```json
{
  "sensorId": "sensor-1",
  "zoneId": "zone-A",
  "windowStart": "2026-04-11T10:00:00Z",
  "windowEnd": "2026-04-11T10:00:15Z",
  "vehicles": [
    { "speedKmh": 45, "vehicleType": "car" },
    { "speedKmh": 40, "vehicleType": "truck" },
    { "speedKmh": 20, "vehicleType": "car" }
  ],
  "vehicleCount": 3
}
```

## Flux sortants

Le service retourne une structure interne avec une liste `outputs`, puis republie automatiquement certaines sorties sur RabbitMQ.

| Destination | Canal | Transport actuel | Contenu |
| --- | --- | --- | --- |
| Dashboard | API REST + base PostgreSQL dediee | HTTP + SQL | resultat detaille |
| MS Alerte | `alert_queue` | RabbitMQ | alerte simplifiee |
| Conducteur | `analysis.user.notification` | RabbitMQ | message lisible |
| MS Log | `log.events` | RabbitMQ | trace technique |
| KPI metier | `analysis.traffic.kpi` | RabbitMQ | indicateurs agreges |
| Historisation | `postgresql.analysis_results` | non branche | analyses calculees |

## Endpoints

### `GET /health`

Verifie que le service est disponible.

Reponse:

```json
{
  "status": "ok"
}
```

### `POST /traffic/analyze`

Permet de lancer manuellement une analyse avec le meme format que celui publie par `ms-collecte-iot`.

Cette route:
- calcule l'analyse metier
- publie les sorties RabbitMQ configurees
- stocke le resultat dashboard en base

### `GET /traffic/dashboard`

Retourne les dernieres analyses disponibles pour affichage dashboard.

Exemple de reponse:

```json
{
  "items": [
    {
      "zoneId": "zone-A",
      "sensorId": "sensor-1",
      "windowStart": "2026-04-11T10:00:00+00:00",
      "windowEnd": "2026-04-11T10:00:15+00:00",
      "trafficState": "medium",
      "averageSpeedKmh": 35.0,
      "vehicleCount": 3,
      "flowRatePerMinute": 12.0
    }
  ]
}
```

## Regles metier actuelles

Le domaine applique actuellement des regles simples:
- calcul de la vitesse moyenne, min et max
- calcul du nombre de vehicules lents (`speedKmh < 30`)
- calcul du nombre de poids lourds (`truck`, `bus`)
- calcul du type de vehicule dominant
- calcul d'un debit estime par minute
- classification du trafic en `low`, `medium` ou `high`

Ces seuils sont encore heuristiques et pourront etre ajustes selon les besoins metier.

## Configuration

Variables d'environnement utiles:

```bash
DATABASE_URL=postgresql://user:password@localhost:5436/analysis
RABBITMQ_HOST=localhost
RABBITMQ_INPUT_QUEUE=collecte_queue
ENABLE_RABBITMQ_CONSUMER=true
```

Quand `ENABLE_RABBITMQ_CONSUMER=true`, le service demarre un consumer RabbitMQ en arriere-plan au lancement de FastAPI.

Si `DATABASE_URL` n'est pas fourni, le service utilise par defaut `sqlite:///./ms_analyse.db` pour un lancement local simple. Dans `docker-compose`, `ms-analyse` est configure pour utiliser une instance PostgreSQL dediee: base `analysis` sur le service `analysis-db`.

## Lancement local

### Avec Python

```bash
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8003
```

### Avec Docker Compose

Depuis la racine du projet:

```bash
docker compose up -d --build ms-analyse
```

## Tests

Lancer les tests:

```bash
pytest
```

Le projet contient actuellement:
- un test de sante
- un test d'analyse trafic via l'endpoint HTTP
- un test de consultation des derniers resultats dashboard

## Limites actuelles

Les points suivants restent a brancher si on veut aller plus loin:
- consommation directe des evenements dashboard par un frontend ou une gateway
- schemas de messages versionnes entre microservices

## Fichiers principaux

- [src/main.py](./src/main.py)
- [src/domain/entities.py](./src/domain/entities.py)
- [src/domain/services.py](./src/domain/services.py)
- [src/application/use_cases/analyze_traffic_use_case.py](./src/application/use_cases/analyze_traffic_use_case.py)
- [src/adapters/database/models.py](./src/adapters/database/models.py)
- [src/adapters/database/repository.py](./src/adapters/database/repository.py)
- [src/adapters/rabbitmq/consumer.py](./src/adapters/rabbitmq/consumer.py)
- [src/adapters/rabbitmq/publisher.py](./src/adapters/rabbitmq/publisher.py)
- [src/adapters/api/schemas.py](./src/adapters/api/schemas.py)
