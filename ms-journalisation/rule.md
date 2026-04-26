🧩 Construction du Microservice Journalisation
🎯 Objectif
Le microservice Journalisation a pour rôle de :
Centraliser les logs de tous les microservices
Assurer la traçabilité des actions système
Faciliter le monitoring, le debugging et l’audit
Stocker les événements techniques et métier
🏗️ 1. Architecture adoptée
Le microservice repose sur une architecture hexagonale (Ports & Adapters).
🔹 Principe
Séparer :
Le cœur métier (gestion des logs)
Des composants techniques (RabbitMQ, base de données, API)
📂 Structure du projet
src/
├── domain/          # Entité Log
├── application/     # Use case (ProcessLogUseCase)
├── ports/           # Interfaces (LogRepositoryPort, LogConsumerPort)
├── adapters/
│   ├── database/    # Implémentation stockage
│   ├── rabbitmq/    # Consumer logs
│   └── api/         # API consultation (optionnelle)
└── main.py          # Point d’entrée
🔁 2. Flux global des données
📥 Entrée (Input)
Les données proviennent de tous les microservices via RabbitMQ.
Exemple de log consommé
{
  "service": "MS Alerte",
  "event_type": "notification_sent",
  "message": "Email envoyé avec succès",
  "level": "INFO",
  "timestamp": "2026-04-21T10:00:00"
}
👉 Sources possibles :
MS Alerte
MS Analyse
MS Collecte
MS Authentification
API Gateway
🐇 3. Consommation via RabbitMQ
Le microservice écoute une queue dédiée (ex: logs_queue)
Les messages sont reçus de manière asynchrone
Chaque log est transformé en objet métier Log
⚙️ 4. Traitement métier (Use Case)
Le cœur du système est le ProcessLogUseCase
Étapes :
1. Transformation
JSON → Objet métier Log
2. Validation
Vérification des champs obligatoires
Normalisation des données
3. Enrichissement (optionnel)
Ajout du niveau de log (INFO / WARNING / ERROR)
Ajout de métadonnées (service source, contexte)
4. Sauvegarde
Stockage en base de données
📤 5. Sorties du microservice
🔹 Base de données
Stockage des logs pour audit et analyse
Table Log
id
service
event_type
message
level
timestamp
🔹 (Optionnel) API REST
Endpoints possibles :
GET /logs → consulter tous les logs
GET /logs/errors → filtrer erreurs
GET /logs/{service} → logs par service
🔹 (Optionnel) Intégration monitoring
Dashboard (Grafana, Kibana)
Alerting en cas d’erreur critique
🔄 6. Résumé du flux
Microservices (Alerte, Analyse, Collecte, etc.)
        ↓
     RabbitMQ
        ↓
Microservice Journalisation
        ↓
Transformation → Log
        ↓
Use Case
        ↓
Base de données
        ↓
(API / Monitoring / Audit)
🧠 7. Avantages de l’architecture
🔌 Découplage total des logs
⚡ Traitement asynchrone
📊 Centralisation des événements
🛠️ Facilite le debugging
🔐 Support pour audit et sécurité
⚠️ 8. Points de vigilance
Volume élevé de logs (scalabilité nécessaire)
Gestion des logs critiques (ERROR)
Risque de saturation du broker
Nécessité de filtrage et archivage
🚀 Conclusion
Le microservice Journalisation est un composant clé de l’architecture UrbanHub.
Il permet de centraliser et exploiter les logs du système, garantissant une meilleure visibilité, une traçabilité complète et un support efficace pour la maintenance et la supervision.