"""
ASPERA Memory System
====================
Gestisce memoria episodica e semantica per il cognitive engine.
Include stub per vector database per future integrazioni.

Author: Christian Quintino De Luca - RTH Italia
"""

from typing import Any, Dict, List, Optional, Tuple
import logging
from datetime import datetime
from collections import deque
import json

logger = logging.getLogger(__name__)

# Optional vector DB integration
try:
    from aspera.integrations.vector_db import VectorDB, create_vector_db
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False
    VectorDB = None


class Episode:
    """Rappresenta un episodio nella memoria episodica"""

    def __init__(self, event_type: str, data: Dict[str, Any], timestamp: datetime = None):
        self.id = f"episode_{id(self)}"
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.tags: List[str] = []
        self.importance: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "importance": self.importance
        }


class MemorySystem:
    """
    Sistema di memoria per ASPERA.
    
    Gestisce:
    - Memoria episodica: eventi temporali sequenziali
    - Memoria semantica: conoscenze concettuali (stub per vector DB)
    - Memoria di lavoro: contesto corrente
    """

    def __init__(self, max_episodes: int = 1000, vector_dim: int = 768):
        self.max_episodes = max_episodes
        self.vector_dim = vector_dim

        # Memoria episodica (FIFO con limite)
        self.episodic_memory: deque = deque(maxlen=max_episodes)

        # Memoria semantica (attualmente dizionario, future: vector DB)
        self.semantic_memory: Dict[str, Any] = {}

        # Memoria di lavoro (sliding window degli ultimi N episodi)
        self.working_memory_size = 10
        self.working_memory: List[Episode] = []

        # Statistiche
        self.stats = {
            "total_episodes": 0,
            "total_retrievals": 0,
            "cache_hits": 0
        }

        logger.info(f"MemorySystem initialized (max_episodes={max_episodes}, vector_dim={vector_dim})")

    def store_episode(self, event_type: str, data: Dict[str, Any],
                      importance: float = 0.5, tags: List[str] = None) -> Episode:
        """
        Memorizza un episodio.

        Args:
            event_type: Tipo di evento
            data: Dati dell'episodio
            importance: Importanza (0-1)
            tags: Tag per categorizzazione

        Returns:
            Episodio creato
        """
        episode = Episode(event_type, data)
        episode.importance = importance
        episode.tags = tags or []

        self.episodic_memory.append(episode)
        self.stats["total_episodes"] += 1

        # Aggiorna working memory
        self._update_working_memory()

        logger.debug(f"Stored episode: {event_type} (importance: {importance})")
        return episode

    def retrieve_episodes(self, event_type: Optional[str] = None,
                          tags: Optional[List[str]] = None,
                          limit: int = 10,
                          min_importance: float = 0.0) -> List[Episode]:
        """
        Recupera episodi dalla memoria.

        Args:
            event_type: Filtra per tipo (opzionale)
            tags: Filtra per tag (opzionale)
            limit: Numero massimo di risultati
            min_importance: Importanza minima

        Returns:
            Lista di episodi
        """
        self.stats["total_retrievals"] += 1

        # Filtra episodi
        results = []
        for episode in reversed(self.episodic_memory):  # Dal più recente
            if event_type and episode.event_type != event_type:
                continue
            if tags and not any(tag in episode.tags for tag in tags):
                continue
            if episode.importance < min_importance:
                continue

            results.append(episode)
            if len(results) >= limit:
                break

        logger.debug(f"Retrieved {len(results)} episodes (filters: type={event_type}, tags={tags})")
        return results

    def store_semantic(self, key: str, value: Any, metadata: Dict[str, Any] = None):
        """
        Memorizza conoscenza semantica.

        Args:
            key: Chiave identificativa
            value: Valore da memorizzare
            metadata: Metadati opzionali
        """
        self.semantic_memory[key] = {
            "value": value,
            "metadata": metadata or {},
            "updated_at": datetime.utcnow().isoformat()
        }
        logger.debug(f"Stored semantic knowledge: {key}")

    def retrieve_semantic(self, key: str) -> Optional[Any]:
        """
        Recupera conoscenza semantica.

        Args:
            key: Chiave identificativa

        Returns:
            Valore memorizzato o None
        """
        if key in self.semantic_memory:
            self.stats["cache_hits"] += 1
            return self.semantic_memory[key]["value"]
        return None

    def query_semantic_similarity(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Query semantica per similarità (stub per vector DB).

        Args:
            query: Query testuale
            top_k: Numero di risultati

        Returns:
            Lista di (key, similarity_score)
        """
        # TODO: Implementare con vector DB (FAISS, Chroma, etc.)
        logger.warning("Semantic similarity query not implemented (stub)")
        return []

    def _update_working_memory(self):
        """Aggiorna la working memory con gli episodi più recenti"""
        recent = list(self.episodic_memory)[-self.working_memory_size:]
        self.working_memory = recent

    def get_working_memory(self) -> List[Episode]:
        """Ritorna la working memory corrente"""
        return self.working_memory

    def consolidate(self, strategy: str = "importance"):
        """
        Consolida la memoria (rimuove episodi meno importanti).

        Args:
            strategy: Strategia di consolidamento ('importance', 'recency', 'frequency')
        """
        if len(self.episodic_memory) < self.max_episodes:
            return  # Non necessario

        if strategy == "importance":
            # Mantieni solo episodi con importanza > soglia
            threshold = 0.5
            to_keep = [ep for ep in self.episodic_memory if ep.importance >= threshold]
            self.episodic_memory = deque(to_keep, maxlen=self.max_episodes)
            logger.info(f"Memory consolidated (importance): kept {len(to_keep)} episodes")

        elif strategy == "recency":
            # Mantieni solo i più recenti (già gestito da deque maxlen)
            logger.info("Memory consolidated (recency): automatic via deque")

        # TODO: Implementare altre strategie

    def get_stats(self) -> Dict[str, Any]:
        """Ritorna statistiche della memoria"""
        return {
            **self.stats,
            "episodic_count": len(self.episodic_memory),
            "semantic_count": len(self.semantic_memory),
            "working_memory_size": len(self.working_memory)
        }

    def export_to_json(self, filepath: str):
        """Esporta memoria su file JSON"""
        data = {
            "episodic_memory": [ep.to_dict() for ep in self.episodic_memory],
            "semantic_memory": self.semantic_memory,
            "stats": self.get_stats()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Memory exported to {filepath}")

    def clear(self):
        """Pulisce tutta la memoria"""
        self.episodic_memory.clear()
        self.semantic_memory.clear()
        self.working_memory.clear()
        logger.info("Memory cleared")

