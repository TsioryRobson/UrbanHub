# 6) Integration UrbanHub

## Positionnement

ms-alerte-usager est le composant de diffusion des alertes dans la plateforme UrbanHub.

## Contrat d'entree

- Canal: RabbitMQ
- Queue: alert_queue (par defaut)
- Payload attendu:
  - type
  - message
  - severity
  - source

## Contrat de persistence

- Base PostgreSQL
- Sauvegarde des alertes via SQLAlchemy
- Stockage des notifications emises

## Contrat de sortie

- NotificationPort pour abstraction des canaux
- Canaux courants: email et sms

## Integration technique

- Compose orchestre db + rabbitmq + ms-alerte-usager
- Le service demarre apres checks de sante db/rabbitmq
- Le workflow CI valide qualite avant fusion

## Points de gouvernance UrbanHub

- Tracabilite des executions via rapports tests et securite
- Qualite continue avec SonarQube et Snyk
- Scripts standardises pour reproductibilite build/test/deploy
