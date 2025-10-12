# HMAP: Hierarchical Manifold Approximation and Projection

HMAP develop a hierarchical deep generative topographic mapping algorithm to realize the recovery of both **global and local** manifolds underlying single-cell data.


<div align="center">
    <img src="./img/figure1.png" alt="" width="60%">
</div>


## Installation
1. Create a virtual environment and activate it
```bash
conda create -n HMAP python=3.10 scipy numpy pandas scikit-learn && conda activate HMAP
```

2. Install [PyTorch](https://pytorch.org/get-started/locally/) following the official instruction. 
```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

3. Install HMAP
```bash
pip install HMAP-tool
```