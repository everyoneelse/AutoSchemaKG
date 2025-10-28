#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atlas RAG 知识图谱导入脚本展开器
将CSV导入的Cypher命令展开为具体的CREATE/MATCH命令

生成时间: 2025-09-28
数据集: mri_artifacts
"""

import csv
import os
import sys
from typing import List, Dict, Any
import argparse


class CypherExpander:
    def __init__(self, base_path: str = "/workspace"):
        self.base_path = base_path
        self.csv_files = {
            'text_nodes': 'mri_artifacts/triples_csv/text_nodes_mri_artifacts_from_json.csv',
            'triple_nodes': 'mri_artifacts/triples_csv/triple_nodes_mri_artifacts_from_json_without_emb.csv',
            'concept_nodes': 'mri_artifacts/concept_csv/concept_nodes_mri_artifacts_from_json_with_concept.csv',
            'triple_edges': 'mri_artifacts/concept_csv/triple_edges_mri_artifacts_from_json_with_concept.csv',
            'concept_edges': 'mri_artifacts/concept_csv/concept_edges_mri_artifacts_from_json_with_concept.csv',
            'text_edges': 'mri_artifacts/triples_csv/text_edges_mri_artifacts_from_json.csv'
        }
        
    def escape_cypher_string(self, value: str) -> str:
        """转义Cypher字符串中的特殊字符"""
        if value is None:
            return "null"
        # 转义单引号和反斜杠
        value = str(value).replace("\\", "\\\\").replace("'", "\\'")
        return f"'{value}'"
    
    def generate_constraints_and_indexes(self) -> List[str]:
        """生成约束和索引创建命令"""
        commands = [
            "// =============================================================================",
            "// 约束和索引创建",
            "// =============================================================================",
            "",
            "// 创建唯一性约束",
            "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;",
            "CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;",
            "CREATE CONSTRAINT text_id_unique IF NOT EXISTS FOR (t:Text) REQUIRE t.id IS UNIQUE;",
            "",
            "// 创建性能索引",
            "CREATE INDEX entity_name_index IF NOT EXISTS FOR (n:Entity) ON (n.name);",
            "CREATE INDEX concept_name_index IF NOT EXISTS FOR (c:Concept) ON (c.name);",
            "CREATE INDEX entity_type_index IF NOT EXISTS FOR (n:Entity) ON (n.type);",
            ""
        ]
        return commands
    
    def read_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """读取CSV文件并返回数据行"""
        full_path = os.path.join(self.base_path, file_path)
        if not os.path.exists(full_path):
            print(f"警告: CSV文件不存在: {full_path}")
            return []
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"错误: 读取CSV文件失败 {full_path}: {e}")
            return []
    
    def generate_text_nodes(self) -> List[str]:
        """生成文本节点创建命令"""
        commands = [
            "// =============================================================================",
            "// 1. 导入文本节点",
            "// =============================================================================",
            ""
        ]
        
        data = self.read_csv_file(self.csv_files['text_nodes'])
        for row in data:
            node_id = self.escape_cypher_string(row.get('name:ID', ''))
            content = self.escape_cypher_string(row.get('content', ''))
            metadata = self.escape_cypher_string(row.get('metadata', ''))
            
            cmd = f"CREATE (t:Text {{id: {node_id}, content: {content}, metadata: {metadata}}});"
            commands.append(cmd)
        
        commands.append("")
        return commands
    
    def generate_entity_nodes(self) -> List[str]:
        """生成实体节点创建命令"""
        commands = [
            "// =============================================================================",
            "// 2. 导入三元组节点 (实体、事件)",
            "// =============================================================================",
            ""
        ]
        
        data = self.read_csv_file(self.csv_files['triple_nodes'])
        for row in data:
            node_id = self.escape_cypher_string(row.get('name:ID', ''))
            node_type = self.escape_cypher_string(row.get('type', ''))
            concepts = self.escape_cypher_string(row.get('concepts', ''))
            synsets = self.escape_cypher_string(row.get('synsets', ''))
            
            cmd = f"CREATE (n:Entity {{id: {node_id}, name: {node_id}, type: {node_type}, concepts: {concepts}, synsets: {synsets}}});"
            commands.append(cmd)
        
        commands.append("")
        return commands
    
    def generate_concept_nodes(self) -> List[str]:
        """生成概念节点创建命令"""
        commands = [
            "// =============================================================================",
            "// 3. 导入概念节点",
            "// =============================================================================",
            ""
        ]
        
        data = self.read_csv_file(self.csv_files['concept_nodes'])
        for row in data:
            concept_id = self.escape_cypher_string(row.get('concept_id:ID', ''))
            name = self.escape_cypher_string(row.get('name', ''))
            
            cmd = f"CREATE (c:Concept {{id: {concept_id}, name: {name}}});"
            commands.append(cmd)
        
        commands.append("")
        return commands
    
    def generate_triple_edges(self) -> List[str]:
        """生成三元组关系创建命令"""
        commands = [
            "// =============================================================================",
            "// 4. 导入三元组关系",
            "// =============================================================================",
            ""
        ]
        
        data = self.read_csv_file(self.csv_files['triple_edges'])
        for row in data:
            start_id = self.escape_cypher_string(row.get(':START_ID', ''))
            end_id = self.escape_cypher_string(row.get(':END_ID', ''))
            relation = self.escape_cypher_string(row.get('relation', ''))
            concepts = self.escape_cypher_string(row.get('concepts', ''))
            synsets = self.escape_cypher_string(row.get('synsets', ''))
            
            cmd = f"MATCH (a:Entity {{id: {start_id}}}) MATCH (b:Entity {{id: {end_id}}}) CREATE (a)-[r:RELATES {{relation: {relation}, concepts: {concepts}, synsets: {synsets}}}]->(b);"
            commands.append(cmd)
        
        commands.append("")
        return commands
    
    def generate_concept_edges(self) -> List[str]:
        """生成概念关系创建命令"""
        commands = [
            "// =============================================================================",
            "// 5. 导入概念关系",
            "// =============================================================================",
            ""
        ]
        
        data = self.read_csv_file(self.csv_files['concept_edges'])
        for row in data:
            start_id = self.escape_cypher_string(row.get(':START_ID', ''))
            end_id = self.escape_cypher_string(row.get(':END_ID', ''))
            
            cmd = f"MATCH (e:Entity {{id: {start_id}}}) MATCH (c:Concept {{id: {end_id}}}) CREATE (e)-[:HAS_CONCEPT]->(c);"
            commands.append(cmd)
        
        commands.append("")
        return commands
    
    def generate_text_edges(self) -> List[str]:
        """生成文本关系创建命令"""
        commands = [
            "// =============================================================================",
            "// 6. 导入文本关系",
            "// =============================================================================",
            ""
        ]
        
        data = self.read_csv_file(self.csv_files['text_edges'])
        for row in data:
            start_id = self.escape_cypher_string(row.get(':START_ID', ''))
            end_id = self.escape_cypher_string(row.get(':END_ID', ''))
            
            cmd = f"MATCH (t:Text {{id: {start_id}}}) MATCH (e:Entity {{id: {end_id}}}) CREATE (t)-[:CONTAINS]->(e);"
            commands.append(cmd)
        
        commands.append("")
        return commands
    
    def generate_statistics_queries(self) -> List[str]:
        """生成统计和验证查询"""
        commands = [
            "// =============================================================================",
            "// 导入统计和验证",
            "// =============================================================================",
            "",
            "// 显示节点统计",
            "MATCH (n) RETURN labels(n)[0] as NodeType, count(n) as Count ORDER BY Count DESC;",
            "",
            "// 显示关系统计",
            "MATCH ()-[r]->() RETURN type(r) as RelationType, count(r) as Count ORDER BY Count DESC;",
            "",
            "// 显示实体类型分布",
            "MATCH (e:Entity) RETURN e.type as EntityType, count(e) as Count ORDER BY Count DESC;",
            "",
            "// 显示概念使用频率 (前20个)",
            "MATCH (e:Entity)-[:HAS_CONCEPT]->(c:Concept) RETURN c.name as ConceptName, count(e) as EntityCount ORDER BY EntityCount DESC LIMIT 20;",
            "",
            "// 显示实体-概念关系示例",
            "MATCH (e:Entity)-[:HAS_CONCEPT]->(c:Concept) RETURN e.name as EntityName, e.type as EntityType, c.name as ConceptName LIMIT 10;",
            ""
        ]
        return commands
    
    def generate_expanded_cypher(self, output_file: str = None) -> str:
        """生成完整的展开Cypher脚本"""
        all_commands = []
        
        # 添加文件头部注释
        all_commands.extend([
            "// =============================================================================",
            "// Atlas RAG 知识图谱导入脚本 (展开版)",
            "// 数据集: mri_artifacts",
            f"// 生成时间: {self._get_current_time()}",
            "// 注意: 此脚本将CSV导入操作展开为具体的CREATE/MATCH命令",
            "// =============================================================================",
            "",
            ""
        ])
        
        # 生成各部分命令
        all_commands.extend(self.generate_constraints_and_indexes())
        all_commands.extend(self.generate_text_nodes())
        all_commands.extend(self.generate_entity_nodes())
        all_commands.extend(self.generate_concept_nodes())
        all_commands.extend(self.generate_triple_edges())
        all_commands.extend(self.generate_concept_edges())
        all_commands.extend(self.generate_text_edges())
        all_commands.extend(self.generate_statistics_queries())
        
        # 将命令列表转换为字符串
        cypher_script = "\n".join(all_commands)
        
        # 如果指定了输出文件，写入文件
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(cypher_script)
                print(f"展开的Cypher脚本已保存到: {output_file}")
            except Exception as e:
                print(f"错误: 无法写入输出文件 {output_file}: {e}")
        
        return cypher_script
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def print_summary(self):
        """打印处理摘要"""
        print("\n" + "="*70)
        print("CSV文件处理摘要:")
        print("="*70)
        
        for name, path in self.csv_files.items():
            full_path = os.path.join(self.base_path, path)
            if os.path.exists(full_path):
                data = self.read_csv_file(path)
                print(f"{name:20} | {len(data):6} 行 | {path}")
            else:
                print(f"{name:20} | {'缺失':>6} | {path}")
        
        print("="*70)


def main():
    parser = argparse.ArgumentParser(description='展开Atlas RAG知识图谱Cypher导入脚本')
    parser.add_argument('--base-path', '-p', default='/workspace', 
                       help='CSV文件的基础路径 (默认: /workspace)')
    parser.add_argument('--output', '-o', 
                       help='输出文件路径 (可选，如果不指定则打印到标准输出)')
    parser.add_argument('--summary', '-s', action='store_true',
                       help='显示CSV文件处理摘要')
    
    args = parser.parse_args()
    
    # 创建展开器实例
    expander = CypherExpander(base_path=args.base_path)
    
    # 显示摘要信息
    if args.summary:
        expander.print_summary()
    
    # 生成展开的Cypher脚本
    try:
        cypher_script = expander.generate_expanded_cypher(output_file=args.output)
        
        # 如果没有指定输出文件，打印到标准输出
        if not args.output:
            print(cypher_script)
            
    except Exception as e:
        print(f"错误: 生成Cypher脚本失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()