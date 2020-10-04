from knowledge_graph.graph_indexer import GraphIndexer
from knowledge_graph.config import DB_IDS


class SimilarityWeightsTest(GraphIndexer):
    """
    Used to create the relations (calls the insert for every article)
    Used to test the relations
    """

    def __init__(self, db_ids):

        GraphIndexer.__init__(self, db_ids)

        self.queries = {
            "GET_ALL": """MATCH (a: Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID}) RETURN a.title""",

            # Chose to use louvain bidirectional. Using OUT on LPA does does seem to improve quality of clusters.
            "LPA": """
                    CALL algo.louvain(
                    'MATCH (p:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID}) RETURN id(p) as id',
                    'MATCH (p1:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID})-[f:SIMILARITY {most_related:true}]-(p2:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID})  RETURN id(p1) as source, id(p2) as target, f.cosine_weight as weight',
                     {graph:'cypher', weightProperty:'cosine_weight', defaultValue:0.00001, write: true, writeProperty:'lpa', direction: 'OUTGOING'})
                    """,

            "PAGE_RANK": """
            CALL algo.pageRank(
            'MATCH (p:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID}) RETURN id(p) as id',
                    'MATCH (p1:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID})-[f:SIMILARITY {most_related:true}]-(p2:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID})  RETURN id(p1) as source, id(p2) as target, f.cosine_weight as weight',
                    {graph:'cypher', weightProperty:'cosine_weight', iterations:5, write: true, writeProperty:"page_rank"}
            )
            """,
            "TEST_MOST_SIMILAR": """
            MATCH(a:Article {title:{TITLE}, cluster_id:$CLUSTER_ID, user_id:$USER_ID})
            USING INDEX a:Article(title)
            WITH a
            MATCH (a)-[r1:SIMILARITY]->(related:Article{cluster_id:$CLUSTER_ID, user_id:$USER_ID})
            WHERE a <> related AND exists(r1.cosine_weight)
            RETURN related, r1.cosine_weight as weight
            ORDER BY weight DESC
            LIMIT $NUM_RELATED
            """

        }

        self._format_queries(db_ids)

    def _format_queries(self, db_ids):
        """
        Formats the neo4j queries to use the correct cluster/user id on insertion
        :param db_ids:
        :return:
        """

        cluster_id = db_ids["cluster_id"]
        user_id = db_ids["user_id"]

        # Replace for actual ids
        for query in self.queries.keys():
            q = self.queries[query]
            q = q.replace("$CLUSTER_ID", "\"{0}\"".format(cluster_id))
            q = q.replace("$USER_ID", "\"{0}\"".format(user_id))

            self.queries[query] = q

    def run_graph_analysis(self):
        """
        Runs both LPA for labeling clusters and Page rank for setting importance of nodes
        :return:
        """

        self.graph.run(self.queries["LPA"])
        self.graph.run(self.queries["PAGE_RANK"])

    def create(self):
        """
        Creates relations in the DB, creates relations for every article node
        :return:
        """

        articles_list = list(self.graph.run(self.queries["GET_ALL"]))

        all_titles = []
        for article in articles_list:
            title = article["a.title"]
            all_titles.append(title)

        for title in all_titles:
            print("Created: " + title)
            self.create_relations(title)

    def test_similarity(self):
        articles_list = list(self.graph.run(self.queries["GET_ALL"]))

        all_titles = []
        for article in articles_list:
            title = article["a.title"]
            all_titles.append(title)

        for title in all_titles:
            print(title)
            most_sim = list(
                self.graph.run(self.queries_dict["GET_MOST_SIMILAR"], TITLE=title, NUM_RELATED=self.num_related))
            try:
                for sim in most_sim:
                    most_similar = sim["related"]["title"]
                    print("TITLE MOST SIM {0}".format(most_similar))
                    self.graph.run(self.queries_dict["SET_RELATED_FLAG"], TITLE1=title, TITLE2=most_similar)

            except IndexError:
                print("No related Articles")

            print("\n\n")


if __name__ == "__main__":
    s = SimilarityWeightsTest(DB_IDS)
    # Creates the weighted graph
    # s.create()
    # Runs page rank and community detection algorithms on the graph
    s.run_graph_analysis()

    # Output the result of running the similarity analysis
    # showing the top related articles
    # s.test_similarity()
