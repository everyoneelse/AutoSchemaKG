#!/usr/bin/env python3
"""
Neo4j知识图谱导入Cypher脚本生成器
支持Atlas RAG项目的知识图谱数据导入
"""

import os
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import json

class Neo4jCypherGenerator:
    def __init__(self, dataset_name: str, import_base_path: str = "/workspace/import"):
        self.dataset_name = dataset_name
        self.import_base_path = Path(import_base_path)
        self.dataset_path = self.import_base_path / dataset_name
        
    def check_data_files(self) -> Dict[str, bool]:
        """检查必需的数据文件是否存在"""
        required_files = {
            'text_nodes': f'triples_csv/text_nodes_{self.dataset_name}_from_json.csv',
            'triple_nodes': f'triples_csv/triple_nodes_{self.dataset_name}_from_json_without_emb.csv',
            'concept_nodes': f'concept_csv/concept_nodes_{self.dataset_name}_from_json_with_concept.csv',
            'triple_edges': f'concept_csv/triple_edges_{self.dataset_name}_from_json_with_concept.csv',
            'concept_edges': f'concept_csv/concept_edges_{self.dataset_name}_from_json_with_concept.csv',
            'text_edges': f'triples_csv/text_edges_{self.dataset_name}_from_json.csv'
        }
        
        file_status = {}
        for file_type, file_path in required_files.items():
            full_path = self.dataset_path / file_path
            file_status[file_type] = full_path.exists()
            if full_path.exists():
                print(f"✅ {file_type}: {full_path}")
            else:
                print(f"❌ {file_type}: {full_path} (文件不存在)")
                
        return file_status
    
    def generate_n10s_setup(self) -> str:
        """生成n10s插件设置的Cypher脚本"""
        return """
// =============================================================================
// n10s (RDF) 插件设置
// =============================================================================

// 创建Resource节点的URI唯一约束
CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS 
FOR (r:Resource) REQUIRE r.uri IS UNIQUE;

// 初始化n10s RDF配置
CALL n10s.graphconfig.init({ 
    handleMultival: "OVERWRITE", 
    handleVocabUris: "SHORTEN", 
    keepLangTag: false, 
    handleRDFTypes: "NODES" 
});

"""

    def generate_constraints_and_indexes(self) -> str:
        """生成约束和索引的Cypher脚本"""
        return f"""
// =============================================================================
// 约束和索引创建
// =============================================================================

// 创建唯一性约束
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS 
FOR (e:Entity) REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT concept_id_unique IF NOT EXISTS 
FOR (c:Concept) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT text_id_unique IF NOT EXISTS 
FOR (t:Text) REQUIRE t.id IS UNIQUE;

// 创建性能索引
CREATE INDEX entity_name_index IF NOT EXISTS 
FOR (n:Entity) ON (n.name);

CREATE INDEX concept_name_index IF NOT EXISTS 
FOR (c:Concept) ON (c.name);

CREATE INDEX entity_type_index IF NOT EXISTS 
FOR (n:Entity) ON (n.type);

"""

    def generate_data_import(self) -> str:
        """生成数据导入的Cypher脚本"""
        return f"""
// =============================================================================
// 数据导入
// =============================================================================

// 1. 导入文本节点
LOAD CSV WITH HEADERS FROM 'file:///{self.dataset_name}/triples_csv/text_nodes_{self.dataset_name}_from_json.csv' AS row
CREATE (t:Text {{
    id: row.`name:ID`,
    content: row.content,
    metadata: row.metadata
}});

// 2. 导入三元组节点 (实体、事件)
LOAD CSV WITH HEADERS FROM 'file:///{self.dataset_name}/triples_csv/triple_nodes_{self.dataset_name}_from_json_without_emb.csv' AS row
CREATE (n:Entity {{
    id: row.`name:ID`,
    name: row.`name:ID`,
    type: row.type,
    concepts: row.concepts,
    synsets: row.synsets
}});

// 3. 导入概念节点
LOAD CSV WITH HEADERS FROM 'file:///{self.dataset_name}/concept_csv/concept_nodes_{self.dataset_name}_from_json_with_concept.csv' AS row
CREATE (c:Concept {{
    id: row.`concept_id:ID`,
    name: row.name
}});

// 4. 导入三元组关系
LOAD CSV WITH HEADERS FROM 'file:///{self.dataset_name}/concept_csv/triple_edges_{self.dataset_name}_from_json_with_concept.csv' AS row
MATCH (a:Entity {{id: row.`:START_ID`}})
MATCH (b:Entity {{id: row.`:END_ID`}})
CREATE (a)-[r:RELATES {{
    relation: row.relation,
    concepts: row.concepts,
    synsets: row.synsets
}}]->(b);

// 5. 导入概念关系
LOAD CSV WITH HEADERS FROM 'file:///{self.dataset_name}/concept_csv/concept_edges_{self.dataset_name}_from_json_with_concept.csv' AS row
MATCH (e:Entity {{id: row.`:START_ID`}})
MATCH (c:Concept {{id: row.`:END_ID`}})
CREATE (e)-[:HAS_CONCEPT]->(c);

// 6. 导入文本关系
LOAD CSV WITH HEADERS FROM 'file:///{self.dataset_name}/triples_csv/text_edges_{self.dataset_name}_from_json.csv' AS row
MATCH (t:Text {{id: row.`:START_ID`}})
MATCH (e:Entity {{id: row.`:END_ID`}})
CREATE (t)-[:CONTAINS]->(e);

"""

    def generate_statistics_query(self) -> str:
        """生成统计查询的Cypher脚本"""
        return """
// =============================================================================
// 导入统计和验证
// =============================================================================

// 显示节点统计
MATCH (n) 
RETURN labels(n)[0] as NodeType, count(n) as Count 
ORDER BY Count DESC;

// 显示关系统计
MATCH ()-[r]->() 
RETURN type(r) as RelationType, count(r) as Count 
ORDER BY Count DESC;

// 显示实体类型分布
MATCH (e:Entity) 
RETURN e.type as EntityType, count(e) as Count 
ORDER BY Count DESC;

// 显示概念使用频率 (前20个)
MATCH (e:Entity)-[:HAS_CONCEPT]->(c:Concept)
RETURN c.name as ConceptName, count(e) as EntityCount
ORDER BY EntityCount DESC
LIMIT 20;

// 显示实体-概念关系示例
MATCH (e:Entity)-[:HAS_CONCEPT]->(c:Concept)
RETURN e.name as EntityName, e.type as EntityType, c.name as ConceptName
LIMIT 10;

"""

    def generate_cleanup_script(self) -> str:
        """生成清理脚本（谨慎使用）"""
        return """
// =============================================================================
// 数据清理脚本 (谨慎使用!)
// =============================================================================

// 清空所有数据 - 谨慎使用!
// MATCH (n) DETACH DELETE n;

// 只清理特定标签的节点
// MATCH (e:Entity) DETACH DELETE e;
// MATCH (c:Concept) DETACH DELETE c;
// MATCH (t:Text) DETACH DELETE t;

// 删除约束
// DROP CONSTRAINT entity_id_unique IF EXISTS;
// DROP CONSTRAINT concept_id_unique IF EXISTS;
// DROP CONSTRAINT text_id_unique IF EXISTS;
// DROP CONSTRAINT n10s_unique_uri IF EXISTS;

"""

    def generate_full_script(self, include_n10s: bool = True, include_cleanup: bool = False) -> str:
        """生成完整的Cypher脚本"""
        script_parts = []
        
        # 添加头部注释
        script_parts.append(f"""
// =============================================================================
// Atlas RAG 知识图谱导入脚本
// 数据集: {self.dataset_name}
// 生成时间: {pd.Timestamp.now()}
// =============================================================================

""")
        
        # n10s设置（可选）
        if include_n10s:
            script_parts.append(self.generate_n10s_setup())
        
        # 约束和索引
        script_parts.append(self.generate_constraints_and_indexes())
        
        # 数据导入
        script_parts.append(self.generate_data_import())
        
        # 统计查询
        script_parts.append(self.generate_statistics_query())
        
        # 清理脚本（可选）
        if include_cleanup:
            script_parts.append(self.generate_cleanup_script())
        
        return '\n'.join(script_parts)
    
    def save_script(self, output_path: str, include_n10s: bool = True, include_cleanup: bool = False):
        """保存生成的Cypher脚本到文件"""
        script_content = self.generate_full_script(include_n10s, include_cleanup)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"✅ Cypher脚本已保存到: {output_path}")
        return output_path

def main():
    parser = argparse.ArgumentParser(description="生成Neo4j知识图谱导入Cypher脚本")
    parser.add_argument("dataset_name", help="数据集名称 (如: Dulce, CICGPC_Glazing_ver1.0a)")
    parser.add_argument("--import-path", default="/workspace/import", help="导入数据路径")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--no-n10s", action="store_true", help="不包含n10s RDF配置")
    parser.add_argument("--include-cleanup", action="store_true", help="包含数据清理脚本")
    parser.add_argument("--check-only", action="store_true", help="只检查数据文件，不生成脚本")
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = Neo4jCypherGenerator(args.dataset_name, args.import_path)
    
    print(f"🚀 Neo4j Cypher脚本生成器")
    print(f"📊 数据集: {args.dataset_name}")
    print(f"📁 数据路径: {args.import_path}")
    print("=" * 50)
    
    # 检查数据文件
    print("🔍 检查数据文件...")
    file_status = generator.check_data_files()
    
    missing_files = [k for k, v in file_status.items() if not v]
    if missing_files:
        print(f"\n❌ 缺少以下数据文件: {', '.join(missing_files)}")
        print("请先运行知识图谱生成流程:")
        print("  python example_scripts/1_slice_kg_extraction.py")
        print("  python example_scripts/2_concept_generation.py")
        if not args.check_only:
            return
    else:
        print("\n✅ 所有必需的数据文件都存在")
    
    if args.check_only:
        return
    
    # 确定输出文件路径
    if args.output:
        output_path = args.output
    else:
        output_path = f"/workspace/neo4j_import_{args.dataset_name}.cypher"
    
    # 生成并保存脚本
    print(f"\n📝 生成Cypher脚本...")
    generator.save_script(
        output_path, 
        include_n10s=not args.no_n10s,
        include_cleanup=args.include_cleanup
    )
    
    print(f"\n🎉 脚本生成完成!")
    print(f"\n📋 使用方法:")
    print(f"  1. 复制数据文件到Neo4j import目录")
    print(f"  2. 在Neo4j Browser中执行脚本: {output_path}")
    print(f"  3. 或使用cypher-shell: cypher-shell -f {output_path}")
    print(f"  4. Docker环境: docker exec neo4j cypher-shell -u neo4j -p password -f /import/script.cypher")

if __name__ == "__main__":
    # 添加pandas导入用于时间戳
    try:
        import pandas as pd
    except ImportError:
        import datetime
        class pd:
            class Timestamp:
                @staticmethod
                def now():
                    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    main()