#!/bin/bash
# Neo4j完整安装和设置脚本

set -e

echo "🚀 开始Neo4j完整安装和设置..."

# 1. 下载和安装Neo4j
NEO4J_VERSION="5.24.1"
NEO4J_HOME="/workspace/neo4j-server-dulce"

if [ ! -d "$NEO4J_HOME" ]; then
    echo "📥 下载Neo4j $NEO4J_VERSION..."
    cd /workspace
    wget -q https://dist.neo4j.org/neo4j-community-${NEO4J_VERSION}-unix.tar.gz
    tar -xzf neo4j-community-${NEO4J_VERSION}-unix.tar.gz
    mv neo4j-community-${NEO4J_VERSION} neo4j-server-dulce
    rm neo4j-community-${NEO4J_VERSION}-unix.tar.gz
    echo "✅ Neo4j安装完成"
else
    echo "✅ Neo4j已存在，跳过下载"
fi

# 2. 创建import目录
mkdir -p ${NEO4J_HOME}/import
echo "📁 创建import目录: ${NEO4J_HOME}/import"

# 3. 复制配置文件
cp /workspace/neo4j_scripts/neo4j.conf ${NEO4J_HOME}/conf/neo4j.conf
echo "⚙️ 复制配置文件完成"

# 4. 设置权限
chmod +x ${NEO4J_HOME}/bin/*
echo "🔐 设置执行权限完成"

# 5. 复制数据文件到import目录
echo "📋 复制数据文件到import目录..."
if [ -d "/workspace/import" ]; then
    cp -r /workspace/import/* ${NEO4J_HOME}/import/ 2>/dev/null || echo "⚠️ 部分文件复制失败，请检查"
    echo "✅ 数据文件复制完成"
    echo "📊 Import目录内容:"
    ls -la ${NEO4J_HOME}/import/
else
    echo "❌ /workspace/import 目录不存在，请先生成知识图谱数据"
fi

echo "🎉 Neo4j设置完成！"
echo "📍 Neo4j安装路径: $NEO4J_HOME"
echo "📍 Import目录: ${NEO4J_HOME}/import"
echo ""
echo "下一步请运行："
echo "  ./start_neo4j_demo.sh"
echo "  然后执行数据导入脚本"