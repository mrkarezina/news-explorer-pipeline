import py2neo
from py2neo import Graph

from knowledge_graph.config import GRAPH_URL


class ArticleInserter:
    """
    Used to insert articles in KG
    """

    def __init__(self, db_ids):

        self.graph = Graph(GRAPH_URL)

        # Minimum entities mentioned in summary
        self.minimum_entities = 0

        # Creates relation between entity and its categories
        self.queries_dict = {
            "CREATE_ARTICLE": """
                        MERGE(article:Article {cluster_id:$CLUSTER_ID, user_id:$USER_ID, title:$TITLE, summary:$TEXT, url:$URL, img_url:$IMG_URL, date:$DATE, embedding:$EMBEDDING})
                        """
        }

        self.CREATE_UNIQUE_CONSTRAINT = """
        CREATE CONSTRAINT ON (a:Article) ASSERT a.title IS UNIQUE
        """

        try:
            self.create_unique_title_constraint()
        except py2neo.database.work.ClientError:
            print("Neo4j unique title contrainst already exists, skipping.")

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

    def create_unique_title_constraint(self):
        """
        Ensures that no two same titles inserted in graph. Ex: nytimes and huffington might have same stuff
        :return:
        """

        self.graph.run(self.CREATE_UNIQUE_CONSTRAINT)

    def db_insert(self, article_dict):
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
