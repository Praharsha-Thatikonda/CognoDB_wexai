from src.harness.adapters.neo4j_adapter import Neo4jAdapter

class FalkorDBAdapter(Neo4jAdapter):
    """
    FalkorDB is Bolt/Cypher compatible, so it can reuse the Neo4j adapter logic.
    """
    pass
