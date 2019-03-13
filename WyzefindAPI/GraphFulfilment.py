import json
from py2neo import Graph

# graph_url = "http://neo4j:Trebinje66@localhost:7474/db/data/"
graph_url = "http://neo4j:Trebinje66@35.202.226.197:7474/db/data/"


class GraphFulfilment:
    """
    Used to:
    -Find most related article from document embedding
    -Get the most similar articles by document embedding
    -Get the entities, concepts associated with a document
    """

    def __init__(self, db_ids):
        self.graph = Graph(graph_url)

        # Minimum entities mentioned in summary
        self.minimum_entities = 0

        # Creates relation between entity and its categories
        self.queries_dict = {

            "GET_MOST_RELATED_BY_EMBEDDING": """
                MATCH (a: Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}})
                WITH a, apoc.algo.cosineSimilarity(a.embedding, {TARGET_EMBEDDING}) as similarity
                
                RETURN a.title as title
                ORDER BY similarity DESC
                LIMIT 5
                """,

            "GET_ARTICLE_DATA": """
                MATCH (a:Article{title:{TITLE}})
                RETURN a
                """,

            "GET_TITLE_FROM_URL": """
                        MATCH (a:Article{url:{URL}})
                        RETURN a.title as title
                        """,

            "GET_CONCEPTS": """
                MATCH (a:Article{title:{TITLE}})
    
                MATCH (a)-[r:MENTIONS_CONCEPT]->(concept)
                RETURN concept
                ORDER BY r.score DESC
                LIMIT 3
                """,

            "GET_ENTITIES": """
                MATCH (a:Article{title:{TITLE}})

                MATCH (a)-[r:RELATED_ENTITY]->(related_entity:Entity)
                RETURN related_entity
                ORDER BY r.score DESC
                LIMIT 3
                """,

            "GET_MOST_RELATED": """
                MATCH (a: Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE}})
                MATCH (a)-[r:SIMILARITY]->(b)
                WHERE r.most_related = true
                
                RETURN b.title as title
                """,

        }

        self.format_queries(db_ids)

    def format_queries(self, db_ids):
        """
        Formats the neo4j queries to use the correct cluster/user id on insertion
        :param db_ids:
        :return:
        """

        cluster_id = db_ids["cluster_id"]
        user_id = db_ids["user_id"]

        # Replace for actual ids
        for query in self.queries_dict.keys():
            q = self.queries_dict[query]
            q = q.replace("{CLUSTER_ID}", "\"{0}\"".format(cluster_id))
            q = q.replace("{USER_ID}", "\"{0}\"".format(user_id))

            self.queries_dict[query] = q

    def get_article_data(self, title):
        """
        Gets data on title
        :param title:
        :return:
        """

        article = list(self.graph.run(self.queries_dict["GET_ARTICLE_DATA"],
                                      TITLE=title))[0][0]

        article_data = {
            'title': article['title'],
            'summary': article['summary'],
            'url': article['url'],
            'img_url': article['img_url'],
            'date': article['date'],
            'entities': [],
            'concepts': [],
        }

        # For finding entities
        entities = list(self.graph.run(self.queries_dict["GET_ENTITIES"],
                                       TITLE=title))
        for entity in entities:
            entity = list(entity)[0]
            article_data['entities'].append({
                'label': entity['label'],
            })

        # For finding common concepts
        concepts = list(self.graph.run(self.queries_dict["GET_CONCEPTS"],
                                       TITLE=title))
        for concept in concepts:
            concept = list(concept)[0]
            article_data['concepts'].append({
                'label': concept['label'],
            })

        return article_data

    def get_most_related_articles(self, title):
        """
        Gets the most related titles to a title
        """

        # For finding common concepts
        most_related = list(self.graph.run(self.queries_dict["GET_MOST_RELATED"],
                                           TITLE=title))

        articles = []
        for related in most_related:
            articles.append(related['title'])

        return articles

    def get_most_related_by_embedding(self, embedding):
        """
        Gets most related titles to embedding
        :param embedding:
        :return:
        """

        # For finding common concepts
        most_related = list(self.graph.run(self.queries_dict["GET_MOST_RELATED_BY_EMBEDDING"],
                                           TARGET_EMBEDDING=embedding))

        articles = []
        for related in most_related:
            articles.append(related['title'])

        return articles

    def get_title_from_url(self, url):
        """
        Gets title from url
        :param url:
        :return:
        """

        # For finding common concepts
        title = list(self.graph.run(self.queries_dict["GET_TITLE_FROM_URL"],
                                    URL=url))[0]['title']

        return title


# if __name__ == "__main__":
#     db_ids = {
#         'cluster_id': 1,
#         'user_id': 1
#     }
#
#     s = GraphFulfilment(db_ids)
#     print(s.get_most_related_articles('Facing opposition, Amazon reconsiders N.Y. headquarters site, two officials say'))
#
#     s = s.get_article_data('Facing opposition, Amazon reconsiders N.Y. headquarters site, two officials say')
#     print(s)

    # s.run_graph_analysis()

    # s.test_similarity()
