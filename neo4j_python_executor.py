#!/usr/bin/env python3
"""
Neo4j Python执行器
直接通过Python连接Neo4j并执行Cypher脚本
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import time

try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⚠️ neo4j驱动未安装，请运行: pip install neo4j")

class Neo4jExecutor:
    def __init__(self, uri: str, username: str, password: str):
        """初始化Neo4j连接"""
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j驱动未安装")
            
        self.uri = uri
        self.username = username
        self.password = password
        self.driver: Optional[Driver] = None
        
    def connect(self) -> bool:
        """连接到Neo4j数据库"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            # 测试连接
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            print(f"✅ 成功连接到Neo4j: {self.uri}")
            return True
        except Exception as e:
            print(f"❌ 连接Neo4j失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
            print("🔒 Neo4j连接已关闭")
    
    def execute_cypher(self, cypher: str) -> Dict[str, Any]:
        """执行单个Cypher语句"""
        if not self.driver:
            raise RuntimeError("未连接到Neo4j")
            
        try:
            with self.driver.session() as session:
                result = session.run(cypher)
                records = []
                summary = result.consume()
                
                # 尝试获取结果记录
                try:
                    records = [record.data() for record in result]
                except:
                    # 如果查询不返回结果（如CREATE语句），records为空
                    pass
                
                return {
                    'success': True,
                    'records': records,
                    'summary': {
                        'query_type': summary.query_type,
                        'counters': dict(summary.counters),
                        'result_available_after': summary.result_available_after,
                        'result_consumed_after': summary.result_consumed_after
                    }
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'cypher': cypher[:100] + '...' if len(cypher) > 100 else cypher
            }
    
    def execute_cypher_file(self, file_path: str, skip_errors: bool = False) -> Dict[str, Any]:
        """执行Cypher脚本文件"""
        if not os.path.exists(file_path):
            return {'success': False, 'error': f'文件不存在: {file_path}'}
        
        print(f"📖 读取Cypher脚本: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割语句（简单的分割，基于分号和换行）
        statements = self._split_cypher_statements(content)
        
        print(f"📋 找到 {len(statements)} 个Cypher语句")
        
        results = []
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            if not statement.strip():
                continue
                
            print(f"\n⚡ 执行语句 {i}/{len(statements)}...")
            print(f"   {statement[:80]}{'...' if len(statement) > 80 else ''}")
            
            result = self.execute_cypher(statement)
            results.append(result)
            
            if result['success']:
                success_count += 1
                if result.get('summary', {}).get('counters'):
                    counters = result['summary']['counters']
                    changes = []
                    for key, value in counters.items():
                        if value > 0:
                            changes.append(f"{key}: {value}")
                    if changes:
                        print(f"   ✅ 完成: {', '.join(changes)}")
                    else:
                        print(f"   ✅ 完成")
                else:
                    print(f"   ✅ 完成")
                    
                # 显示查询结果（如果有）
                if result.get('records') and len(result['records']) > 0:
                    print(f"   📊 返回 {len(result['records'])} 条记录")
                    # 显示前几条记录
                    for record in result['records'][:5]:
                        print(f"      {record}")
                    if len(result['records']) > 5:
                        print(f"      ... 还有 {len(result['records']) - 5} 条记录")
            else:
                error_count += 1
                print(f"   ❌ 错误: {result['error']}")
                if not skip_errors:
                    print("💥 执行中断（使用 --skip-errors 跳过错误）")
                    break
            
            # 短暂延迟避免过快执行
            time.sleep(0.1)
        
        return {
            'success': error_count == 0,
            'total_statements': len(statements),
            'success_count': success_count,
            'error_count': error_count,
            'results': results
        }
    
    def _split_cypher_statements(self, content: str) -> List[str]:
        """分割Cypher语句"""
        # 移除注释行
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('//'):
                lines.append(line)
        
        # 重新组合并按分号分割
        cleaned_content = ' '.join(lines)
        
        # 简单的分号分割（可能需要更复杂的解析）
        statements = []
        current_statement = []
        
        # 按分号分割，但保留CALL语句的完整性
        parts = cleaned_content.split(';')
        
        for part in parts:
            part = part.strip()
            if part:
                current_statement.append(part)
                # 如果不是以CALL开头的语句，或者已经有完整的CALL语句
                if not part.upper().startswith('CALL') or len(current_statement) > 1:
                    statements.append('; '.join(current_statement))
                    current_statement = []
        
        # 处理最后一个语句
        if current_statement:
            statements.append('; '.join(current_statement))
        
        return [s.strip() for s in statements if s.strip()]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        queries = {
            'node_stats': "MATCH (n) RETURN labels(n)[0] as NodeType, count(n) as Count ORDER BY Count DESC",
            'relationship_stats': "MATCH ()-[r]->() RETURN type(r) as RelationType, count(r) as Count ORDER BY Count DESC",
            'entity_type_stats': "MATCH (e:Entity) RETURN e.type as EntityType, count(e) as Count ORDER BY Count DESC"
        }
        
        stats = {}
        for stat_name, query in queries.items():
            result = self.execute_cypher(query)
            if result['success']:
                stats[stat_name] = result['records']
            else:
                stats[stat_name] = f"错误: {result['error']}"
        
        return stats

def main():
    parser = argparse.ArgumentParser(description="Neo4j Python执行器")
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--username", "-u", default="neo4j", help="用户名")
    parser.add_argument("--password", "-p", required=True, help="密码")
    parser.add_argument("--file", "-f", help="要执行的Cypher脚本文件")
    parser.add_argument("--query", "-q", help="要执行的单个Cypher查询")
    parser.add_argument("--stats", action="store_true", help="显示数据库统计信息")
    parser.add_argument("--skip-errors", action="store_true", help="跳过错误继续执行")
    parser.add_argument("--dataset", help="数据集名称（自动生成脚本）")
    
    args = parser.parse_args()
    
    if not NEO4J_AVAILABLE:
        print("❌ 请先安装neo4j驱动: pip install neo4j")
        sys.exit(1)
    
    # 创建执行器
    executor = Neo4jExecutor(args.uri, args.username, args.password)
    
    try:
        # 连接到Neo4j
        if not executor.connect():
            sys.exit(1)
        
        # 如果指定了数据集，自动生成并执行脚本
        if args.dataset:
            print(f"🚀 自动处理数据集: {args.dataset}")
            
            # 生成Cypher脚本
            from generate_neo4j_cypher import Neo4jCypherGenerator
            generator = Neo4jCypherGenerator(args.dataset)
            
            # 检查数据文件
            file_status = generator.check_data_files()
            missing_files = [k for k, v in file_status.items() if not v]
            
            if missing_files:
                print(f"❌ 缺少数据文件: {', '.join(missing_files)}")
                sys.exit(1)
            
            # 生成脚本
            script_path = f"/tmp/neo4j_import_{args.dataset}.cypher"
            generator.save_script(script_path)
            
            # 执行脚本
            print(f"\n🎯 执行导入脚本...")
            result = executor.execute_cypher_file(script_path, args.skip_errors)
            
            print(f"\n📊 执行结果:")
            print(f"   总语句数: {result['total_statements']}")
            print(f"   成功: {result['success_count']}")
            print(f"   错误: {result['error_count']}")
            
            if result['success']:
                print("🎉 数据导入成功完成!")
            else:
                print("⚠️ 数据导入过程中有错误")
        
        # 执行脚本文件
        elif args.file:
            result = executor.execute_cypher_file(args.file, args.skip_errors)
            print(f"\n📊 执行结果:")
            print(f"   总语句数: {result['total_statements']}")
            print(f"   成功: {result['success_count']}")
            print(f"   错误: {result['error_count']}")
        
        # 执行单个查询
        elif args.query:
            result = executor.execute_cypher(args.query)
            if result['success']:
                print("✅ 查询执行成功")
                if result.get('records'):
                    for record in result['records']:
                        print(f"   {record}")
            else:
                print(f"❌ 查询执行失败: {result['error']}")
        
        # 显示统计信息
        if args.stats:
            print("\n📊 数据库统计信息:")
            stats = executor.get_database_stats()
            
            for stat_name, data in stats.items():
                print(f"\n{stat_name}:")
                if isinstance(data, list):
                    for item in data[:10]:  # 只显示前10项
                        print(f"   {item}")
                else:
                    print(f"   {data}")
    
    finally:
        executor.close()

if __name__ == "__main__":
    main()