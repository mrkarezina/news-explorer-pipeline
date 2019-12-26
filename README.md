# Graph Visualisation Scripts

These scripts are used to preprocess, analyze and insert articles into the knowledge graph.
The [language_processor_api](https://github.com/mrkarezina/content-recommendation-api) is used
to process the raw test and generate the Doc2Vec embeddings.

## Usage
Create a text file `knowledge_graph/articles.txt` containing all of the urls of the articles to be inserted into the 
knowledge graph with urls separated by newline.


Create a variable in `knowledge_graph/secrets.py` containing your graph DB connection string.


Example `NEO4J_CONNECTION_STRING = http://neo4j:PASSWORD@35.111.11.111:7474/db/data/`


Also create a variable `IBM_WATSON_API_KEY = ...` which is the api key used for the IBM Watson NLU service. Enter the config in `knowledge_graph/config.py` including the
timeout between inserted articles and number of articles to insert.


Run `knowledge_graph/main.py` to process the articles and insert the extracted data into
the knowledge graph.


Run `knowledge_graph/SimilarityWeightsTest.py` to analyze the relations between the articles
creating the weighted graph. Sample relations will be outputted when the relations are tested.

The neo4j database should now contain the knowledge graph with the nodes representing the analyzed articles
as well as nodes for all of their meta data, ie entities, topics, and concepts mentioned. The edges between the articles
will have a similarity weight based on various signals such as common entities and cosine similarity between embeddings.
The edges between articles and their respective meta data will contain information such as sentiment scores
towards entities as well as relevance scores for topics and entities.



