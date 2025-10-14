import pyro
import pyro.distributions as dist
from pyro.optim import ExponentialLR
from pyro.infer import SVI, JitTraceEnum_ELBO, TraceEnum_ELBO, config_enumerate

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.distributions.utils import logits_to_probs, probs_to_logits, clamp_probs
from torch.distributions import constraints
from torch.distributions.transforms import SoftmaxTransform

import argparse
import os
import time as tm
import random 
import pandas as pd
import numpy as np
import datatable as dt
import networkx as nx
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

from SURE.utils import convert_to_tensor, tensor_to_numpy, CustomDataset, CustomDataset2
from .utils.custom_mlp import MLP, Exp

from tqdm import tqdm
from typing import Literal
import dill as pickle
import gzip

class HMAP(nn.Module):
    def __init__(self,
                 input_size: int = 2000,
                 undesired_size: int = 2,
                 codebook_size: int = 30,   # size of metacell codebook
                 codebook_size2: int = 100,
                 d_dim: int = 2,            # dimension of a metacell variable
                 d_dist: Literal['normal','laplacian','caucy','studentt','vonmises','gumbel'] = 'normal',
                 z_dim: int = 10,
                 z_dist: Literal['normal','laplacian','cauchy','studentt','gumbel'] = 'studentt',
                 hidden_layers: list =[500],
                 hidden_layer_activation: Literal['relu','softplus','leakyrelu','linear'] = 'relu',
                 use_dirichlet: bool = True,
                 dirichlet_mass: float = 1.0,
                 loss_func: Literal['negbinomial','poisson','multinomial','gaussian'] = 'multinomial',
                 inverse_dispersion: float = 10.0,
                 nn_dropout: float = 0.1,
                 zero_inflation: Literal['exact','inexact','none'] = 'exact',
                 gate_prior: float = 0.6,
                 delta: float = 0.5,
                 post_layer_fct: list = ['layernorm'],
                 post_act_fct: list = None,
                 config_enum: str = 'parallel',
                 use_cuda: bool = False,
                 dtype = torch.float32, # type: ignore
                 ):
        super().__init__()

        # initialize the class with all arguments provided to the constructor
        self.input_size = input_size
        self.undesired_size = undesired_size
        self.inverse_dispersion = inverse_dispersion
        self.z_dim = z_dim
        self.hidden_layers = hidden_layers
        self.use_undesired = True if self.undesired_size>0 else False
        self.allow_broadcast = config_enum == 'parallel'
        self.use_cuda = use_cuda
        self.dist_model = 'dmm' if use_dirichlet else 'mm'
        self.delta = delta
        self.loss_func = loss_func
        self.dirimulti_mass = dirichlet_mass
        self.options = None
        self.code_size=codebook_size
        self.code_size2=codebook_size2
        self.D_size=d_dim
        self.z_dist = z_dist
        self.d_dist = d_dist
        self.G = None

        self.dtype = dtype

        self.use_zeroinflate=False
        self.use_exact_zeroinflate=False
        if zero_inflation=='exact':
            self.use_exact_zeroinflate=True
            self.use_zeroinflate=True
        elif zero_inflation=='inexact':
            self.use_zeroinflate=True

        if gate_prior < 1e-5:
            gate_prior = 1e-5
        elif gate_prior == 1:
            gate_prior = 1-1e-5
        self.gate_prior = np.log(gate_prior) - np.log(1-gate_prior)

        self.nn_dropout = nn_dropout
        self.post_layer_fct = post_layer_fct
        self.post_act_fct = post_act_fct
        self.hidden_layer_activation = hidden_layer_activation

        # define and instantiate the neural networks representing
        # the parameters of various distributions in the model
        self.setup_networks()

    def setup_networks(self):
        z_dim = self.z_dim
        hidden_sizes = self.hidden_layers

        nn_layer_norm, nn_batch_norm, nn_layer_dropout = False, False, False
        na_layer_norm, na_batch_norm, na_layer_dropout = False, False, False

        if self.post_layer_fct is not None:
            nn_layer_norm=True if ('layernorm' in self.post_layer_fct) or ('layer_norm' in self.post_layer_fct) else False
            nn_batch_norm=True if ('batchnorm' in self.post_layer_fct) or ('batch_norm' in self.post_layer_fct) else False
            nn_layer_dropout=True if 'dropout' in self.post_layer_fct else False

        if self.post_act_fct is not None:
            na_layer_norm=True if ('layernorm' in self.post_act_fct) or ('layer_norm' in self.post_act_fct) else False
            na_batch_norm=True if ('batchnorm' in self.post_act_fct) or ('batch_norm' in self.post_act_fct) else False
            na_layer_dropout=True if 'dropout' in self.post_act_fct else False

        if nn_layer_norm and nn_batch_norm and nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout),nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif nn_layer_norm and nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.LayerNorm(layer.module.out_features))
        elif nn_batch_norm and nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.BatchNorm1d(layer.module.out_features))
        elif nn_layer_norm and nn_batch_norm:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif nn_layer_norm:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.LayerNorm(layer.module.out_features)
        elif nn_batch_norm:
            post_layer_fct = lambda layer_ix, total_layers, layer:nn.BatchNorm1d(layer.module.out_features)
        elif nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Dropout(self.nn_dropout)
        else:
            post_layer_fct = lambda layer_ix, total_layers, layer: None

        if na_layer_norm and na_batch_norm and na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout),nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif na_layer_norm and na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.LayerNorm(layer.module.out_features))
        elif na_batch_norm and na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.BatchNorm1d(layer.module.out_features))
        elif na_layer_norm and na_batch_norm:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif na_layer_norm:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.LayerNorm(layer.module.out_features)
        elif na_batch_norm:
            post_act_fct = lambda layer_ix, total_layers, layer:nn.BatchNorm1d(layer.module.out_features)
        elif na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Dropout(self.nn_dropout)
        else:
            post_act_fct = lambda layer_ix, total_layers, layer: None

        if self.hidden_layer_activation == 'relu':
            activate_fct = nn.ReLU
        elif self.hidden_layer_activation == 'softplus':
            activate_fct = nn.Softplus
        elif self.hidden_layer_activation == 'leakyrelu':
            activate_fct = nn.LeakyReLU
        elif self.hidden_layer_activation == 'linear':
            activate_fct = nn.Identity

        # define the neural networks used later in the model and the guide.
        self.encoder_n = MLP(
            [self.D_size + self.code_size2] + hidden_sizes + [self.code_size],
            activation=activate_fct,
            output_activation=None,
            post_layer_fct=post_layer_fct,
            post_act_fct=post_act_fct,
            allow_broadcast=self.allow_broadcast,
            use_cuda=self.use_cuda,
        )

        self.encoder_n2 = MLP(
            [self.z_dim] + hidden_sizes + [self.code_size2],
            activation=activate_fct,
            output_activation=Exp,
            post_layer_fct=post_layer_fct,
            post_act_fct=post_act_fct,
            allow_broadcast=self.allow_broadcast,
            use_cuda=self.use_cuda,
        )

        self.encoder_zn = MLP(
            [self.input_size] + hidden_sizes + [[z_dim, z_dim]],
            activation=activate_fct,
            output_activation=[None, Exp],
            post_layer_fct=post_layer_fct,
            post_act_fct=post_act_fct,
            allow_broadcast=self.allow_broadcast,
            use_cuda=self.use_cuda,
        )

        self.encoder_d = MLP(
            [self.z_dim] + hidden_sizes + [[self.D_size, self.D_size]],
            activation=activate_fct,
            output_activation=[None, Exp],
            post_layer_fct=post_layer_fct,
            post_act_fct=post_act_fct,
            allow_broadcast=self.allow_broadcast,
            use_cuda=self.use_cuda,
        )

        if self.use_undesired:
            if self.loss_func in ['gaussian','lognormal']:
                self.decoder_concentrate = MLP(
                    [self.undesired_size + self.z_dim] + hidden_sizes + [[self.input_size, self.input_size]],
                    activation=activate_fct,
                    output_activation=[None, Exp],
                    post_layer_fct=post_layer_fct,
                    post_act_fct=post_act_fct,
                    allow_broadcast=self.allow_broadcast,
                    use_cuda=self.use_cuda,
                )
            else:
                self.decoder_concentrate = MLP(
                    [self.undesired_size + self.z_dim] + hidden_sizes + [self.input_size],
                    activation=activate_fct,
                    output_activation=None,
                    post_layer_fct=post_layer_fct,
                    post_act_fct=post_act_fct,
                    allow_broadcast=self.allow_broadcast,
                    use_cuda=self.use_cuda,
                )

            self.encoder_gate = MLP(
                [self.undesired_size + self.z_dim] + hidden_sizes + [[self.input_size, 1]],
                activation=activate_fct,
                output_activation=[None, Exp],
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )
        else:
            if self.loss_func in ['gaussian','lognormal']:
                self.decoder_concentrate = MLP(
                    [self.z_dim] + hidden_sizes + [[self.input_size, self.input_size]],
                    activation=activate_fct,
                    output_activation=[None, Exp],
                    post_layer_fct=post_layer_fct,
                    post_act_fct=post_act_fct,
                    allow_broadcast=self.allow_broadcast,
                    use_cuda=self.use_cuda,
                )
            else:
                self.decoder_concentrate = MLP(
                    [self.z_dim] + hidden_sizes + [self.input_size],
                    activation=activate_fct,
                    output_activation=None,
                    post_layer_fct=post_layer_fct,
                    post_act_fct=post_act_fct,
                    allow_broadcast=self.allow_broadcast,
                    use_cuda=self.use_cuda,
                )

            self.encoder_gate = MLP(
                [self.z_dim] + hidden_sizes + [[self.input_size, 1]],
                activation=activate_fct,
                output_activation=[None, Exp],
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            ) 

        if self.d_dist == 'studentt':
            self.codebook = MLP(
                [self.code_size] + hidden_sizes + [[self.D_size,self.D_size]],
                activation=activate_fct,
                output_activation=[Exp, None],
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )
        else:
            self.codebook = MLP(
                [self.code_size] + hidden_sizes + [self.D_size],
                activation=activate_fct,
                output_activation=None,
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )

        self.decoder_n2 = MLP(
            [self.D_size] + hidden_sizes + [self.code_size2],
            activation=activate_fct,
            output_activation=Exp,
            post_layer_fct=post_layer_fct,
            post_act_fct=post_act_fct,
            allow_broadcast=self.allow_broadcast,
            use_cuda=self.use_cuda,
        )

        if self.z_dist == 'studentt':
            self.codebook2 = MLP(
                [self.code_size2] + hidden_sizes + [[self.z_dim,self.z_dim]],
                activation=activate_fct,
                output_activation=[Exp,None],
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )
        else:
            self.codebook2 = MLP(
                [self.code_size2] + hidden_sizes + [self.z_dim],
                activation=activate_fct,
                output_activation=None,
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )

        # using GPUs for faster training of the networks
        if self.use_cuda:
            self.cuda()

    def cutoff(self, xs, thresh=None):
        eps = torch.finfo(xs.dtype).eps
        
        if not thresh is None:
            if eps < thresh:
                eps = thresh

        xs = xs.clamp(min=eps)

        if torch.any(torch.isnan(xs)):
            xs[torch.isnan(xs)] = eps

        return xs

    def softmax(self, xs):
        #soft_enc = nn.Softmax(dim=1)
        #xs = soft_enc(xs)
        #xs = clamp_probs(xs)
        #xs = ft.normalize(xs, 1, 1)
        xs = SoftmaxTransform()(xs)
        return xs
    
    def sigmoid(self, xs):
        sigm_enc = nn.Sigmoid()
        xs = sigm_enc(xs)
        xs = clamp_probs(xs)
        return xs

    def softmax_logit(self, xs):
        eps = torch.finfo(xs.dtype).eps
        xs = self.softmax(xs)
        xs = torch.logit(xs, eps=eps)
        return xs

    def logit(self, xs):
        eps = torch.finfo(xs.dtype).eps
        xs = torch.logit(xs, eps=eps)
        return xs

    def dirimulti_param(self, xs):
        xs = self.dirimulti_mass * self.sigmoid(xs)
        return xs

    def multi_param(self, xs):
        xs = self.softmax(xs)
        return xs
    
    def get_device(self):
        return next(self.parameters()).device

    def model(self, xs, ks2=None):
        # register this pytorch module and all of its sub-modules with pyro
        pyro.module('scc', self)

        eps = torch.finfo(xs.dtype).eps
        batch_size = xs.size(0)
        self.options = dict(dtype=xs.dtype, device=xs.device)

        total_count = pyro.param("inverse_dispersion", self.inverse_dispersion * torch.ones(1, self.input_size, **self.options),
                                 constraint=constraints.positive)
        acs_scale = pyro.param("codebook_scale", torch.ones(1, self.D_size, **self.options),
                                 constraint=constraints.positive)
        bcs_scale = pyro.param("codebook_scale2", torch.ones(1, self.z_dim, **self.options),
                                 constraint=constraints.positive)
        
        I = torch.eye(self.code_size)
        if self.d_dist == 'studentt':
            acs_dof,acs_loc = self.codebook(I)
        else:
            acs_loc = self.codebook(I)

        I2 = torch.eye(self.code_size2)
        if self.z_dist == 'studentt':
            bcs_dof,bcs_loc = self.codebook2(I2)
        else:
            bcs_loc = self.codebook2(I2)

        with pyro.plate('data'):
            ###############################################
            # p(zn)
            prior = torch.zeros(batch_size, self.code_size, **self.options)
            ns = pyro.sample('n', dist.OneHotCategorical(logits=prior))

            if self.d_dist == 'studentt':
                d_dof = torch.matmul(ns,acs_dof)
            d_loc = torch.matmul(ns,acs_loc)
            d_scale = acs_scale
            if self.d_dist == 'normal':
                ds = pyro.sample('d', dist.Normal(d_loc, d_scale).to_event(1))
            elif self.d_dist == 'laplacian':
                ds = pyro.sample('d', dist.Laplace(d_loc, d_scale).to_event(1))
            elif self.d_dist == 'cauchy':
                ds = pyro.sample('d', dist.Cauchy(d_loc, d_scale).to_event(1))
            elif self.d_dist == 'vonmises':
                ds = pyro.sample('d', dist.VonMises(d_loc, d_scale).to_event(1))
            elif self.d_dist == 'gumbel':
                ds = pyro.sample('d', dist.Gumbel(d_loc, d_scale).to_event(1))
            elif self.d_dist == 'studentt':
                ds = pyro.sample('d', dist.StudentT(df=d_dof, loc=d_loc, scale=d_scale).to_event(1))

            con2 = self.decoder_n2(ds)
            ns2 = pyro.sample('n2', dist.Dirichlet(concentration=con2))
            if self.z_dist == 'studentt':
                zn_dof = torch.matmul(ns2, bcs_dof)
                zn_loc = torch.matmul(ns2, bcs_loc)
                zn_scale = bcs_scale
            else:
                zn_loc = torch.matmul(ns2, bcs_loc)
                zn_scale = bcs_scale
            if self.z_dist == 'laplacian':
                zns = pyro.sample('zn', dist.Laplace(zn_loc, zn_scale).to_event(1))
            elif self.z_dist == 'cauchy':
                zns = pyro.sample('zn', dist.Cauchy(zn_loc, zn_scale).to_event(1))
            elif self.z_dist == 'normal':
                zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1))
            elif self.z_dist == 'studentt':
                zns = pyro.sample('zn', dist.StudentT(df=zn_dof, loc=zn_loc, scale=zn_scale).to_event(1))
            elif self.z_dist == 'gumbel':
                zns = pyro.sample('zn', dist.Gumbel(zn_loc, zn_scale).to_event(1))

            ###############################################
            # p(a | zys, zk2s)
            if self.use_undesired:
                zs = [ks2, zns]
            else:
                zs = zns

            if self.loss_func == 'gaussian':
                concentrate_loc, concentrate_scale = self.decoder_concentrate(zs)
                concentrate = concentrate_loc
            else:
                concentrate = self.decoder_concentrate(zs)

            if self.dist_model == 'dmm':
                concentrate = self.dirimulti_param(concentrate)
                theta = dist.DirichletMultinomial(total_count=1, concentration=concentrate).mean
            elif self.dist_model == 'mm':
                probs = self.multi_param(concentrate)
                theta = dist.Multinomial(total_count=1, probs=probs).mean

            # zero-inflation model
            if self.use_zeroinflate:
                gate_loc = self.gate_prior * torch.ones(batch_size, self.input_size, **self.options)
                gate_scale = torch.ones(batch_size, self.input_size, **self.options)
                gate_logits = pyro.sample('gate_logit', dist.Normal(gate_loc, gate_scale).to_event(1))
                gate_probs = self.sigmoid(gate_logits)

                if self.use_exact_zeroinflate:
                    if self.loss_func == 'multinomial':
                        theta = probs_to_logits(theta) + probs_to_logits(1-gate_probs)
                        theta = logits_to_probs(theta)
                else:
                    if self.loss_func != 'gaussian':
                        theta = probs_to_logits(theta) + probs_to_logits(1-gate_probs)
                        theta = logits_to_probs(theta)

                if self.delta > 0:
                    ones = torch.zeros(batch_size, self.input_size, **self.options)
                    ones[xs > 0] = 1
                    with pyro.poutine.scale(scale=self.delta):
                        ones = pyro.sample('one', dist.Binomial(probs=1-gate_probs).to_event(1), obs=ones)

            if self.loss_func == 'negbinomial':
                if self.use_exact_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.NegativeBinomial(total_count=total_count, probs=theta),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.NegativeBinomial(total_count=total_count, probs=theta).to_event(1), obs=xs)
            elif self.loss_func == 'poisson':
                rate = xs.sum(1).unsqueeze(-1) * theta
                rate = self.cutoff(rate)
                if self.use_exact_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Poisson(rate=rate),gate_logits=gate_logits).to_event(1), obs=xs.round())
                else:
                    pyro.sample('x', dist.Poisson(rate=rate).to_event(1), obs=xs.round())
            elif self.loss_func == 'multinomial':
                pyro.sample('x', dist.Multinomial(total_count=int(1e8), probs=theta), obs=xs)
            elif self.loss_func == 'gaussian':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Normal(concentrate_loc, concentrate_scale),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.Normal(concentrate_loc, concentrate_scale).to_event(1), obs=xs)
            elif self.loss_func == 'lognormal':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.LogNormal(concentrate_loc, concentrate_scale),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.LogNormal(concentrate_loc, concentrate_scale).to_event(1), obs=xs)

    def guide(self, xs, ks2=None):
        # inform Pyro that the variables in the batch of xs, ys are conditionally independent
        with pyro.plate('data'):
            # q(zn | x)
            zn_loc, zn_scale = self.encoder_zn(xs)
            zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1))

            con2 = self.encoder_n2(zns)
            ns2 = pyro.sample('n2', dist.Dirichlet(concentration=con2))

            d_loc,d_scale = self.encoder_d(zns)
            ds = pyro.sample('d', dist.Normal(d_loc, d_scale).to_event(1))

            alpha = self.encoder_n([ds,ns2])
            ns = pyro.sample('n', dist.OneHotCategorical(logits=alpha))
        
            ####################################
            # q(gate | xs)
            if self.use_zeroinflate:
                if self.use_undesired:
                    zs=[ks2,zns]
                else:
                    zs=zns
                loc, scale = self.encoder_gate(zs)
                scale = self.cutoff(scale)
                gates_logit = pyro.sample('gate_logit', dist.Normal(loc, scale).to_event(1))

    def _codebook(self):
        I = torch.eye(self.code_size, **self.options)
        if self.d_dist == 'studentt':
            _,loc = self.codebook(I)
        else:
            loc = self.codebook(I)
        return loc
    
    def get_codebook(self):
        I = torch.eye(self.code_size, **self.options)
        if self.d_dist == 'studentt':
            _,cb = self.codebook(I)
        else:
            cb = self.codebook(I)

        if self.z_dist == 'studentt':
            _,zs,_ = self.decoder_zn(cb)
        else:
            zs,_ = self.decoder_zn(cb)
        return tensor_to_numpy(cb), tensor_to_numpy(zs)
    
    def _code(self, xs):
        zns,_ = self.encoder_zn(xs)
        con = self.encoder_n2(zns)
        con = con / torch.sum(con, dim=1, keepdim=True)
        ds,_ = self.encoder_d(zns)
        alpha = self.encoder_n([ds,con])
        return alpha
    
    def _code2(self, xs):
        zns,_ = self.encoder_zn(xs)
        con = self.encoder_n2(zns)
        con = con / torch.sum(con, dim=1, keepdim=True)
        return con
    
    def _l1_embedding(self,xs,metacell_view=False):
        if metacell_view:
            alpha = self._soft_assignments(xs)
            acs = self._codebook()
            ds = torch.matmul(alpha,acs)
        else:
            zs = self._l2_embedding(xs)
            ds,_ = self.encoder_d(zs)
            
        return ds
    
    def _l2_embedding(self, xs):
        zns, _ = self.encoder_zn(xs)
        return zns
    
    def get_l1_embedding(self,xs,batch_size=1024,metacell_view=False):
        xs = convert_to_tensor(xs, device=self.get_device())
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                zns = self._l1_embedding(X_batch, metacell_view=metacell_view)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def get_l2_embedding(self,xs,batch_size=1024):
        xs = convert_to_tensor(xs, device=self.get_device())
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                zns = self._l2_embedding(X_batch)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def _soft_assignments(self, xs):
        alpha = self._code(xs)
        alpha = self.softmax(alpha)
        return alpha
    
    def _soft_assignments2(self, xs):
        alpha = self._code2(xs)
        return alpha
       
    def soft_assignments(self, xs, batch_size=1024):
        xs = convert_to_tensor(xs, device=self.get_device())
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                a = self._soft_assignments(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def soft_assignments2(self, xs, batch_size=1024):
        xs = convert_to_tensor(xs, device=self.get_device())
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                a = self._soft_assignments2(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def _hard_assignments(self, xs):
        alpha = self._code(xs)
        res, ind = torch.topk(alpha, 1)
        ns = torch.zeros_like(alpha).scatter_(1, ind, 1.0)
        return ns
    
    def hard_assignments(self, xs, batch_size=1024):
        xs = convert_to_tensor(xs, device=self.get_device())
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                a = self._hard_assignments(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def metacell_similarity(self, xs):
        ys = self.soft_assignments(xs)
        ys = convert_to_tensor(ys, device=self.get_device())
        m2m = torch.matmul(ys.T / torch.sum(ys.T, dim=1, keepdim=True), ys)
        m2m = tensor_to_numpy(m2m)
        return m2m
    
    def metacell_network(self, xs, k=10, exclude_metacells: list = None):
        affinity_matrix = self.metacell_similarity(xs)
        self.G = nx.Graph()
        self.G.add_nodes_from(np.arange(self.code_size))
        
        if k < affinity_matrix.shape[1]:
            for i in np.arange(self.code_size):
                arr = affinity_matrix[i,:]
                kth_largest_value = np.partition(arr, -k)[-k]
                arr[arr<kth_largest_value] = 0
                affinity_matrix[i,:] = arr

                if exclude_metacells is None:
                    for j in np.arange(len(arr)):
                        if (arr[j]>0) and (j!=i):
                            self.G.add_edge(i,j,weight=1/arr[j])
                elif not (i in exclude_metacells):
                    for j in np.arange(len(arr)):
                        if (arr[j]>0) and (j!=i) and (not j in exclude_metacells):
                            self.G.add_edge(i,j,weight=1/arr[j])
            
        return self.G
    
    def metacell_tree(self, G, root_metacell=0):
        T = nx.minimum_spanning_tree(G)
        sorted(T.edges(data=True))
        tree = nx.dfs_tree(T, root_metacell)

        return tree
    
    def fit(self, xs, 
            us = None, 
            num_epochs: int = 200, 
            learning_rate: float = 0.0001, 
            batch_size: int = 512, 
            algo: Literal['adam','rmsprop','adamw'] = 'adam', 
            beta_1: float = 0.9, 
            weight_decay: float = 0.005, 
            decay_rate: float = 0.9,
            config_enum: str = 'parallel',
            use_jax: bool = False):
        """
        Train the SURE model.

        Parameters
        ----------
        xs
            Single-cell experssion matrix. It should be a Numpy array or a Pytorch Tensor. Rows are cells and columns are features.
        us
            Undesired factor matrix. It should be a Numpy array or a Pytorch Tensor. Rows are cells and columns are undesired factors.
        num_epochs
            Number of training epochs.
        learning_rate
            Parameter for training.
        batch_size
            Size of batch processing.
        algo
            Optimization algorithm.
        beta_1
            Parameter for optimization.
        weight_decay
            Parameter for optimization.
        decay_rate 
            Parameter for optimization.
        use_jax
            If toggled on, Jax will be used for speeding up. CAUTION: This will raise errors because of unknown reasons when it is called in
            the Python script or Jupyter notebook. It is OK if it is used when runing SURE in the shell command.
        """
        
        xs = convert_to_tensor(xs, dtype=self.dtype, device=self.get_device())
        if us is not None:
            us = convert_to_tensor(us, dtype=self.dtype, device=self.get_device())

        dataset = CustomDataset2(xs, us)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # setup the optimizer
        optim_params = {'lr': learning_rate, 'betas': (beta_1, 0.999), 'weight_decay': weight_decay}

        if algo.lower()=='rmsprop':
            optimizer = torch.optim.RMSprop
        elif algo.lower()=='adam':
            optimizer = torch.optim.Adam
        elif algo.lower() == 'adamw':
            optimizer = torch.optim.AdamW
        else:
            raise ValueError("An optimization algorithm must be specified.")
        scheduler = ExponentialLR({'optimizer': optimizer, 'optim_args': optim_params, 'gamma': decay_rate})

        pyro.clear_param_store()

        # set up the loss(es) for inference, wrapping the guide in config_enumerate builds the loss as a sum
        # by enumerating each class label form the sampled discrete categorical distribution in the model
        Elbo = JitTraceEnum_ELBO if use_jax else TraceEnum_ELBO
        elbo = Elbo(max_plate_nesting=1, strict_enumeration_warning=False)
        guide = config_enumerate(self.guide, config_enum, expand=True)
        loss_basic = SVI(self.model, guide, scheduler, loss=elbo)

        # build a list of all losses considered
        losses = [loss_basic]
        num_losses = len(losses)

        with tqdm(total=num_epochs, desc='Training', unit='epoch') as pbar:
            for epoch in range(num_epochs):
                epoch_losses = [0.0] * num_losses
                for batch_x, batch_u, _ in dataloader:
                    if us is None:
                        batch_u = None

                    for loss_id in range(num_losses):
                        new_loss = losses[loss_id].step(batch_x, batch_u)
                        epoch_losses[loss_id] += new_loss

                avg_epoch_losses_ = map(lambda v: v / len(dataloader), epoch_losses)
                avg_epoch_losses = map(lambda v: "{:.4f}".format(v), avg_epoch_losses_)

                # store the loss
                str_loss = " ".join(map(str, avg_epoch_losses))

                # Update progress bar
                pbar.set_postfix({'loss': str_loss})
                pbar.update(1)
        
        assigns = self.soft_assignments(xs)
        assigns = convert_to_tensor(assigns, dtype=self.dtype, device=self.get_device())
        self.codebook_weights = torch.sum(assigns, dim=0)
        self.codebook_weights = self.codebook_weights / torch.sum(self.codebook_weights)

    @classmethod
    def save_model(cls, model, file_path, compression=False):
        """Save the model to the specified file path."""
        file_path = os.path.abspath(file_path)

        model.eval()
        if compression:
            with gzip.open(file_path, 'wb') as pickle_file:
                pickle.dump(model, pickle_file)
        else:
            with open(file_path, 'wb') as pickle_file:
                pickle.dump(model, pickle_file)

        print(f'Model saved to {file_path}')

    @classmethod
    def load_model(cls, file_path):
        """Load the model from the specified file path and return an instance."""
        print(f'Model loaded from {file_path}')

        file_path = os.path.abspath(file_path)
        if file_path.endswith('gz'):
            with gzip.open(file_path, 'rb') as pickle_file:
                model = pickle.load(pickle_file)
        else:
            with open(file_path, 'rb') as pickle_file:
                model = pickle.load(pickle_file)
        
        return model


EXAMPLE_RUN = (
    "example run: HMAP --help"
)

def parse_args():
    parser = argparse.ArgumentParser(
        description="HMAP\n{}".format(EXAMPLE_RUN))

    parser.add_argument(
        "--cuda", action="store_true", help="use GPU(s) to speed up training"
    )
    parser.add_argument(
        "--jit", action="store_true", help="use PyTorch jit to speed up training"
    )
    parser.add_argument(
        "-n", "--num-epochs", default=200, type=int, help="number of epochs to run"
    )
    parser.add_argument(
        "-enum",
        "--enum-discrete",
        default="parallel",
        help="parallel, sequential or none. uses parallel enumeration by default",
    )
    parser.add_argument(
        "-data",
        "--data-file",
        default=None,
        type=str,
        help="the data file",
    )
    parser.add_argument(
        "-undesired",
        "--undesired-factor-file",
        default=None,
        type=str,
        help="the file for the record of undesired factors",
    )
    parser.add_argument(
        "-delta",
        "--delta",
        default=0.0,
        type=float,
        help="penalty weight for zero inflation loss",
    )
    parser.add_argument(
        "-64",
        "--float64",
        action="store_true",
        help="use double float precision",
    )
    parser.add_argument(
        "--z-dist",
        default='studentt',
        type=str,
        choices=['normal','laplacian','cauchy','studentt','gumbel'],
        help="distribution model for latent representation",
    )
    parser.add_argument(
        "-zd",
        "--z-dim",
        default=10,
        type=int,
        help="size of the tensor representing the latent variable z",
    )
    parser.add_argument(
        "-cs",
        "--codebook_size",
        default=30,
        type=int,
        help="size of vector quantization codebook",
    )
    parser.add_argument(
        "-dd",
        "--d-dim",
        default=2,
        type=int,
        choices=[2,3],
        help="size of the vector quantization codeword",
    )
    parser.add_argument(
        "--d-dist",
        default='normal',
        type=str,
        choices=['normal','laplacian','cauchy','vonmises','gumbel','studentt'],
        help="distribution model for visual representation",
    )
    parser.add_argument(
        "-hl",
        "--hidden-layers",
        nargs="+",
        default=[500],
        type=int,
        help="a tuple (or list) of MLP layers to be used in the neural networks "
        "representing the parameters of the distributions in our model",
    )
    parser.add_argument(
        "-hla",
        "--hidden-layer-activation",
        default='relu',
        type=str,
        choices=['relu','softplus','leakyrelu','linear'],
        help="activation function for hidden layers",
    )
    parser.add_argument(
        "-plf",
        "--post-layer-function",
        nargs="+",
        default=['layernorm'],
        type=str,
        help="post functions for hidden layers, could be none, dropout, layernorm, batchnorm, or combination, default is 'dropout layernorm'",
    )
    parser.add_argument(
        "-paf",
        "--post-activation-function",
        nargs="+",
        default=['none'],
        type=str,
        help="post functions for activation layers, could be none or dropout, default is 'none'",
    )
    parser.add_argument(
        "-id",
        "--inverse-dispersion",
        default=10.0,
        type=float,
        help="inverse dispersion prior for negative binomial",
    )
    parser.add_argument(
        "-lr",
        "--learning-rate",
        default=0.0001,
        type=float,
        help="learning rate for Adam optimizer",
    )
    parser.add_argument(
        "-dr",
        "--decay-rate",
        default=0.9,
        type=float,
        help="decay rate for Adam optimizer",
    )
    parser.add_argument(
        "--layer-dropout-rate",
        default=0.1,
        type=float,
        help="droput rate for neural networks",
    )
    parser.add_argument(
        "-b1",
        "--beta-1",
        default=0.95,
        type=float,
        help="beta-1 parameter for Adam optimizer",
    )
    parser.add_argument(
        "-bs",
        "--batch-size",
        default=1000,
        type=int,
        help="number of cells to be considered in a batch",
    )
    parser.add_argument(
        "-gp",
        "--gate-prior",
        default=0.6,
        type=float,
        help="gate prior for zero-inflated model",
    )
    parser.add_argument(
        "-likeli",
        "--likelihood",
        default='negbinomial',
        type=str,
        choices=['negbinomial', 'multinomial', 'poisson', 'gaussian','lognormal'],
        help="specify the distribution likelihood function",
    )
    parser.add_argument(
        "-dirichlet",
        "--use-dirichlet",
        action="store_true",
        help="use Dirichlet distribution over gene frequency",
    )
    parser.add_argument(
        "-mass",
        "--dirichlet-mass",
        default=1,
        type=float,
        help="mass param for dirichlet model",
    )
    parser.add_argument(
        "-zi",
        "--zero-inflation",
        default='exact',
        type=str,
        choices=['none','exact','inexact'],
        help="use zero-inflated estimation",
    )
    parser.add_argument(
        "--seed",
        default=None,
        type=int,
        help="seed for controlling randomness in this example",
    )
    parser.add_argument(
        "--save-model",
        default=None,
        type=str,
        help="path to save model for prediction",
    )
    args = parser.parse_args()

    return args

def set_random_seed(seed):
    # Set seed for PyTorch
    torch.manual_seed(seed)
    
    # If using CUDA, set the seed for CUDA
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)  # For multi-GPU setups.
    
    # Set seed for NumPy
    np.random.seed(seed)
    
    # Set seed for Python's random module
    random.seed(seed)

    # Set seed for Pyro
    pyro.set_rng_seed(seed)


def main():
    args = parse_args()

    assert (
        (args.data_file is not None) and (
            os.path.exists(args.data_file))
    ), "data file must be provided"

    if args.seed is not None:
        set_random_seed(args.seed)

    if args.float64:
        dtype = torch.float64
        torch.set_default_dtype(torch.float64)
    else:
        dtype = torch.float32
        torch.set_default_dtype(torch.float32)

    xs = dt.fread(file=args.data_file, header=True).to_numpy()
    us = None 
    if args.undesired_factor_file is not None:
        us = dt.fread(file=args.undesired_factor_file, header=True).to_numpy()

    input_size = xs.shape[1]
    undesired_size = 0 if us is None else us.shape[1]

    z_dist = args.z_dist
    d_dist = args.d_dist

    # batch_size: number of cells (and labels) to be considered in a batch
    hmap = HMAP(
        input_size=input_size,
        undesired_size=undesired_size,
        codebook_size=args.codebook_size,
        d_dim=args.d_dim,
        d_dist=d_dist,
        z_dim=args.z_dim,
        z_dist=z_dist,
        hidden_layers=args.hidden_layers,
        hidden_layer_activation=args.hidden_layer_activation,
        use_dirichlet=args.use_dirichlet,
        dirichlet_mass=args.dirichlet_mass,
        loss_func=args.likelihood,
        inverse_dispersion=args.inverse_dispersion,
        nn_dropout=args.layer_dropout_rate,
        zero_inflation=args.zero_inflation,
        gate_prior=args.gate_prior,
        delta=args.delta,
        use_cuda=args.cuda,
        config_enum=args.enum_discrete,
        post_layer_fct=args.post_layer_function,
        post_act_fct=args.post_activation_function,
        dtype=dtype,
    )

    hmap.fit(xs, us, 
             num_epochs=args.num_epochs,
             learning_rate=args.learning_rate,
             batch_size=args.batch_size,
             beta_1=args.beta_1,
             decay_rate=args.decay_rate,
             use_jax=args.jit,
             config_enum=args.enum_discrete,
             )

    if args.save_model is not None:
        HMAP.save_model(hmap, args.save_model)


if __name__ == "__main__":
    main()
