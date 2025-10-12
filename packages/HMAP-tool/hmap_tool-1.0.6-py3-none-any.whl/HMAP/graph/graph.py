import numpy as np
import scipy.sparse as sp
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm
from scipy.sparse.csgraph import connected_components

import scanpy as sc

import warnings
from typing import Literal


def compute_metacell_diffusion_kernel(X, A, n_neighbors=50, sigma=1.0, diffusion_time=1.0):
    """
    计算元细胞之间的扩散核相似度
    
    参数:
        X: 细胞embedding矩阵, shape=(n_cells, n_features)
        A: 细胞-元细胞相似度矩阵, shape=(n_cells, n_metacells), 每行和为1
        n_neighbors: KNN近邻数
        sigma: 高斯核带宽
        diffusion_time: 扩散时间参数
        
    返回:
        K_meta: 元细胞扩散核相似度矩阵, shape=(n_metacells, n_metacells)
    """
    # 转换为稀疏矩阵以节省内存
    A = csr_matrix(A)
    n_cells, n_metacells = A.shape
    
    print(f"Processing {n_cells} cells and {n_metacells} metacells...")
    
    # 步骤1: 构建细胞的KNN图 (使用近似方法处理大规模数据)
    print("Building KNN graph for cells...")
    ad = sc.AnnData(X)
    sc.pp.neighbors(ad, use_rep='X', n_neighbors=n_neighbors)
    distances = ad.obsp['distances']
    
    W_cells = -distances.power(2) / (2 * sigma**2)
    W_cells.data = np.exp(W_cells.data)
    
    # 对称化
    W_cells = (W_cells + W_cells.T) / 2
    
    # 步骤2: 构建细胞层的扩散算子
    print("Constructing cell diffusion operator...")
    # 计算度矩阵
    D_cells = sp.diags(W_cells.sum(axis=1).A1)
    
    # 归一化转移矩阵 (行归一化)
    P_cells = D_cells.power(-1) @ W_cells
    
    # 步骤3: 构建元细胞层的扩散核
    print("Computing metacell diffusion kernel...")
    # 通过细胞层传播到元细胞层
    #if X.shape[0]<10000:
    #    I = sp.identity(P_cells.shape[0], format='csr')
    #    K_meta = A.T @ (expm(-diffusion_time * (I - P_cells))) @ A
    #else:
    if True:
        # 更高效的计算方式: 使用矩阵级数展开近似
        # 因为直接计算矩阵指数对于大规模数据不可行
        # 使用迭代方法近似计算扩散核
        K_meta = approximate_diffusion_kernel(A.T, P_cells, diffusion_time)
    
    # 确保对称性
    K_meta = (K_meta + K_meta.T) / 2
    
    return K_meta.toarray()

def approximate_diffusion_kernel(AT, P, t, n_terms=10):
    """
    近似计算扩散核: exp(-t*(I-P)) ≈ sum_{k=0}^n [(-t)^k/k!] (I-P)^k
    
    使用稀疏矩阵乘法高效计算
    """
    n = P.shape[0]
    I = sp.identity(n, format='csr')
    L = I - P  # 随机游走拉普拉斯
    
    result = AT @ AT.T  # 初始化为单位矩阵的近似
    term = AT.copy()
    
    for k in range(1, n_terms+1):
        term = term @ L
        coeff = ((-t)**k) / np.math.factorial(k)
        result += coeff * (AT @ term.T)
    
    return result

def sparse_row_normalize(mat):
    """行归一化稀疏矩阵"""
    row_sums = np.array(mat.sum(axis=1)).flatten()
    row_indices, col_indices = mat.nonzero()
    normalized_data = mat.data / row_sums[row_indices]
    return csr_matrix((normalized_data, (row_indices, col_indices)), shape=mat.shape)

# 示例用法
#if __name__ == "__main__":
#    # 生成模拟数据
#    n_cells = 100000  # 10万细胞
#    n_features = 50
#    n_metacells = 100
#    
#    print("Generating synthetic data...")
#    X = np.random.randn(n_cells, n_features)  # 细胞embedding
#    A = np.random.rand(n_cells, n_metacells)  # 细胞-元细胞相似度
#    A = A / A.sum(axis=1, keepdims=True)  # 行归一化
#    
#    # 转换为稀疏矩阵
#    A = csr_matrix(A)
#    
#    # 计算元细胞扩散核
#    K_meta = compute_metacell_diffusion_kernel(
#        X, A, 
#        n_neighbors=30, 
#        sigma=1.0, 
#        diffusion_time=1.0
#    )
#    
#    print("Metacell diffusion kernel shape:", K_meta.shape)
#    print("Done!")




def compute_pseudotime(K_meta, root_metacell=None):
    """
    基于K_meta计算元细胞的pseudotime
    
    参数:
        K_meta: 元细胞相似度矩阵 (n_metacells x n_metacells)
        root_metacell: 伪时间起点的元细胞索引
        
    返回:
        pseudotime: 每个元细胞的伪时间值
    """  
    # 转换为距离矩阵 (相似度越高，距离越小)
    np.fill_diagonal(K_meta, 1)
    D = 1 - K_meta
    D = np.maximum(D, 0)
    np.fill_diagonal(D, 0)  # 对角线距离设为0
    
    # 检查连通性
    n_components, labels = connected_components(D, directed=False)
    if n_components > 1:
        warnings.warn(f"Graph has {n_components} connected components. Using largest component.")
        D = largest_component(D, labels)
    
    # 自动选择根节点 (距离矩阵中最边缘的点)
    if root_metacell is None:
        root_metacell = select_root_metacell(D)
        print(f"Automatically selected root metacell: {root_metacell}")
    
    ad = sc.AnnData(K_meta)
    ad.uns['iroot'] = root_metacell
    
    sc.pp.neighbors(ad, method='gauss')
    sc.tl.diffmap(ad)
    sc.tl.dpt(ad)
    
    return ad.obs['dpt_pseudotime']

def largest_component(D, labels):
    """提取最大连通分量"""
    unique, counts = np.unique(labels, return_counts=True)
    largest_label = unique[np.argmax(counts)]
    mask = labels == largest_label
    return D[mask][:, mask]

def select_root_metacell(D):
    """选择距离矩阵中最边缘的点作为根节点"""
    eccentricity = np.max(D, axis=1)
    root = np.argmax(eccentricity)
    return root



# 示例用法
#if __name__ == "__main__":
#    # 创建模拟的K_meta矩阵 (链式结构)
#    n_metacells = 50
#    K_meta = np.zeros((n_metacells, n_metacells))
#    
#    # 创建链式相似度 (模拟轨迹)
#    for i in range(n_metacells):
#        for j in range(n_metacells):
#            K_meta[i, j] = np.exp(-abs(i-j)/5)
#    
#    # 计算伪时间
#    pseudotime = compute_pseudotime(
#        K_meta, 
#        method='diffusion',  # 可选 'shortest_path'
#      
#    )
#    
#    
#    print("Pseudotime values:", pseudotime)


import igraph as ig
from fa2_modified import ForceAtlas2
import matplotlib.pyplot as plt

def create_metacell_igraph(K_meta, threshold=0.1):
    """
    从K_meta矩阵创建igraph图对象
    
    参数:
        K_meta: 元细胞扩散核相似度矩阵
        threshold: 相似度阈值，低于此值的边将被过滤
        
    返回:
        G: igraph图对象
    """   
    # 获取上三角矩阵并应用阈值
    n = K_meta.shape[0]
    sources, targets = np.where(np.triu(K_meta) > threshold)
    weights = K_meta[sources, targets]
    
    # 创建igraph图
    G = ig.Graph()
    G.add_vertices(n)
    G.add_edges(zip(sources, targets))
    G.es['weight'] = weights
    
    return G

def visualize_metacell_igraph_with_fa2(G, init_pos=None, iterations=100,
                                       outboundAttractionDistribution=True,
                                       linLogMode=False,
                                       adjustSizes=False,
                                       edgeWeightInfluence=1.0,
                                       jitterTolerance=1.0,
                                       barnesHutOptimize=True,
                                       barnesHutTheta=1.2,
                                       scalingRatio=2.0,
                                       strongGravityMode=False,
                                       gravity=1.0,
                                       verbose=True):
    """
    使用ForceAtlas2算法可视化igraph网络
    
    参数:
        G: igraph图对象
        iterations: FA2迭代次数
    """
    np.random.seed(42)
        
    # 初始化ForceAtlas2
    forceatlas2 = ForceAtlas2(
        outboundAttractionDistribution=outboundAttractionDistribution,
        linLogMode=linLogMode,
        adjustSizes=adjustSizes,
        edgeWeightInfluence=edgeWeightInfluence,
        jitterTolerance=jitterTolerance,
        barnesHutOptimize=barnesHutOptimize,
        barnesHutTheta=barnesHutTheta,
        scalingRatio=scalingRatio,
        strongGravityMode=strongGravityMode,
        gravity=gravity,
        verbose=verbose
    )
    
    # 获取边权重
    #edge_weights = G.es['weight'] if 'weight' in G.es.attributes() else None
    
    # 运行布局算法
    positions = forceatlas2.forceatlas2_igraph_layout(
        G, weight_attr='weight', iterations=iterations, pos=init_pos
    )
    
    # 转换为可视化的坐标
    layout = [[pos[0], pos[1]] for pos in positions]
    
    # 可视化
    #fig, ax = plt.subplots(figsize=(12, 12))
    
    # 绘制网络
    #ig.plot(
    #    G,
    #    target=ax,
    #    layout=layout,
    #    vertex_size=10,
    #    vertex_color='skyblue',
    #    edge_width=edge_weights * 2,
    #    edge_color='gray',
    #    edge_alpha=0.3
    #)
    #
    #plt.title('Metacell Network with ForceAtlas2 Layout (igraph)')
    #plt.axis('off')
    #plt.tight_layout()
    #plt.show()
    
    return np.array(layout)

# 示例用法
#if __name__ == "__main__":
#    # 创建模拟的K_meta矩阵用于演示
#    n_metacells = 100
#    K_meta = np.random.rand(n_metacells, n_metacells)
#    K_meta = (K_meta + K_meta.T) / 2  # 对称化
#    np.fill_diagonal(K_meta, 1)  # 对角线设为1
#    
#    # 创建igraph图
#    G = create_igraph(K_meta, threshold=0.3)
#    
#    print(f"Created graph with {G.vcount()} vertices and {G.ecount()} edges")
#    
#    # 使用FA2可视化
#    layout = visualize_igraph_with_fa2(G, iterations=100)


def clustering(K_meta, resolution=1, method: Literal['louvain','leiden']='leiden'):
    ad = sc.AnnData(K_meta)
    
    if method == 'louvain':
        sc.tl.louvain(ad, adjacency=K_meta, resolution=resolution, directed=False, use_weights=True)
        return ad.obs['louvain'].tolist()
    else:
        sc.tl.leiden(ad, adjacency=K_meta, resolution=resolution, directed=False, use_weights=True)
        return ad.obs['leiden'].tolist()