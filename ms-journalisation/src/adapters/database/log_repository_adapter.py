"""
Adapter de base de données : LogRepositoryAdapter
Implémentation de la persistance des logs
"""
from typing import List, Optional
from uuid import uuid4
from src.domain.log import Log
from src.ports.log_repository_port import LogRepositoryPort


class InMemoryLogRepository(LogRepositoryPort):
    """Implémentation en mémoire du repository (pour tests et développement)"""

    def __init__(self):
        """Initialise le repository en mémoire"""
        self.logs: dict = {}

    def save(self, log: Log) -> str:
        """Sauvegarde un log en mémoire"""
        if not log.log_id:
            log.log_id = str(uuid4())
        self.logs[log.log_id] = log
        return log.log_id

    def find_by_id(self, log_id: str) -> Optional[Log]:
        """Récupère un log par son identifiant"""
        return self.logs.get(log_id)

    def find_by_service(self, service: str) -> List[Log]:
        """Récupère tous les logs d'un service"""
        return [log for log in self.logs.values() if log.service == service]

    def find_by_level(self, level: str) -> List[Log]:
        """Récupère tous les logs d'un niveau spécifique"""
        return [log for log in self.logs.values() if log.level == level]

    def find_all(self) -> List[Log]:
        """Récupère tous les logs"""
        return list(self.logs.values())

    def delete_by_id(self, log_id: str) -> bool:
        """Supprime un log par son identifiant"""
        if log_id in self.logs:
            del self.logs[log_id]
            return True
        return False


class SQLiteLogRepository(LogRepositoryPort):
    """Implémentation avec SQLite du repository"""

    def __init__(self, db_path: str = "logs.db"):
        """
        Initialise le repository SQLite

        Args:
            db_path: Chemin du fichier SQLite
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialise la base de données"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id TEXT PRIMARY KEY,
                service TEXT NOT NULL,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                level TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)

        conn.commit()
        conn.close()

    def save(self, log: Log) -> str:
        """Sauvegarde un log en base de données"""
        import sqlite3
        import json

        if not log.log_id:
            log.log_id = str(uuid4())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO logs (id, service, event_type, message, level, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            log.log_id,
            log.service,
            log.event_type,
            log.message,
            log.level,
            log.timestamp.isoformat(),
            json.dumps(log.metadata)
        ))

        conn.commit()
        conn.close()

        return log.log_id

    def find_by_id(self, log_id: str) -> Optional[Log]:
        """Récupère un log par son identifiant"""
        import sqlite3
        import json

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM logs WHERE id = ?", (log_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_log(row)

    def find_by_service(self, service: str) -> List[Log]:
        """Récupère tous les logs d'un service"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM logs WHERE service = ?", (service,))
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_log(row) for row in rows]

    def find_by_level(self, level: str) -> List[Log]:
        """Récupère tous les logs d'un niveau spécifique"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM logs WHERE level = ?", (level,))
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_log(row) for row in rows]

    def find_all(self) -> List[Log]:
        """Récupère tous les logs"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM logs")
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_log(row) for row in rows]

    def delete_by_id(self, log_id: str) -> bool:
        """Supprime un log par son identifiant"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM logs WHERE id = ?", (log_id,))
        conn.commit()
        rows_deleted = cursor.rowcount
        conn.close()

        return rows_deleted > 0

    @staticmethod
    def _row_to_log(row) -> Log:
        """Convertit une ligne SQLite en objet Log"""
        import json
        from datetime import datetime

        log_id, service, event_type, message, level, timestamp, metadata = row

        return Log(
            service=service,
            event_type=event_type,
            message=message,
            level=level,
            timestamp=datetime.fromisoformat(timestamp),
            metadata=json.loads(metadata) if metadata else {},
            log_id=log_id
        )
