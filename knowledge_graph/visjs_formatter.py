from flask import Flask, request
import json
from py2neo import Graph

graph_url = "http://neo4j:password@localhost:7474/db/data/"


class GraphViz:
    """
    Used to format the queried subgraph for use in Vis.js
    """

    def __init__(self, db_ids):

        self.queries = {

            # Can adjust the number of nodes to query from the subgraph.
            "QUERY_SUBGRAPH": """
                                MATCH (a:Article{cluster_id:$CLUSTER_ID, user_id: $USER_ID})
                                WITH a 
                                ORDER BY a.page_rank DESC
                                LIMIT 100
                                MATCH (a)-[r:SIMILARITY{most_related:true}]->(b:Article{cluster_id: $CLUSTER_ID, user_id: $USER_ID}) 
                                WHERE a <> b
                                RETURN r.cosine_weight, a, b

                                """
        }

        self.graph = Graph(graph_url)

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

    def format_graph_data(self):
        json_subgraph = json.loads(json.dumps(self.graph.run(self.queries["QUERY_SUBGRAPH"]).data()))
        # print("sub", json_subgraph)

        graph_json_formated = {
            "nodes": [],
            "edges": []

        }
        unique_nodes = []

        for rel in json_subgraph:
            items = [rel["a"], rel["b"]]

            unique_nodes.extend(items)

            graph_json_formated["edges"].append(
                {
                    "from": items[0]["title"],
                    "to": items[1]["title"],
                    "value": rel["r.cosine_weight"]
                }
            )

        # Get unique
        unique_nodes = list({v['title']: v for v in unique_nodes}.values())

        for unique_art in unique_nodes:
            graph_json_formated["nodes"].append({
                "id": unique_art["title"],
                "label": unique_art["title"],
                "group": unique_art["lpa"],
                "value": unique_art["page_rank"],
                "url": unique_art["url"],
                "img_url": unique_art["img_url"],
                "date": unique_art["date"]
            })

        # For response to be in same format as gCloud
        graph_json_formated = [graph_json_formated]

        return json.dumps(graph_json_formated)
        # print(json.dumps(graph_json_formated, indent=2))
