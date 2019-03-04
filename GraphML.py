
from py2neo import Graph

# TODO: Make import script for configuring the database, including title index


graph_url = "http://neo4j:Trebinje66@35.192.221.56:7474/db/data/"
# graph_url = "http://neo4j:Trebinje66@localhost:7474/db/data/"

"""
Importing exporting databases using GraphML: https://medium.com/@niazangels/export-and-import-your-neo4j-graph-easily-with-apoc-4ea614f7cbdf

Make sure to set the node lables before export so you can set them again on import

// Export entire database
CALL apoc.export.graphml.all('/Users/milanarezina/Desktop/complete-graph.graphml', {useTypes:true, storeNodeIds:true})

Can import the graph from a google drive URL:
-Make sure you use a download link
https://docs.google.com/uc?export=download&id=[Your id]
"""


# Call to set the label properties:
"""
MATCH (n)
SET n.node_label = labels(n)
"""

export_qeury = """
CALL apoc.export.graphml.all('/Users/milanarezina/Desktop/complete-graph.graphml', {useTypes:true, storeNodeIds:true})
"""

load_query = """
CALL apoc.import.graphml('https://docs.google.com/uc?export=download&id=1LGyA-nzdOqUiZBwQv870rlmtfmMo3SCm', {batchSize: 10000, useTypes:true, storeNodeIds:true})
"""

# To set relations
#TODO: make script that can be run at once, run each of these independently, or memory error
"""
MATCH (n)
WHERE n.node_label=['Article']
SET n :Article

MATCH (n)
WHERE n.node_label=['Category']
SET n :Category

MATCH (n)
WHERE n.node_label=['Concept']
SET n :Concept

MATCH (n)
WHERE n.node_label=['Entity']
SET n :Entity

MATCH (n)
WHERE n.node_label=['Topic']
SET n :Topic
"""


graph = Graph(graph_url)

print('Loading...')
graph.run(load_query)



