#!/usr/bin/env python3
"""
改进的Neo4j导入脚本
基于用户提供的脚本，增加了错误处理、进度显示和语句分割优化
"""

from neo4j import GraphDatabase
from tqdm import tqdm
import re
import time
import sys
from typing import List, Dict, Any

def smart_split_cypher(cypher_content: str) -> List[str]:
    """
    智能分割Cypher语句
    处理复杂的语句，避免在字符串内部分割
    """
    # 移除注释
    lines = []
    for line in cypher_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('//'):
            lines.append(line)
    
    content = ' '.join(lines)
    
    # 更智能的语句分割
    statements = []
    current_stmt = []
    in_string = False
    quote_char = None
    i = 0
    
    while i < len(content):
        char = content[i]
        
        # 处理字符串
        if char in ['"', "'"] and not in_string:
            in_string = True
            quote_char = char
        elif char == quote_char and in_string:
            in_string = False
            quote_char = None
        
        # 处理分号
        elif char == ';' and not in_string:
            current_stmt.append(char)
            stmt = ''.join(current_stmt).strip()
            if stmt and stmt != ';':
                statements.append(stmt.rstrip(';'))
            current_stmt = []
            i += 1
            continue
        
        current_stmt.append(char)
        i += 1
    
    # 处理最后一个语句
    if current_stmt:
        stmt = ''.join(current_stmt).strip()
        if stmt:
            statements.append(stmt)
    
    return [s.strip() for s in statements if s.strip()]

def execute_cypher_with_progress(driver, cypher_file: str, skip_errors: bool = True) -> Dict[str, Any]:
    """
    执行Cypher脚本并显示进度
    """
    print(f"📖 读取Cypher文件: {cypher_file}")
    
    try:
        with open(cypher_file, encoding="utf-8") as f:
            cypher_content = f.read()
    except FileNotFoundError:
        print(f"❌ 文件不存在: {cypher_file}")
        return {"success": False, "error": "文件不存在"}
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return {"success": False, "error": str(e)}
    
    # 智能分割语句
    statements = smart_split_cypher(cypher_content)
    print(f"📋 找到 {len(statements)} 个Cypher语句")
    
    if not statements:
        print("⚠️ 没有找到有效的Cypher语句")
        return {"success": False, "error": "没有有效语句"}
    
    # 执行统计
    success_count = 0
    error_count = 0
    results = []
    
    with driver.session() as session:
        # 使用tqdm显示进度
        for i, stmt in enumerate(tqdm(statements, desc="执行Cypher语句"), 1):
            try:
                # 显示当前执行的语句（截取前80字符）
                stmt_preview = stmt[:80] + "..." if len(stmt) > 80 else stmt
                tqdm.write(f"⚡ [{i}/{len(statements)}] {stmt_preview}")
                
                # 执行语句
                start_time = time.time()
                result = session.run(stmt)
                
                # 获取结果摘要
                summary = result.consume()
                execution_time = time.time() - start_time
                
                # 记录成功
                success_count += 1
                
                # 显示执行结果
                counters = dict(summary.counters)
                changes = []
                for key, value in counters.items():
                    if value > 0:
                        changes.append(f"{key}:{value}")
                
                if changes:
                    tqdm.write(f"   ✅ 完成 ({execution_time:.2f}s): {', '.join(changes)}")
                else:
                    tqdm.write(f"   ✅ 完成 ({execution_time:.2f}s)")
                
                results.append({
                    "success": True,
                    "statement": stmt[:100],
                    "counters": counters,
                    "execution_time": execution_time
                })
                
            except Exception as e:
                error_count += 1
                error_msg = str(e)
                tqdm.write(f"   ❌ 错误: {error_msg}")
                
                results.append({
                    "success": False,
                    "statement": stmt[:100],
                    "error": error_msg
                })
                
                if not skip_errors:
                    tqdm.write("💥 执行中断（设置skip_errors=True可跳过错误）")
                    break
            
            # 短暂延迟，避免过快执行
            time.sleep(0.05)
    
    return {
        "success": error_count == 0,
        "total_statements": len(statements),
        "success_count": success_count,
        "error_count": error_count,
        "results": results
    }

def get_database_stats(driver) -> Dict[str, Any]:
    """获取数据库统计信息"""
    stats_queries = {
        "节点统计": "MATCH (n) RETURN labels(n)[0] as NodeType, count(n) as Count ORDER BY Count DESC",
        "关系统计": "MATCH ()-[r]->() RETURN type(r) as RelationType, count(r) as Count ORDER BY Count DESC",
        "实体类型": "MATCH (e:Entity) RETURN e.type as EntityType, count(e) as Count ORDER BY Count DESC LIMIT 10"
    }
    
    stats = {}
    with driver.session() as session:
        for stat_name, query in stats_queries.items():
            try:
                result = session.run(query)
                records = [dict(record) for record in result]
                stats[stat_name] = records
            except Exception as e:
                stats[stat_name] = f"错误: {e}"
    
    return stats

def main():
    """主函数 - 改进版本的导入脚本"""
    
    # 连接配置
    uri = "bolt://10.8.71.126:7687"
    user = "neo4j" 
    pwd = "graphrag123"
    cypher_file = "test.cypher"  # 您的Cypher文件
    
    print("🚀 Neo4j知识图谱导入工具")
    print("=" * 40)
    print(f"📍 Neo4j URI: {uri}")
    print(f"👤 用户名: {user}")
    print(f"📄 脚本文件: {cypher_file}")
    print()
    
    # 创建驱动连接
    try:
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        print("✅ 成功连接到Neo4j")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return
    
    try:
        # 测试连接
        with driver.session() as session:
            session.run("RETURN 1 as test")
        print("✅ 连接测试通过")
        print()
        
        # 执行导入
        print("🎯 开始执行Cypher脚本...")
        result = execute_cypher_with_progress(driver, cypher_file, skip_errors=True)
        
        print()
        print("📊 执行结果:")
        print(f"   总语句数: {result.get('total_statements', 0)}")
        print(f"   成功执行: {result.get('success_count', 0)}")
        print(f"   执行错误: {result.get('error_count', 0)}")
        
        if result.get('success'):
            print("🎉 导入成功完成!")
        elif result.get('error_count', 0) > 0:
            print("⚠️ 导入过程中有错误，但已跳过")
        else:
            print("❌ 导入失败")
            return
        
        # 显示数据库统计
        print()
        print("📈 数据库统计信息:")
        stats = get_database_stats(driver)
        
        for stat_name, data in stats.items():
            print(f"\n{stat_name}:")
            if isinstance(data, list):
                for item in data[:5]:  # 只显示前5项
                    print(f"   {item}")
                if len(data) > 5:
                    print(f"   ... 还有 {len(data) - 5} 项")
            else:
                print(f"   {data}")
        
        print("\n🎉 全部完成!")
        
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {e}")
    
    finally:
        driver.close()
        print("🔒 连接已关闭")

if __name__ == "__main__":
    main()