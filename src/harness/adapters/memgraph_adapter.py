from src.harness.adapters.neo4j_adapter import Neo4jAdapter

class MemgraphAdapter(Neo4jAdapter):
    """
    Memgraph is Bolt/Cypher compatible, so it can reuse the Neo4j adapter logic.
    """
    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            # In some memgraph versions, dropping all indexes is needed if recreating them
            # session.run("DROP INDEX ON :User(id)")
