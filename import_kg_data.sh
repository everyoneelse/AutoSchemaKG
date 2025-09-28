#!/bin/bash
# 知识图谱数据导入脚本

set -e

# 配置参数
NEO4J_HOME="/workspace/neo4j-server-dulce"
NEO4J_URI="bolt://localhost:8612"
NEO4J_USER="neo4j"
NEO4J_PASS="admin2024"
DATASET_NAME="Dulce"  # 可以修改为其他数据集名称

echo "🚀 开始导入知识图谱数据..."
echo "📊 数据集: $DATASET_NAME"

# 检查Neo4j是否运行
if ! ${NEO4J_HOME}/bin/cypher-shell -u $NEO4J_USER -p $NEO4J_PASS -a $NEO4J_URI "RETURN 1" >/dev/null 2>&1; then
    echo "❌ Neo4j未运行或连接失败，请先启动Neo4j服务"
    echo "运行: cd /workspace/neo4j_scripts && ./start_neo4j_demo.sh"
    exit 1
fi

echo "✅ Neo4j连接成功"

# 检查数据文件是否存在
DATA_DIR="${NEO4J_HOME}/import/${DATASET_NAME}"
if [ ! -d "$DATA_DIR" ]; then
    echo "❌ 数据目录不存在: $DATA_DIR"
    echo "请确保已运行知识图谱生成流程并复制数据到import目录"
    exit 1
fi

echo "📁 数据目录: $DATA_DIR"
echo "📋 可用数据文件:"
find $DATA_DIR -name "*.csv" | head -10

# 创建Cypher导入脚本
cat > /tmp/import_kg.cypher << EOF
// 知识图谱数据导入Cypher脚本
// 数据集: $DATASET_NAME

// 1. 清空现有数据 (可选，谨慎使用)
// MATCH (n) DETACH DELETE n;

// 2. 创建约束和索引
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT text_id_unique IF NOT EXISTS FOR (t:Text) REQUIRE t.id IS UNIQUE;

// 3. 导入文本节点
LOAD CSV WITH HEADERS FROM 'file:///${DATASET_NAME}/triples_csv/text_nodes_${DATASET_NAME}_from_json.csv' AS row
CREATE (t:Text {
    id: row.\`name:ID\`,
    content: row.content,
    metadata: row.metadata
});

// 4. 导入三元组节点 (实体、事件)
LOAD CSV WITH HEADERS FROM 'file:///${DATASET_NAME}/triples_csv/triple_nodes_${DATASET_NAME}_from_json_without_emb.csv' AS row
CREATE (n:Entity {
    id: row.\`name:ID\`,
    name: row.\`name:ID\`,
    type: row.type,
    concepts: row.concepts,
    synsets: row.synsets
});

// 5. 导入概念节点
LOAD CSV WITH HEADERS FROM 'file:///${DATASET_NAME}/concept_csv/concept_nodes_${DATASET_NAME}_from_json_with_concept.csv' AS row
CREATE (c:Concept {
    id: row.\`concept_id:ID\`,
    name: row.name
});

// 6. 导入三元组关系
LOAD CSV WITH HEADERS FROM 'file:///${DATASET_NAME}/concept_csv/triple_edges_${DATASET_NAME}_from_json_with_concept.csv' AS row
MATCH (a:Entity {id: row.\`:START_ID\`})
MATCH (b:Entity {id: row.\`:END_ID\`})
CREATE (a)-[r:RELATES {
    relation: row.relation,
    concepts: row.concepts,
    synsets: row.synsets
}]->(b);

// 7. 导入概念关系
LOAD CSV WITH HEADERS FROM 'file:///${DATASET_NAME}/concept_csv/concept_edges_${DATASET_NAME}_from_json_with_concept.csv' AS row
MATCH (e:Entity {id: row.\`:START_ID\`})
MATCH (c:Concept {id: row.\`:END_ID\`})
CREATE (e)-[:HAS_CONCEPT]->(c);

// 8. 导入文本关系
LOAD CSV WITH HEADERS FROM 'file:///${DATASET_NAME}/triples_csv/text_edges_${DATASET_NAME}_from_json.csv' AS row
MATCH (t:Text {id: row.\`:START_ID\`})
MATCH (e:Entity {id: row.\`:END_ID\`})
CREATE (t)-[:CONTAINS]->(e);

// 9. 创建性能索引
CREATE INDEX entity_name_index IF NOT EXISTS FOR (n:Entity) ON (n.name);
CREATE INDEX concept_name_index IF NOT EXISTS FOR (c:Concept) ON (c.name);
CREATE INDEX entity_type_index IF NOT EXISTS FOR (n:Entity) ON (n.type);

// 10. 显示导入统计
MATCH (e:Entity) WITH count(e) as entity_count
MATCH (c:Concept) WITH entity_count, count(c) as concept_count
MATCH (t:Text) WITH entity_count, concept_count, count(t) as text_count
MATCH ()-[r]->() WITH entity_count, concept_count, text_count, count(r) as relation_count
RETURN 
    entity_count as \`实体数量\`,
    concept_count as \`概念数量\`,
    text_count as \`文本数量\`,
    relation_count as \`关系数量\`;
EOF

echo "📝 生成Cypher导入脚本: /tmp/import_kg.cypher"

# 执行导入
echo "⚡ 开始执行数据导入..."
${NEO4J_HOME}/bin/cypher-shell -u $NEO4J_USER -p $NEO4J_PASS -a $NEO4J_URI -f /tmp/import_kg.cypher

if [ $? -eq 0 ]; then
    echo "🎉 数据导入成功完成！"
    echo ""
    echo "📊 现在您可以:"
    echo "  1. 访问Neo4j Browser: http://localhost:7474"
    echo "  2. 使用用户名: $NEO4J_USER, 密码: $NEO4J_PASS"
    echo "  3. 运行查询来探索知识图谱"
    echo ""
    echo "🔍 示例查询:"
    echo "  MATCH (n) RETURN labels(n), count(n);"
    echo "  MATCH (e:Entity)-[:HAS_CONCEPT]->(c:Concept) RETURN e.name, c.name LIMIT 10;"
else
    echo "❌ 数据导入失败，请检查错误信息"
    exit 1
fi