#!/usr/bin/env python3
"""
NetworkX可视化脚本 - 用于可视化mri_artifacts_without_concept.pkl文件
支持多种数据格式：图、邻接矩阵、边列表、节点关系等
"""

import pickle
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple, Union

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_pickle_file(file_path: str) -> Any:
    """加载pickle文件"""
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        print(f"✓ 成功加载文件: {file_path}")
        return data
    except Exception as e:
        print(f"✗ 加载文件失败: {e}")
        return None

def analyze_data_structure(data: Any) -> None:
    """分析数据结构"""
    print("\n" + "="*50)
    print("数据结构分析")
    print("="*50)
    
    print(f"数据类型: {type(data)}")
    
    if hasattr(data, '__len__'):
        try:
            print(f"数据长度: {len(data)}")
        except:
            pass
    
    if isinstance(data, dict):
        print(f"字典键: {list(data.keys())}")
        for key, value in list(data.items())[:3]:  # 显示前3个键值对
            print(f"  {key}: {type(value)} - {str(value)[:100]}...")
    
    elif isinstance(data, list):
        print(f"列表前几个元素:")
        for i, item in enumerate(data[:5]):
            print(f"  [{i}]: {type(item)} - {str(item)[:100]}...")
    
    elif isinstance(data, np.ndarray):
        print(f"数组形状: {data.shape}")
        print(f"数据类型: {data.dtype}")
        print(f"数组内容预览:\n{data}")
    
    elif hasattr(data, 'nodes') and hasattr(data, 'edges'):
        print("检测到NetworkX图对象")
        print(f"节点数: {data.number_of_nodes()}")
        print(f"边数: {data.number_of_edges()}")
        print(f"是否为有向图: {data.is_directed()}")
    
    else:
        print(f"数据内容: {str(data)[:200]}...")

def create_graph_from_data(data: Any) -> nx.Graph:
    """根据数据类型创建NetworkX图"""
    G = nx.Graph()
    
    # 如果已经是NetworkX图
    if hasattr(data, 'nodes') and hasattr(data, 'edges'):
        print("数据已经是NetworkX图格式")
        return data
    
    # 如果是字典格式
    elif isinstance(data, dict):
        print("尝试从字典创建图...")
        
        # 检查是否有nodes和edges键
        if 'nodes' in data and 'edges' in data:
            G.add_nodes_from(data['nodes'])
            G.add_edges_from(data['edges'])
        
        # 检查是否是邻接字典格式
        elif all(isinstance(v, (list, set, dict)) for v in data.values()):
            for node, neighbors in data.items():
                G.add_node(node)
                if isinstance(neighbors, dict):
                    for neighbor, weight in neighbors.items():
                        G.add_edge(node, neighbor, weight=weight)
                else:
                    for neighbor in neighbors:
                        G.add_edge(node, neighbor)
        
        # 其他字典格式处理
        else:
            # 尝试将键值对作为边
            for key, value in data.items():
                if isinstance(value, (list, tuple)):
                    for item in value:
                        G.add_edge(key, item)
                else:
                    G.add_edge(key, value)
    
    # 如果是列表格式
    elif isinstance(data, list):
        print("尝试从列表创建图...")
        
        # 检查是否是边列表
        if data and len(data) > 0:
            first_item = data[0]
            
            # 边列表格式 [(node1, node2), ...]
            if isinstance(first_item, (tuple, list)) and len(first_item) >= 2:
                G.add_edges_from(data)
            
            # 节点列表格式
            elif isinstance(first_item, (str, int, float)):
                G.add_nodes_from(data)
            
            # 复杂对象列表
            else:
                for i, item in enumerate(data):
                    G.add_node(i, data=item)
                    # 尝试连接相邻项
                    if i > 0:
                        G.add_edge(i-1, i)
    
    # 如果是numpy数组
    elif isinstance(data, np.ndarray):
        print("尝试从numpy数组创建图...")
        
        # 如果是2D数组，假设是邻接矩阵
        if data.ndim == 2 and data.shape[0] == data.shape[1]:
            G = nx.from_numpy_array(data)
        
        # 如果是1D数组，创建路径图
        elif data.ndim == 1:
            G = nx.path_graph(len(data))
            for i, value in enumerate(data):
                G.nodes[i]['value'] = value
    
    # pandas DataFrame
    elif isinstance(data, pd.DataFrame):
        print("尝试从DataFrame创建图...")
        
        # 如果有source和target列
        if 'source' in data.columns and 'target' in data.columns:
            edges = [(row['source'], row['target']) for _, row in data.iterrows()]
            G.add_edges_from(edges)
        
        # 如果是方阵，作为邻接矩阵
        elif data.shape[0] == data.shape[1]:
            G = nx.from_pandas_adjacency(data)
        
        # 其他情况，使用索引作为节点
        else:
            for idx, row in data.iterrows():
                G.add_node(idx)
                for col in data.columns:
                    if pd.notna(row[col]):
                        G.add_edge(idx, f"{col}_{row[col]}")
    
    print(f"创建的图: {G.number_of_nodes()}个节点, {G.number_of_edges()}条边")
    return G

def visualize_graph(G: nx.Graph, title: str = "网络图可视化", 
                   output_file: str = None, figsize: Tuple[int, int] = (12, 8)) -> None:
    """可视化NetworkX图"""
    
    if G.number_of_nodes() == 0:
        print("图中没有节点，无法可视化")
        return
    
    plt.figure(figsize=figsize)
    
    # 选择布局算法
    if G.number_of_nodes() < 50:
        pos = nx.spring_layout(G, k=1, iterations=50)
    elif G.number_of_nodes() < 200:
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.random_layout(G)
    
    # 计算节点大小（基于度数）
    degrees = dict(G.degree())
    node_sizes = [max(100, degrees[node] * 50) for node in G.nodes()]
    
    # 绘制图
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                          node_color='lightblue', alpha=0.7)
    nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray')
    
    # 添加标签（如果节点不太多）
    if G.number_of_nodes() <= 50:
        labels = {node: str(node)[:10] for node in G.nodes()}  # 限制标签长度
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    # 显示图的统计信息
    info_text = f"节点数: {G.number_of_nodes()}\n边数: {G.number_of_edges()}"
    if G.number_of_nodes() > 0:
        avg_degree = sum(degrees.values()) / len(degrees)
        info_text += f"\n平均度数: {avg_degree:.2f}"
    
    plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"图像已保存到: {output_file}")
    
    plt.show()

def generate_graph_statistics(G: nx.Graph) -> Dict[str, Any]:
    """生成图的统计信息"""
    if G.number_of_nodes() == 0:
        return {"error": "图中没有节点"}
    
    stats = {
        "节点数": G.number_of_nodes(),
        "边数": G.number_of_edges(),
        "是否连通": nx.is_connected(G),
        "连通分量数": nx.number_connected_components(G),
    }
    
    if G.number_of_nodes() > 0:
        degrees = dict(G.degree())
        stats.update({
            "平均度数": sum(degrees.values()) / len(degrees),
            "最大度数": max(degrees.values()),
            "最小度数": min(degrees.values()),
        })
        
        if nx.is_connected(G):
            stats["直径"] = nx.diameter(G)
            stats["平均路径长度"] = nx.average_shortest_path_length(G)
    
    return stats

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) > 1:
        pkl_file = sys.argv[1]
    else:
        pkl_file = "mri_artifacts_without_concept.pkl"
    
    # 检查文件是否存在
    if not Path(pkl_file).exists():
        print(f"文件不存在: {pkl_file}")
        print("请确保文件在当前目录中，或提供正确的文件路径")
        print("使用方法: python visualize_pkl_networkx.py <pkl_file_path>")
        return
    
    print(f"开始处理文件: {pkl_file}")
    
    # 加载数据
    data = load_pickle_file(pkl_file)
    if data is None:
        return
    
    # 分析数据结构
    analyze_data_structure(data)
    
    # 创建图
    print("\n" + "="*50)
    print("创建NetworkX图")
    print("="*50)
    
    G = create_graph_from_data(data)
    
    # 生成统计信息
    print("\n" + "="*50)
    print("图统计信息")
    print("="*50)
    
    stats = generate_graph_statistics(G)
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # 可视化
    print("\n" + "="*50)
    print("生成可视化")
    print("="*50)
    
    output_file = pkl_file.replace('.pkl', '_network_visualization.png')
    visualize_graph(G, title=f"MRI Artifacts Network - {Path(pkl_file).name}", 
                   output_file=output_file)
    
    print(f"\n✓ 可视化完成！图像保存为: {output_file}")

if __name__ == "__main__":
    main()