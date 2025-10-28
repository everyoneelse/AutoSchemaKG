# NetworkX可视化工具使用说明

## 概述
这个工具可以帮助你使用NetworkX来可视化存储在pickle文件中的网络数据，特别适用于`mri_artifacts_without_concept.pkl`等文件。

## 文件说明
- `visualize_pkl_networkx.py` - 主要的可视化脚本
- `create_sample_data.py` - 创建示例数据的脚本
- `README_NetworkX_Visualization.md` - 本说明文档

## 安装依赖
脚本需要以下Python包：
```bash
pip install networkx matplotlib pandas numpy seaborn
```

## 使用方法

### 基本使用
```bash
python3 visualize_pkl_networkx.py your_file.pkl
```

### 示例
```bash
# 可视化你的MRI数据文件
python3 visualize_pkl_networkx.py mri_artifacts_without_concept.pkl

# 可视化示例数据
python3 visualize_pkl_networkx.py sample_adjacency_dict.pkl
```

## 支持的数据格式

脚本可以自动识别并处理以下数据格式：

### 1. NetworkX图对象
如果pkl文件直接包含NetworkX图对象，脚本会直接使用。

### 2. 字典格式
- **邻接字典**: `{'node1': ['node2', 'node3'], 'node2': ['node1']}`
- **带权重**: `{'node1': {'node2': 0.8, 'node3': 0.6}}`
- **节点和边**: `{'nodes': [...], 'edges': [...]}`

### 3. 列表格式
- **边列表**: `[('node1', 'node2'), ('node2', 'node3')]`
- **节点列表**: `['node1', 'node2', 'node3']`

### 4. NumPy数组
- **邻接矩阵**: 2D方阵表示节点间的连接关系
- **1D数组**: 创建路径图

### 5. Pandas DataFrame
- **边表**: 包含'source'和'target'列
- **邻接矩阵**: 方形DataFrame

## 输出结果

脚本会生成：

1. **数据结构分析**: 显示数据类型、长度和内容预览
2. **图统计信息**: 包括节点数、边数、连通性等
3. **可视化图像**: PNG格式的网络图，保存为`原文件名_network_visualization.png`

## 可视化特性

- **自适应布局**: 根据图的大小选择最佳布局算法
- **节点大小**: 基于节点度数调整大小
- **颜色编码**: 使用不同颜色区分节点和边
- **标签显示**: 小图显示节点标签，大图隐藏以避免拥挤
- **统计信息**: 在图上显示基本统计信息

## 自定义选项

你可以修改脚本中的以下参数：

```python
# 图像大小
figsize = (12, 8)

# 节点颜色
node_color = 'lightblue'

# 边的透明度
edge_alpha = 0.5

# 最大显示标签的节点数
max_labels = 50
```

## 示例数据

运行以下命令创建示例数据：
```bash
python3 create_sample_data.py
```

这会创建4个示例文件：
- `sample_adjacency_dict.pkl` - 邻接字典格式
- `sample_edge_list.pkl` - 边列表格式  
- `sample_weighted_network.pkl` - 带权重网络
- `sample_adjacency_matrix.pkl` - 邻接矩阵格式

## 故障排除

### 常见问题

1. **文件不存在错误**
   - 确保pkl文件在当前目录或提供完整路径
   - 检查文件名拼写

2. **数据格式不支持**
   - 脚本会显示数据结构分析
   - 根据分析结果调整数据格式

3. **图像显示问题**
   - 在服务器环境中，图像会保存为PNG文件
   - 使用图像查看器打开生成的PNG文件

4. **中文字体问题**
   - 脚本已配置支持中文显示
   - 如有问题，可以修改字体设置

### 性能考虑

- **大图处理**: 超过200个节点时使用随机布局以提高速度
- **内存使用**: 大型网络可能需要较多内存
- **可视化质量**: 节点过多时会隐藏标签以保持清晰度

## 高级功能

### 自定义可视化
你可以修改`visualize_graph`函数来：
- 改变颜色方案
- 调整布局参数
- 添加更多统计信息
- 自定义节点和边的样式

### 批处理
处理多个文件：
```bash
for file in *.pkl; do
    python3 visualize_pkl_networkx.py "$file"
done
```

## 联系和支持

如果遇到问题或需要添加新的数据格式支持，请检查：
1. 数据结构分析输出
2. 错误消息
3. 确认数据格式是否符合预期

脚本设计为尽可能通用和灵活，应该能处理大多数常见的网络数据格式。