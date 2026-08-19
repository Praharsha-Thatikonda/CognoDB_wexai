from src.harness.adapters.neo4j_adapter import Neo4jAdapter

class CognoDBAdapter(Neo4jAdapter):
    """
    CognoDB is Bolt/Cypher compatible, so it can reuse the Neo4j adapter logic.
    We subclass it simply to separate the metrics and handle any specific quirks if needed.
    """
    pass
