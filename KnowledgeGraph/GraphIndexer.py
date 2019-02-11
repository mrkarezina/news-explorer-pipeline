from py2neo import Graph
import threading

graph_url = "http://neo4j:Trebinje66@localhost:7474/db/data/"


class GraphIndexer:
    """
    Used to create edges between nodes based on the overlap in their entities, doc2vec, and entity meta information
    The edges have values reflecting the similarity of the articles
    """

    def __init__(self, db_ids):

        self.graph = Graph(graph_url)

        self.relation_values = {"doc2vec": 0.25, "concept": 0.35, "entity": 0.40, "entity_category": 0.25}

        # Cosine similarity to add to prospective articles
        self.cosine_thresh = 0.4 * self.relation_values["doc2vec"]

        self.num_related = 3

        # TODO: Make use of the relevancy score
        # TODO: Delete unused properties
        """
        Queries to create weights:
        -Percentage overlap in Concepts, Entities, Entity Categories
        -Cosine similarity for Doc2Vec vector
        """

        self.queries_dict = {
            # Used set totals as property to prevent recomputing
            # If this is used article by article, when comuting bidirectional relation will fail silently if other article not having totals property
            "SET_PROPERTIES_COUNT": """
                                    MATCH (a: Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE}})
                                    WHERE not exists(a.total_entity)
                                    
                                    OPTIONAL MATCH (a)-[:RELATED_ENTITY]->(e:Entity)
                                    WHERE e.type <> 'Location'
                                    
                                    OPTIONAL MATCH (a)-[:RELATED_ENTITY]->(e)-[:IN_CATEGORY]->(e_cat:Category)
                                    OPTIONAL MATCH (a)-[:MENTIONS_CONCEPT]->(c:Concept)
                                    
                                    WITH a, count(distinct e) as ent, count(distinct e_cat) as cat, count(distinct c) as con
                                    SET a.total_entity = ent
                                    SET a.total_category = cat
                                    SET a.total_concept = con
                                    """,

            # Creates semantic weight based on common concepts, entities, and entity categories
            "CREATE_SEMANTIC_RELATIONS": """
                                                MATCH (a: Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE1}})
                                                MATCH (b: Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE2}})
                                                MATCH (a)-[r:SIMILARITY]->(b)
                                                WHERE NOT EXISTS (r.entity_weight)

                                                WITH a, b, r, SIZE((a)-[:RELATED_ENTITY]->(:Entity)<-[:RELATED_ENTITY]-(b)) as overlap_ent, SIZE((a)-[:MENTIONS_CONCEPT]->(:Concept)<-[:MENTIONS_CONCEPT]-(b)) as overlap_con

                                                OPTIONAL MATCH (a)-[:RELATED_ENTITY]->(e1:Entity)-[:IN_CATEGORY]->(e_cat:Category)<-[:IN_CATEGORY]-(e2:Entity)<-[:RELATED_ENTITY]-(b)
                                                WHERE e1 <> e2
                                                WITH a, r, overlap_ent, overlap_con, count(distinct e_cat) as overlap_cat

                                                SET r.semantic_weight = {ENTITY_WEIGHT}*overlap_ent/(a.total_entity + 1) + ({ENTITY_CATEGORY_WEIGHT}*overlap_cat)/(a.total_category+1) + ({CONCEPT_WEIGHT}*overlap_con)/(a.total_concept+1)
                                                """,

            # Create relation weight from cosine similarity of doc2vec vectors
            "CREATE_COSINE_SIMILARITY_RELATIONS": """
                                            MATCH (a: Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE}})
                                            MATCH (b: Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}})
                                            WHERE NOT EXISTS((a)-[:SIMILARITY]->(b))

                                            WITH a, b, apoc.algo.cosineSimilarity(a.embedding, b.embedding) as similarity

                                            CREATE (a)-[r:SIMILARITY]->(b)
                                            SET r.cosine_weight = {CONCEPT_WEIGHT}*similarity
                                            """,

            # Used to match all articles to perform full analysis on
            "MATCH_PROSPECTIVE_ARTICLES": """
                                    MATCH (a: Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE}})
                                    OPTIONAL MATCH (a)-[:RELATED_ENTITY]->(:Entity)<-[:RELATED_ENTITY]-(b1:Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}})
                                    OPTIONAL MATCH (a)-[:MENTIONS_CONCEPT]->(:Concept)<-[:MENTIONS_CONCEPT]-(b2:Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}})
                                    
                                    RETURN collect(distinct b1.title) + collect(distinct b2.title) as titles
                                    """,

            "MATCH_COSINE_ARTICLES": """
                                            MATCH (a: Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE}})
                                            MATCH (a)-[r:SIMILARITY]->(b:Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}})
                                            WHERE r.cosine_weight > {COSINE_THRESH}
                                            WITH r.cosine_weight as weight, b
                                            ORDER BY weight DESC
                                            RETURN collect(distinct b.title) as titles
                                            """,

            "GET_MOST_SIMILAR": """
                                        MATCH(a:Article {title:{TITLE}, cluster_id:{CLUSTER_ID}, user_id:{USER_ID}})
                                        MATCH (a)-[r1:SIMILARITY]->(related:Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}})
                                        WHERE a <> related AND exists(r1.semantic_weight)
                                        RETURN related, r1.semantic_weight as weight
                                        ORDER BY weight DESC
                                        LIMIT {NUM_RELATED}
                                        """,

            "SET_RELATED_FLAG": """
                                            MATCH (a:Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE1}})-[r_ab:SIMILARITY]->(b:Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE2}})
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
            q = q.replace("{CLUSTER_ID}", "\"{0}\"".format(cluster_id))
            q = q.replace("{USER_ID}", "\"{0}\"".format(user_id))

            self.queries_dict[query] = q

    def create_relations(self, title):

        self.graph.run(self.queries_dict["SET_PROPERTIES_COUNT"], TITLE=title)
        self.graph.run(self.queries_dict["CREATE_COSINE_SIMILARITY_RELATIONS"], TITLE=title,
                       CONCEPT_WEIGHT=self.relation_values["doc2vec"])

        self._set_sim_weight(title, bidirectional=True)
        self.create_most_similar_article_property(title)

    def _set_sim_weight(self, title, bidirectional=False):

        # Get prospective articles with matching, entity, category
        prospective_articles = list(self.graph.run(self.queries_dict["MATCH_PROSPECTIVE_ARTICLES"], TITLE=title))[0]['titles']
        cosine_prospective = list(self.graph.run(self.queries_dict["MATCH_COSINE_ARTICLES"], TITLE=title, COSINE_THRESH= self.cosine_thresh))[0]['titles']

        print(cosine_prospective)

        prospective_articles = set(cosine_prospective + prospective_articles)
        prospective_articles.remove(title)
        print("Prospective Articles: {0}".format(len(prospective_articles)))

        # Creates full relations between unique articles returned
        # Ensure that the other articles already have a weight property set, other wise bidirectional relationship will fail
        for j, title2 in enumerate(prospective_articles):

            self.graph.run(self.queries_dict["CREATE_SEMANTIC_RELATIONS"],
                           TITLE1=title,
                           TITLE2=title2,
                           CONCEPT_WEIGHT=self.relation_values["concept"],
                           ENTITY_WEIGHT=self.relation_values["entity"],
                           ENTITY_CATEGORY_WEIGHT=self.relation_values["entity_category"])

            if bidirectional:
                self.graph.run(self.queries_dict["CREATE_SEMANTIC_RELATIONS"],
                               TITLE1=title2,
                               TITLE2=title,
                               CONCEPT_WEIGHT=self.relation_values["concept"],
                               ENTITY_WEIGHT=self.relation_values["entity"],
                               ENTITY_CATEGORY_WEIGHT=self.relation_values["entity_category"])

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
                self.graph.run(self.queries_dict["SET_RELATED_FLAG"], TITLE1=title, TITLE2=most_similar)

        except IndexError:
            print("No related Articles")
