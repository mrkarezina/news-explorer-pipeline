from knowledge_graph.secrets import NEO4J_CONNECTION_STRING

# Neo4j connection string
GRAPH_URL = NEO4J_CONNECTION_STRING

# URL of language processor API
LANGUAGE_PROCESSOR_API = "https://us-central1-graph-intelligence.cloudfunctions.net/language-processor-health "

# Timeout between inserting articles in seconds
TIMEOUT = 1

# Maximum articles to insert
MAX_ARTICLES = 300

# Specifies the cluster of articles in the knowledge graph
DB_IDS = {
    'cluster_id': 1,
    'user_id': "cnn"
}
