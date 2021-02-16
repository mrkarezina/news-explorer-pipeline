# Knowledge Graph Pipeline

These scripts are used to download, preprocess, and insert articles into the knowledge graph. The [language processor endpoint](https://github.com/mrkarezina/graph-recommendation-api) is used to process the raw text and generate the Doc2Vec embeddings.

## Usage
1. Using `utils/save_article_links.py` create a text file `knowledge_graph/articles.txt` containing all of the urls of the articles to be inserted into the knowledge graph with urls separated by newline.

2. Populate a variable in `knowledge_graph/secrets.py` containing your graph DB connection string. Example
```
NEO4J_CONNECTION_STRING = http://neo4j:PASSWORD@35.111.11.111:7474/db/data/
```

3. Similarly populate `IBM_WATSON_API_KEY` which is the api key used for the IBM Watson NLU service. Adjust the config in `knowledge_graph/config.py` including the timeout between inserted articles and number of articles to insert.

4. Run `knowledge_graph/main.py` to process the articles and insert the extracted data into
the knowledge graph.


5. Run `knowledge_graph/similarity_weights_test.py` to analyze the relations between the articles creating the weighted graph. Sample relations will be outputted when the relations are tested.

The neo4j database should now contain the knowledge graph with the nodes representing the analyzed articles as well as nodes for all of their meta data, ie entities, topics, and concepts mentioned.

The edges between the articles will have a similarity weight based on various signals such as common entities and cosine similarity between embeddings. The edges between articles and their respective meta data will contain information such as sentiment scores
towards entities as well as relevance scores for topics and entities.


# Utility Scripts

## `graph_ml.py`
Used for importing an existing database exported in graph ML format


## `load_rss_feeds.py`
Loads RSS feeds into the database where a cron job keeps the latest articles cached. Used by the [article_curation](https://github.com/mrkarezina/content-recommendation-api) api.


## `sitemap_utility.py`
Scrapes and downloads all of the articles from RSS feeds. Useful in creating a corpora to train a Doc2Vec model.

## `export_neo4j_visjs.py`
Formats and exports the knowledge graph in the Neo4j database in a format compatible with the [vis.js](https://visjs.org/) library. Used in the [web app](https://graphs.markoarezina.com/).


