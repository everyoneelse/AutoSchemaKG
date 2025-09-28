#!/usr/bin/env python3
"""
创建示例数据文件，演示不同的数据格式
"""

import pickle
import networkx as nx
import numpy as np
import pandas as pd

def create_sample_data():
    """创建各种格式的示例数据"""
    
    # 示例1: 邻接字典格式（常见的网络数据格式）
    adjacency_dict = {
        'Node_A': ['Node_B', 'Node_C', 'Node_D'],
        'Node_B': ['Node_A', 'Node_E'],
        'Node_C': ['Node_A', 'Node_F'],
        'Node_D': ['Node_A'],
        'Node_E': ['Node_B', 'Node_F'],
        'Node_F': ['Node_C', 'Node_E']
    }
    
    # 示例2: 边列表格式
    edge_list = [
        ('Gene_1', 'Gene_2'),
        ('Gene_2', 'Gene_3'),
        ('Gene_3', 'Gene_4'),
        ('Gene_1', 'Gene_4'),
        ('Gene_2', 'Gene_5'),
        ('Gene_5', 'Gene_6')
    ]
    
    # 示例3: 带权重的网络数据
    weighted_network = {
        'nodes': ['A', 'B', 'C', 'D', 'E'],
        'edges': [
            ('A', 'B', {'weight': 0.8}),
            ('B', 'C', {'weight': 0.6}),
            ('C', 'D', {'weight': 0.9}),
            ('D', 'E', {'weight': 0.7}),
            ('E', 'A', {'weight': 0.5})
        ]
    }
    
    # 示例4: 邻接矩阵
    adjacency_matrix = np.array([
        [0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0],
        [1, 1, 0, 1, 1],
        [0, 1, 1, 0, 1],
        [0, 0, 1, 1, 0]
    ])
    
    # 保存不同格式的示例数据
    samples = {
        'sample_adjacency_dict.pkl': adjacency_dict,
        'sample_edge_list.pkl': edge_list,
        'sample_weighted_network.pkl': weighted_network,
        'sample_adjacency_matrix.pkl': adjacency_matrix
    }
    
    for filename, data in samples.items():
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
        print(f"创建示例文件: {filename}")

if __name__ == "__main__":
    create_sample_data()