// 导入知识图谱数据到Neo4j的Cypher脚本

// 1. 清空现有数据 (可选)
MATCH (n) DETACH DELETE n;

// 2. 导入文本节点
LOAD CSV WITH HEADERS FROM 'file:///Dulce/triples_csv/text_nodes_Dulce_from_json.csv' AS row
CREATE (t:Text {
    id: row.`name:ID`,
    content: row.content,
    metadata: row.metadata
});

// 3. 导入三元组节点 (实体、事件)
LOAD CSV WITH HEADERS FROM 'file:///Dulce/triples_csv/triple_nodes_Dulce_from_json_without_emb.csv' AS row
CREATE (n:Entity {
    id: row.`name:ID`,
    name: row.`name:ID`,
    type: row.type,
    concepts: row.concepts,
    synsets: row.synsets
});

// 4. 导入概念节点
LOAD CSV WITH HEADERS FROM 'file:///Dulce/concept_csv/concept_nodes_Dulce_from_json_with_concept.csv' AS row
CREATE (c:Concept {
    id: row.`concept_id:ID`,
    name: row.name
});

// 5. 导入三元组关系
LOAD CSV WITH HEADERS FROM 'file:///Dulce/concept_csv/triple_edges_Dulce_from_json_with_concept.csv' AS row
MATCH (a:Entity {id: row.`:START_ID`})
MATCH (b:Entity {id: row.`:END_ID`})
CREATE (a)-[r:RELATES {
    relation: row.relation,
    concepts: row.concepts,
    synsets: row.synsets
}]->(b);

// 6. 导入概念关系
LOAD CSV WITH HEADERS FROM 'file:///Dulce/concept_csv/concept_edges_Dulce_from_json_with_concept.csv' AS row
MATCH (e:Entity {id: row.`:START_ID`})
MATCH (c:Concept {id: row.`:END_ID`})
CREATE (e)-[:HAS_CONCEPT]->(c);

// 7. 导入文本关系
LOAD CSV WITH HEADERS FROM 'file:///Dulce/triples_csv/text_edges_Dulce_from_json.csv' AS row
MATCH (t:Text {id: row.`:START_ID`})
MATCH (e:Entity {id: row.`:END_ID`})
CREATE (t)-[:CONTAINS]->(e);

// 8. 创建索引以提升查询性能
CREATE INDEX entity_id_index FOR (n:Entity) ON (n.id);
CREATE INDEX concept_name_index FOR (c:Concept) ON (c.name);
CREATE INDEX text_id_index FOR (t:Text) ON (t.id);