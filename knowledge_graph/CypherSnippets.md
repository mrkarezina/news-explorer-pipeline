# Useful Cypher Snippets

## Louvain Cluster Analysis
```cypher
CALL algo.louvain('MATCH (p:Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}}) RETURN id(p) as id',
                    'MATCH (p1:Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}})-[f:SIMILARITY {most_related:true}]-(p2:Article{cluster_id:{CLUSTER_ID}, user_id:{USER_ID}})  RETURN id(p1) as source, id(p2) as target, f.weight as weight',
                     {weightProperty:'weight', defaultValue:0.0, concurrency:4, graph:'cypher',write: true, writeProperty:"lpa"})
```

## Uniqueness constraint
```cypher
CREATE CONSTRAINT ON (a:Article) ASSERT a.title IS UNIQUE
```

## Delete relations
```cypher
MATCH (n:Article{cluster_id:"techcrunch"})-[r:SIMILARITY]-()
DELETE r
```

## Delete embedding property
```cypher
MATCH (n:Article{cluster_id:"cnn"})
DELETE n.embedding
```

## Delete Duplicate Relations
```cypher
MATCH (n:Article)-[:MENTIONS_CONCEPT]->(n2)<-[:MENTIONS_CONCEPT]-(n)
WITH n
OPTIONAL MATCH (n)-[r]-()
DELETE n, r
```

## Delete everything
```cypher
MATCH (n)
OPTIONAL MATCH (n)-[r]-()
DELETE n,r
```

## Delete some article nodes
```cypher
Match (n:Article) with n limit 140
Match (n)-[r]-()
Delete n, r
```

## Delete a cluster
```cypher
MATCH (n:Article{cluster_id:"CNN"})
OPTIONAL MATCH (n)-[r]-()
DELETE n,r
```