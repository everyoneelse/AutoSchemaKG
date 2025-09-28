# Atlas RAG 知识图谱 Cypher 导入脚本展开器

这个工具可以将使用 `LOAD CSV` 的 Cypher 导入脚本展开为具体的 `CREATE` 和 `MATCH` 命令，方便调试和理解数据导入过程。

## 功能特点

- 📊 **CSV 数据读取**: 自动读取指定的 CSV 文件
- 🔧 **命令展开**: 将 `LOAD CSV` 操作转换为具体的 Cypher 命令
- 🛡️ **字符串转义**: 自动处理特殊字符的转义
- 📈 **统计信息**: 提供 CSV 文件处理摘要
- 🎯 **灵活输出**: 支持文件输出或标准输出

## 文件结构

```
/workspace/
├── expand_cypher_import.py     # 主要的展开器脚本
├── example_usage.py            # 使用示例和演示
├── expanded_cypher_import.cql  # 生成的展开脚本示例
└── mri_artifacts/              # 示例 CSV 数据目录
    ├── triples_csv/
    │   ├── text_nodes_mri_artifacts_from_json.csv
    │   ├── triple_nodes_mri_artifacts_from_json_without_emb.csv
    │   └── text_edges_mri_artifacts_from_json.csv
    └── concept_csv/
        ├── concept_nodes_mri_artifacts_from_json_with_concept.csv
        ├── triple_edges_mri_artifacts_from_json_with_concept.csv
        └── concept_edges_mri_artifacts_from_json_with_concept.csv
```

## 使用方法

### 1. 基本使用

```bash
# 显示帮助信息
python3 expand_cypher_import.py --help

# 显示 CSV 文件摘要
python3 expand_cypher_import.py --summary

# 生成展开脚本到文件
python3 expand_cypher_import.py --output expanded_script.cql

# 输出到标准输出
python3 expand_cypher_import.py
```

### 2. 指定自定义路径

```bash
# 指定 CSV 文件的基础路径
python3 expand_cypher_import.py --base-path /path/to/your/data --output result.cql
```

### 3. 运行示例

```bash
# 运行完整示例（包含示例数据生成）
python3 example_usage.py
```

## 原始 Cypher 脚本 vs 展开脚本

### 原始脚本（使用 LOAD CSV）

```cypher
// 导入文本节点
LOAD CSV WITH HEADERS FROM 'file:///mri_artifacts/triples_csv/text_nodes_mri_artifacts_from_json.csv' AS row
CREATE (t:Text {
    id: row.`name:ID`,
    content: row.content,
    metadata: row.metadata
});
```

### 展开脚本（具体命令）

```cypher
// 导入文本节点
CREATE (t:Text {id: 'text_001', content: 'MRI artifacts can significantly impact image quality', metadata: '{"source": "medical_paper_1"}'});
CREATE (t:Text {id: 'text_002', content: 'Motion artifacts are common in pediatric imaging', metadata: '{"source": "medical_paper_2"}'});
CREATE (t:Text {id: 'text_003', content: 'Susceptibility artifacts occur near metal implants', metadata: '{"source": "medical_paper_3"}'});
```

## 支持的数据类型

脚本支持以下类型的数据导入：

1. **文本节点** (`Text`): 包含文本内容和元数据
2. **实体节点** (`Entity`): 包含实体信息、类型、概念和同义词集
3. **概念节点** (`Concept`): 包含概念定义
4. **三元组关系** (`RELATES`): 实体间的关系
5. **概念关系** (`HAS_CONCEPT`): 实体到概念的关系
6. **文本关系** (`CONTAINS`): 文本到实体的关系

## 输出格式

生成的脚本包含以下部分：

1. **约束和索引创建**: 唯一性约束和性能索引
2. **数据导入命令**: 按类型分组的具体 CREATE 和 MATCH 命令
3. **统计查询**: 用于验证导入结果的查询命令

## 注意事项

- 确保 CSV 文件路径正确且文件存在
- CSV 文件必须包含正确的列标题
- 特殊字符会被自动转义
- 生成的脚本可以直接在 Neo4j 中执行

## 示例数据

脚本包含了 MRI 伪影相关的示例数据，包括：

- **实体**: motion_artifact, pediatric_patient, metal_implant, image_quality
- **概念**: motion, artifact, imaging, pediatric, patient, metal, implant, quality
- **关系**: affects, experiences, causes
- **文本**: 医学论文中关于 MRI 伪影的描述

## 错误处理

- 文件不存在时会显示警告并跳过
- CSV 读取错误会显示详细错误信息
- 字符串转义确保生成的 Cypher 语法正确

## 扩展性

可以通过修改 `CypherExpander` 类来支持：

- 新的节点类型
- 不同的关系类型
- 自定义的属性映射
- 额外的数据验证

## 性能考虑

- 大型 CSV 文件可能需要较长处理时间
- 生成的脚本对于大量数据可能需要分批执行
- 建议在执行前先在测试环境中验证

---

*生成时间: 2025-09-28*  
*数据集: mri_artifacts*