from py2neo import Graph

# graph_url = "http://neo4j:Trebinje66@35.202.226.197:7474/db/data/"
graph_url = "http://neo4j:Trebinje66@localhost:7474/db/data/"

class ArticleInserter:
    """
    Used to insert articles in KG
    """

    def __init__(self, db_ids):

        self.graph = Graph(graph_url)

        # Minimum entities mentioned in summary
        self.minimum_entities = 0

        # Creates relation between entity and its categories
        self.queries_dict = {

            "CREATE_ARTICLE": """
                        MERGE(article:Article {cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE}, summary:{TEXT}, url:{URL}, img_url:{IMG_URL}, date:{DATE}, embedding:{EMBEDDING}})
                        """,

            "RELATED_ENTITY_INSERTION_QUERY": """
                MATCH(article:Article {cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE}})

                MERGE (entity:Entity {label: {ENTITY_LABEL}})

                MERGE (article)-[r:RELATED_ENTITY]->(entity)
                SET r.type = {ENTITY_TYPE}
                SET r.count = {COUNT}
                SET r.score = {RELEVANCE}
                SET r.sentiment = {SENTIMENT}

                FOREACH (category IN {ENTITY_CATEGORIES} |
                    MERGE (cat:Category {label: category})
                    MERGE (entity)-[:IN_CATEGORY]->(cat)
                )
                """,

            "ARTICLE_TOPICS": """
            MATCH(article:Article {cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE}})
            
            MERGE (topic:Topic {label: {TOPIC_LABEL}})
            
            MERGE (article)-[r:HAS_TOPIC]->(topic)
            SET r.score = {RELEVANCE_SCORE}
            """

            ,

            "ARTICLE_CONCEPTS": """
            MATCH(article:Article {cluster_id:{CLUSTER_ID}, user_id:{USER_ID}, title:{TITLE}})
            
            MERGE (concept:Concept {label: {CONCEPT_LABEL}})
            
            MERGE (article)-[r:MENTIONS_CONCEPT]->(concept)
            SET r.score = {RELEVANCE_SCORE}
            """

        }

        self.CREATE_UNIQUE_CONSTRAINT = """
        CREATE CONSTRAINT ON (a:Article) ASSERT a.title IS UNIQUE
        """

        self.create_unique_title_constraint()

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

    def create_unique_title_constraint(self):
        """
        Ensures that no two same titles inserted in graph. Ex: nytimes and huffington might have same stuff
        :return:
        """

        self.graph.run(self.CREATE_UNIQUE_CONSTRAINT)

    def db_insert(self, article_dict, watson_entities, insert_topics):
        """
        Inserts the extracted information into the knowledge graph
        :param article_dict:
            Contains all required article properties
        :param watson_entities:
            Dict from watson NLU API
        :return:
        """

        self.graph.run(self.queries_dict["CREATE_ARTICLE"], TITLE=article_dict['title'],
                       TEXT=article_dict['summary'], URL=article_dict['url'],
                       IMG_URL=article_dict['img_url'], DATE=article_dict['date'],
                       EMBEDDING=article_dict['embedding'])

        for entity in watson_entities['entities']:

            if entity['type'] != 'Quantity':
                try:
                    entity_categories = entity['disambiguation']['subtype']
                except KeyError:
                    entity_categories = []

                self.graph.run(self.queries_dict["RELATED_ENTITY_INSERTION_QUERY"],
                               TITLE=article_dict['title'],
                               ENTITY_LABEL=entity['text'], ENTITY_TYPE=entity['type'], COUNT=entity['count'],
                               SENTIMENT=entity['sentiment']['label'],
                               RELEVANCE=entity['relevance'],
                               ENTITY_CATEGORIES=entity_categories)

            for category in watson_entities['concepts']:
                self.graph.run(self.queries_dict["ARTICLE_CONCEPTS"],
                               TITLE=article_dict['title'],
                               CONCEPT_LABEL=category['text'], RELEVANCE_SCORE=category['relevance'])

            if insert_topics:
                for topic in watson_entities['categories']:
                    self.graph.run(self.queries_dict["ARTICLE_TOPICS"],
                                   TITLE=article_dict['title'],
                                   TOPIC_LABEL=topic['label'], RELEVANCE_SCORE=topic['score'])
