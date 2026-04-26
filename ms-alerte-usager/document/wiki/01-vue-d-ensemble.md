# 1) Vue d'ensemble

## Objectif du service

Le microservice ms-alerte-usager consomme des alertes depuis RabbitMQ, enregistre les alertes en base, puis declenche les notifications vers les utilisateurs cibles.

## Flux fonctionnel

1. Reception d'un message d'alerte sur la queue RabbitMQ.
2. Transformation en entite Alert.
3. Sauvegarde de l'alerte dans PostgreSQL.
4. Recuperation des utilisateurs a notifier.
5. Envoi des notifications (email/sms).

## Architecture

- Domain: entites metier.
- Application: use case ProcessAlertUseCase.
- Ports: contrats repository/notification/consumer.
- Adapters: RabbitMQ, SQLAlchemy, notification service.

## Point d'entree

- Execution principale: src/main.py
- Orchestration locale: docker-compose.yml
