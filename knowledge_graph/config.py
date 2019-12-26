from knowledge_graph.secrets import IBM_WATSON_API_KEY, NEO4J_CONNECTION_STRING

# Neo4j connection string
GRAPH_URL = NEO4J_CONNECTION_STRING

# IBM cloud api key
IBM_WATSON_API_KEY = IBM_WATSON_API_KEY

# URL of language processor API
LANGUAGE_PROCESSOR_API = 'https://us-central1-graph-intelligence.cloudfunctions.net/language-processor-tech'

# Timeout between inserting articles in seconds
TIMEOUT = 3

# Maximum articles to insert
MAX_ARTICLES = 3330

# Specifies the cluster of articles in the knowledge graph
DB_IDS = {
    'cluster_id': 1,
    'user_id': "1"
}
