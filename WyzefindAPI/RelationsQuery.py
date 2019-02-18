import json
from py2neo import Graph

graph_url = "http://neo4j:Trebinje66@localhost:7474/db/data/"


class RelationsQuery:
    """
    Used to query relations between articles in the graph
    -Find / Explain relation between articles
    -Find me a path query
    """

    def __init__(self, db_ids):
        self.graph = Graph(graph_url)

        # Minimum entities mentioned in summary
        self.minimum_entities = 0

        # Creates relation between entity and its categories
        self.queries_dict = {

            # TODO: change to dijikstra, only have 2 'most related' and find shortest path, or try to remove duplicates
            # "i": """
            # MATCH (a:Article{title:{INITIAL}})
            # MATCH (b:Article{title : {TARGET}})
            # CALL apoc.algo.dijkstra(a, b, 'SIMILARITY', 'inverse_cosine_weight') YIELD path, weight
            # RETURN nodes(path)
            # """,

            "QUERY_ARTICLE_PATH": """
                MATCH (a:Article{title:{INITIAL}})
                MATCH (b:Article{title : {TARGET}})
                MATCH p=((a)-[q:SIMILARITY*..5{most_related: true}]->(b))
                WHERE NONE (n IN nodes(p) 
                WHERE size(filter(x IN nodes(p) 
                                  WHERE n = x))> 1)
                
                WITH p, relationships(p) AS r
                WITH p, reduce(acc=0, n in r | acc + n.cosine_weight) as path_length
                ORDER BY path_length DESC
                RETURN nodes(p)
                """,

            "EXPLAIN_COMMON_ENTITY_RELATION": """
                MATCH (a:Article{title:{INITIAL}})
                MATCH (b:Article{title : {TARGET}})
                
                MATCH (a)-[r:RELATED_ENTITY]->(entity)<-[:RELATED_ENTITY]-(b)
                RETURN entity
                ORDER BY r.score DESC
                """,

            "EXPLAIN_CONCEPT_RELATION": """
                MATCH (a:Article{title:{INITIAL}})
                MATCH (b:Article{title : {TARGET}})
    
                MATCH (a)-[r:MENTIONS_CONCEPT]->(concept)<-[:MENTIONS_CONCEPT]-(b)
                RETURN concept
                ORDER BY r.score DESC
                """,

            "EXPLAIN_RELATED_ENTITY_RELATION": """
                MATCH (a:Article{title:{INITIAL}})
                MATCH (b:Article{title : {TARGET}})

                MATCH (a)-[r:RELATED_ENTITY]->(:Entity)-[:IN_CATEGORY]->(category:Category)<-[:IN_CATEGORY]-(related_entity:Entity)<-[:RELATED_ENTITY]-(b)
                RETURN related_entity, category
                ORDER BY r.score DESC
                """

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

    def get_path(self, initial, target, length):
        """
        Gets a path between two titles
        :param initial:
        :param target:
        :return:
        """

        articles = list(self.graph.run(self.queries_dict["QUERY_ARTICLE_PATH"],
                                       INITIAL=initial,
                                       TARGET=target))

        articles = articles[0][0]

        for article in articles:
            print(article['title'])

    def explain_relation(self, initial, target):
        """

        :param initial:
        :param target:
        :return:
        """

        explanation = {
            'entities': [],
            'entity_categories': [],
            'concepts': []
        }

        # For finding common entities
        entities = list(self.graph.run(self.queries_dict["EXPLAIN_COMMON_ENTITY_RELATION"],
                                       INITIAL=initial,
                                       TARGET=target))
        for entity in entities:
            entity = list(entity)[0]
            explanation['entities'].append({
                'label': entity['label'],
                'type': entity['type']
            })

        # For finding entities related by meta categories
        entity_category = list(self.graph.run(self.queries_dict["EXPLAIN_RELATED_ENTITY_RELATION"],
                                              INITIAL=initial,
                                              TARGET=target))
        for category in entity_category:
            category = tuple(category)
            explanation['entity_categories'].append({
                'entity': category[0]['label'],
                'relation': category[1]['label']
            })

        # For finding common concepts
        concepts = list(self.graph.run(self.queries_dict["EXPLAIN_CONCEPT_RELATION"],
                                       INITIAL=initial,
                                       TARGET=target))
        for concept in concepts:
            concept = list(concept)[0]
            explanation['concepts'].append({
                'label': concept['label'],
            })

        a = json.dumps(explanation, indent=2)
        print(a)


if __name__ == "__main__":
    db_ids = {
        'cluster_id': 1,
        'user_id': 1
    }

    s = RelationsQuery(db_ids)
    s.explain_relation("Facebook acquires visual search startup GrokStyle",
                       "Data is not the new oil")

    s.get_path("AI Weekly: The AI research agenda for the next 20 years is being made now",
               "To support founders’ emotional health, VCs must change how they invest", 5)
    # s.run_graph_analysis()

    # s.test_similarity()
