#!/bin/bash
# Docker Neo4j 环境设置和数据导入脚本

set -e

# 配置参数
CONTAINER_NAME="neo4j"  # 您的Neo4j容器名称，请根据实际情况修改
NEO4J_USER="neo4j"
NEO4J_PASS="neo4j"      # 请根据实际密码修改
NEO4J_URI="bolt://localhost:7687"  # Docker默认端口
DATASET_NAME="Dulce"    # 数据集名称

echo "🐳 Docker Neo4j 环境设置和数据导入"
echo "======================================"
echo "📊 容器名称: $CONTAINER_NAME"
echo "📊 数据集: $DATASET_NAME"

# 检查Docker容器是否运行
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo "❌ Neo4j容器 '$CONTAINER_NAME' 未运行"
    echo "请先启动Neo4j容器，例如："
    echo "docker run -d --name neo4j \\"
    echo "  -p 7474:7474 -p 7687:7687 \\"
    echo "  -e NEO4J_AUTH=neo4j/your_password \\"
    echo "  -v \$PWD/neo4j/data:/data \\"
    echo "  -v \$PWD/neo4j/logs:/logs \\"
    echo "  -v \$PWD/neo4j/import:/var/lib/neo4j/import \\"
    echo "  neo4j:latest"
    exit 1
fi

echo "✅ Neo4j容器正在运行"

# 检查连接
echo "🔍 测试Neo4j连接..."
if ! docker exec $CONTAINER_NAME cypher-shell -u $NEO4J_USER -p $NEO4J_PASS "RETURN 1 as test" >/dev/null 2>&1; then
    echo "❌ 无法连接到Neo4j，请检查用户名和密码"
    echo "当前使用: 用户名=$NEO4J_USER, 密码=$NEO4J_PASS"
    exit 1
fi

echo "✅ Neo4j连接成功"

# 复制数据文件到容器的import目录
echo "📁 复制数据文件到容器..."
if [ -d "/workspace/import/$DATASET_NAME" ]; then
    docker cp /workspace/import/$DATASET_NAME $CONTAINER_NAME:/var/lib/neo4j/import/
    echo "✅ 数据文件复制完成"
else
    echo "❌ 数据目录不存在: /workspace/import/$DATASET_NAME"
    echo "请先运行知识图谱生成流程"
    exit 1
fi

# 创建n10s约束和配置
echo "⚙️ 创建n10s约束和RDF配置..."
docker exec $CONTAINER_NAME cypher-shell -u $NEO4J_USER -p $NEO4J_PASS \
  "CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE;"

# 检查n10s插件是否可用
if docker exec $CONTAINER_NAME cypher-shell -u $NEO4J_USER -p $NEO4J_PASS \
  "CALL n10s.graphconfig.init({ handleMultival: 'OVERWRITE', handleVocabUris: 'SHORTEN', keepLangTag: false, handleRDFTypes: 'NODES' })" 2>/dev/null; then
    echo "✅ n10s RDF配置初始化成功"
else
    echo "⚠️ n10s插件不可用，跳过RDF配置（这不影响Atlas RAG数据导入）"
fi

echo "🎉 Docker Neo4j环境设置完成！"