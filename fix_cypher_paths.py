#!/usr/bin/env python3
"""
修复Cypher脚本中的文件路径问题
将绝对路径转换为Neo4j可识别的相对路径格式
"""

import re
import sys
import os
from pathlib import Path

def fix_load_csv_paths(cypher_content: str, dataset_name: str) -> str:
    """
    修复LOAD CSV语句中的文件路径
    将绝对路径转换为相对路径格式
    """
    
    # 匹配LOAD CSV语句中的文件路径
    pattern = r"LOAD CSV WITH HEADERS FROM '([^']+)'"
    
    def replace_path(match):
        original_path = match.group(1)
        
        # 如果已经是file://格式，直接返回
        if original_path.startswith('file://'):
            return match.group(0)
        
        # 如果是绝对路径，提取相对部分
        if original_path.startswith('/'):
            # 查找dataset_name在路径中的位置
            if dataset_name in original_path:
                # 提取从dataset_name开始的相对路径
                parts = original_path.split('/')
                try:
                    dataset_index = parts.index(dataset_name)
                    relative_path = '/'.join(parts[dataset_index:])
                    new_path = f"file:///{relative_path}"
                    return f"LOAD CSV WITH HEADERS FROM '{new_path}'"
                except ValueError:
                    pass
        
        # 如果是相对路径，添加file://前缀
        if not original_path.startswith('file://'):
            # 确保路径以dataset_name开头
            if not original_path.startswith(dataset_name):
                new_path = f"file:///{dataset_name}/{original_path}"
            else:
                new_path = f"file:///{original_path}"
            return f"LOAD CSV WITH HEADERS FROM '{new_path}'"
        
        return match.group(0)
    
    # 替换所有LOAD CSV路径
    fixed_content = re.sub(pattern, replace_path, cypher_content)
    
    return fixed_content

def main():
    if len(sys.argv) < 2:
        print("用法: python fix_cypher_paths.py <cypher_file> [dataset_name]")
        print("示例: python fix_cypher_paths.py test.cypher mri_artifacts")
        sys.exit(1)
    
    cypher_file = sys.argv[1]
    dataset_name = sys.argv[2] if len(sys.argv) > 2 else "dataset"
    
    if not os.path.exists(cypher_file):
        print(f"❌ 文件不存在: {cypher_file}")
        sys.exit(1)
    
    print(f"🔧 修复Cypher脚本路径: {cypher_file}")
    print(f"📊 数据集名称: {dataset_name}")
    
    # 读取原始文件
    try:
        with open(cypher_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        sys.exit(1)
    
    # 修复路径
    fixed_content = fix_load_csv_paths(original_content, dataset_name)
    
    # 创建备份
    backup_file = f"{cypher_file}.backup"
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"💾 创建备份文件: {backup_file}")
    except Exception as e:
        print(f"⚠️ 创建备份失败: {e}")
    
    # 写入修复后的内容
    try:
        with open(cypher_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ 路径修复完成: {cypher_file}")
    except Exception as e:
        print(f"❌ 写入文件失败: {e}")
        sys.exit(1)
    
    # 显示修改的内容
    print("\n📋 修复的路径:")
    load_csv_lines = [line.strip() for line in fixed_content.split('\n') 
                      if 'LOAD CSV' in line and 'FROM' in line]
    
    for i, line in enumerate(load_csv_lines, 1):
        print(f"   {i}. {line}")
    
    print(f"\n🎉 完成! 共修复了 {len(load_csv_lines)} 个LOAD CSV语句")

if __name__ == "__main__":
    main()