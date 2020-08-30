from knowledge_graph.config import GRAPH_URL

from py2neo import Graph


class GraphIndexer:
    """
    Used to create edges between nodes based on the overlap in their entities, doc2vec, and entity meta information
    The edges have values reflecting the similarity of the articles
    """

    def __init__(self, db_ids):

        self.graph = Graph(GRAPH_URL)

        self.relation_values = {
            "doc2vec": 0.25, "concept": 0.35, "entity": 0.40, "entity_category": 0.25}

        # Cosine similarity to add to prospective articles
        self.cosine_thresh = 0.4 * self.relation_values["doc2vec"]

        self.num_related = 3

        self.queries_dict = {

            # Create relation weight from cosine similarity of doc2vec vectors
            "CREATE_COSINE_SIMILARITY_RELATIONS": """
                                            MATCH (a: Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID, title:$TITLE})
                                            MATCH (b: Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID})
                                            WHERE NOT EXISTS((a)-[:SIMILARITY]->(b)) AND a <> b

                                            WITH a, b, apoc.algo.cosineSimilarity(a.embedding, b.embedding) as similarity

                                            CREATE (a)-[r:SIMILARITY]->(b)
                                            SET r.cosine_weight = $CONCEPT_WEIGHT*similarity
                                            """,

            # Used to match all articles to perform full analysis on
            "MATCH_PROSPECTIVE_ARTICLES": """
                                    MATCH (a: Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID, title:$TITLE})
                                    OPTIONAL MATCH (a)-[:RELATED_ENTITY]->(:Entity)<-[:RELATED_ENTITY]-(b1:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID})
                                    OPTIONAL MATCH (a)-[:MENTIONS_CONCEPT]->(:Concept)<-[:MENTIONS_CONCEPT]-(b2:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID})
                                    
                                    RETURN collect(distinct b1.title) + collect(distinct b2.title) as titles
                                    """,

            "MATCH_COSINE_ARTICLES": """
                                            MATCH (a: Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID, title:$TITLE})
                                            MATCH (a)-[r:SIMILARITY]->(b:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID})
                                            WHERE r.cosine_weight > $COSINE_THRESH
                                            WITH r.cosine_weight as weight, b
                                            ORDER BY weight DESC
                                            RETURN collect(distinct b.title) as titles
                                            """,

            "GET_MOST_SIMILAR": """
                                        MATCH(a:Article {title:$TITLE, cluster_id:$CLUSTER_ID, user_id:$USER_ID})
                                        MATCH (a)-[r1:SIMILARITY]->(related:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID})
                                        WHERE a <> related AND exists(r1.cosine_weight)
                                        RETURN related, r1.cosine_weight as weight
                                        ORDER BY weight DESC
                                        LIMIT $NUM_RELATED
                                        """,

            "SET_RELATED_FLAG": """
                                            MATCH (a:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID, title:$TITLE1})-[r_ab:SIMILARITY]->(b:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID, title:$TITLE2})
                                            SET r_ab.most_related = true
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
            q = q.replace("$CLUSTER_ID", "\"{0}\"".format(cluster_id))
            q = q.replace("$USER_ID", "\"{0}\"".format(user_id))

            self.queries_dict[query] = q

    def create_relations(self, title):

        self.graph.run(self.queries_dict["CREATE_COSINE_SIMILARITY_RELATIONS"], TITLE=title,
                       CONCEPT_WEIGHT=self.relation_values["doc2vec"])
        self.create_most_similar_article_property(title)

    def create_most_similar_article_property(self, title):
        """
        Sets a flag for the top n relations for an article
        :return:
        """

        most_sim = list(
            self.graph.run(self.queries_dict["GET_MOST_SIMILAR"], TITLE=title, NUM_RELATED=self.num_related))
        try:
            for sim in most_sim:
                most_similar = sim["related"]["title"]
                print("TITLE MOST SIM {0}".format(most_similar))
                self.graph.run(
                    self.queries_dict["SET_RELATED_FLAG"], TITLE1=title, TITLE2=most_similar)

        except IndexError:
            print("No related Articles")
