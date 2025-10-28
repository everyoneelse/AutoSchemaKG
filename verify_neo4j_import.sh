#!/bin/bash
# Neo4j数据导入验证脚本

NEO4J_HOME="/workspace/neo4j-server-dulce"
NEO4J_URI="bolt://localhost:8612"
NEO4J_USER="neo4j"
NEO4J_PASS="admin2024"

echo "🔍 验证Neo4j知识图谱数据导入"
echo "================================"

# 检查连接
if ! ${NEO4J_HOME}/bin/cypher-shell -u $NEO4J_USER -p $NEO4J_PASS -a $NEO4J_URI "RETURN 1 as test" >/dev/null 2>&1; then
    echo "❌ 无法连接到Neo4j，请确保服务正在运行"
    exit 1
fi

echo "✅ Neo4j连接正常"
echo ""

# 基本统计查询
echo "📊 数据统计:"
${NEO4J_HOME}/bin/cypher-shell -u $NEO4J_USER -p $NEO4J_PASS -a $NEO4J_URI \
"MATCH (n) RETURN labels(n)[0] as NodeType, count(n) as Count ORDER BY Count DESC;"

echo ""
echo "🔗 关系统计:"
${NEO4J_HOME}/bin/cypher-shell -u $NEO4J_USER -p $NEO4J_PASS -a $NEO4J_URI \
"MATCH ()-[r]->() RETURN type(r) as RelationType, count(r) as Count ORDER BY Count DESC;"

echo ""
echo "👤 实体示例 (前5个):"
${NEO4J_HOME}/bin/cypher-shell -u $NEO4J_USER -p $NEO4J_PASS -a $NEO4J_URI \
"MATCH (e:Entity) RETURN e.name, e.type LIMIT 5;"

echo ""
echo "💡 概念示例 (前5个):"
${NEO4J_HOME}/bin/cypher-shell -u $NEO4J_USER -p $NEO4J_PASS -a $NEO4J_URI \
"MATCH (c:Concept) RETURN c.name LIMIT 5;"

echo ""
echo "🔍 实体-概念关系示例:"
${NEO4J_HOME}/bin/cypher-shell -u $NEO4J_USER -p $NEO4J_PASS -a $NEO4J_URI \
"MATCH (e:Entity)-[:HAS_CONCEPT]->(c:Concept) RETURN e.name, c.name LIMIT 5;"

echo ""
echo "✅ 验证完成！"
echo ""
echo "🌐 现在可以访问 Neo4j Browser:"
echo "   http://localhost:7474"
echo "   用户名: neo4j, 密码: admin2024"