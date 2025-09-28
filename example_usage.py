#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例: 展开Atlas RAG知识图谱Cypher导入脚本

这个脚本演示如何使用CypherExpander来展开CSV导入操作
"""

import os
from expand_cypher_import import CypherExpander


def create_sample_csv_files():
    """创建一些示例CSV文件用于测试"""
    
    # 创建目录结构
    os.makedirs('/workspace/mri_artifacts/triples_csv', exist_ok=True)
    os.makedirs('/workspace/mri_artifacts/concept_csv', exist_ok=True)
    
    # 1. 示例文本节点CSV
    text_nodes_content = '''name:ID,content,metadata
text_001,"MRI artifacts can significantly impact image quality","{'source': 'medical_paper_1'}"
text_002,"Motion artifacts are common in pediatric imaging","{'source': 'medical_paper_2'}"
text_003,"Susceptibility artifacts occur near metal implants","{'source': 'medical_paper_3'}"
'''
    
    with open('/workspace/mri_artifacts/triples_csv/text_nodes_mri_artifacts_from_json.csv', 'w', encoding='utf-8') as f:
        f.write(text_nodes_content)
    
    # 2. 示例实体节点CSV
    triple_nodes_content = '''name:ID,type,concepts,synsets
motion_artifact,artifact,"['motion', 'artifact', 'imaging']","['motion.n.01', 'artifact.n.01']"
pediatric_patient,patient,"['pediatric', 'patient', 'child']","['child.n.01', 'patient.n.01']"
metal_implant,implant,"['metal', 'implant', 'medical_device']","['implant.n.01', 'metal.n.01']"
image_quality,quality,"['image', 'quality', 'assessment']","['quality.n.01', 'image.n.01']"
'''
    
    with open('/workspace/mri_artifacts/triples_csv/triple_nodes_mri_artifacts_from_json_without_emb.csv', 'w', encoding='utf-8') as f:
        f.write(triple_nodes_content)
    
    # 3. 示例概念节点CSV
    concept_nodes_content = '''concept_id:ID,name
concept_001,motion
concept_002,artifact
concept_003,imaging
concept_004,pediatric
concept_005,patient
concept_006,metal
concept_007,implant
concept_008,quality
'''
    
    with open('/workspace/mri_artifacts/concept_csv/concept_nodes_mri_artifacts_from_json_with_concept.csv', 'w', encoding='utf-8') as f:
        f.write(concept_nodes_content)
    
    # 4. 示例三元组关系CSV
    triple_edges_content = ''':START_ID,:END_ID,relation,concepts,synsets
motion_artifact,image_quality,affects,"['affects', 'impact']","['affect.v.01']"
pediatric_patient,motion_artifact,experiences,"['experiences', 'has']","['experience.v.01']"
metal_implant,motion_artifact,causes,"['causes', 'produces']","['cause.v.01']"
'''
    
    with open('/workspace/mri_artifacts/concept_csv/triple_edges_mri_artifacts_from_json_with_concept.csv', 'w', encoding='utf-8') as f:
        f.write(triple_edges_content)
    
    # 5. 示例概念关系CSV
    concept_edges_content = ''':START_ID,:END_ID
motion_artifact,concept_001
motion_artifact,concept_002
pediatric_patient,concept_004
pediatric_patient,concept_005
metal_implant,concept_006
metal_implant,concept_007
image_quality,concept_008
'''
    
    with open('/workspace/mri_artifacts/concept_csv/concept_edges_mri_artifacts_from_json_with_concept.csv', 'w', encoding='utf-8') as f:
        f.write(concept_edges_content)
    
    # 6. 示例文本关系CSV
    text_edges_content = ''':START_ID,:END_ID
text_001,motion_artifact
text_001,image_quality
text_002,pediatric_patient
text_002,motion_artifact
text_003,metal_implant
text_003,motion_artifact
'''
    
    with open('/workspace/mri_artifacts/triples_csv/text_edges_mri_artifacts_from_json.csv', 'w', encoding='utf-8') as f:
        f.write(text_edges_content)
    
    print("示例CSV文件已创建完成！")


def main():
    print("="*70)
    print("Atlas RAG 知识图谱Cypher展开器 - 使用示例")
    print("="*70)
    
    # 创建示例CSV文件
    print("\n1. 创建示例CSV文件...")
    create_sample_csv_files()
    
    # 创建展开器实例
    print("\n2. 初始化Cypher展开器...")
    expander = CypherExpander(base_path='/workspace')
    
    # 显示CSV文件摘要
    print("\n3. CSV文件处理摘要:")
    expander.print_summary()
    
    # 生成展开的Cypher脚本
    print("\n4. 生成展开的Cypher脚本...")
    output_file = '/workspace/expanded_cypher_import.cql'
    cypher_script = expander.generate_expanded_cypher(output_file=output_file)
    
    print(f"\n5. 脚本已生成并保存到: {output_file}")
    print(f"   脚本总行数: {len(cypher_script.splitlines())}")
    
    # 显示部分生成的脚本内容
    print("\n6. 生成脚本的前20行预览:")
    print("-" * 50)
    lines = cypher_script.splitlines()
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:2d}: {line}")
    if len(lines) > 20:
        print(f"... (还有 {len(lines) - 20} 行)")
    
    print("\n" + "="*70)
    print("示例运行完成！")
    print("="*70)
    
    # 提供使用说明
    print("\n使用说明:")
    print("1. 直接运行展开器:")
    print("   python expand_cypher_import.py --base-path /workspace --output expanded.cql")
    print("\n2. 显示CSV文件摘要:")
    print("   python expand_cypher_import.py --summary")
    print("\n3. 输出到标准输出:")
    print("   python expand_cypher_import.py --base-path /workspace")


if __name__ == "__main__":
    main()