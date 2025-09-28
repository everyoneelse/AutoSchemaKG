#!/bin/bash
# 一键Neo4j设置和数据导入脚本

set -e

echo "🎯 Atlas RAG Neo4j 一键设置和导入"
echo "=================================="

# 检查是否提供了数据集名称参数
DATASET_NAME=${1:-"Dulce"}
echo "📊 使用数据集: $DATASET_NAME"

# 步骤1: 安装和设置Neo4j
echo ""
echo "📋 步骤1: 设置Neo4j环境"
chmod +x /workspace/setup_neo4j_complete.sh
/workspace/setup_neo4j_complete.sh

# 步骤2: 启动Neo4j服务
echo ""
echo "📋 步骤2: 启动Neo4j服务"
cd /workspace/neo4j_scripts
chmod +x start_neo4j_demo.sh
./start_neo4j_demo.sh

# 等待Neo4j完全启动
echo "⏳ 等待Neo4j服务完全启动..."
sleep 15

# 步骤3: 导入数据
echo ""
echo "📋 步骤3: 导入知识图谱数据"
cd /workspace
chmod +x import_kg_data.sh

# 修改导入脚本中的数据集名称
sed -i "s/DATASET_NAME=\"Dulce\"/DATASET_NAME=\"$DATASET_NAME\"/" import_kg_data.sh

./import_kg_data.sh

echo ""
echo "🎉 完成！Neo4j知识图谱已准备就绪"
echo ""
echo "🌐 访问地址:"
echo "  Neo4j Browser: http://localhost:7474"
echo "  Bolt连接: bolt://localhost:8612"
echo "  用户名: neo4j"
echo "  密码: admin2024"
echo ""
echo "🔍 快速开始查询:"
echo '  MATCH (n) RETURN labels(n) as NodeType, count(n) as Count;'