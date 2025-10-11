# HMAP: Hierarchical Manifold Approximation and Projection

HMAP develop a hierarchical deep generative topographic mapping algorithm to realize the recovery of both **global and local** manifolds underlying the given data.


<div align="center">
    <img src="./img/figure1.png" alt="" width="60%">
</div>

## Example
[HERE](./example)

## Metacell calling
HMAP also provides the supervised mode, allowing the computation of global and local embeddings under the supervision of given metacells. 

## Installation
1. Download HMAP and enter the directory
```bash
git clone https://github.com/ZengFLab/HMAP.git && cd HMAP
```

2. Create a virtual environment and activate it
```bash
conda create -n HMAP python=3.10 && conda activate HMAP
```

3. Install [PyTorch](https://pytorch.org/get-started/locally/) following the official instruction. 
```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

4. Install HMAP
```bash
pip install HMAP-tool
```