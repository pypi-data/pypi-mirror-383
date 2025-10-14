# -*- coding: utf-8 -*-
from torch_geometric.utils import add_self_loops

from ..models import DGCLUSTER
from . import BasePipeline
from argparse import Namespace
from ..utils import perturb_data
import numpy as np
import scipy.sparse as sp
import torch.nn.functional as F
import torch


class DGCLUSTERPipeline(BasePipeline):
    """DGCLUSTER pipeline.

    Args:
        args (Namespace): Arguments.
    """
    def __init__(self, args: Namespace):
        super().__init__(args)

    def augment_data(self):
        self.data = perturb_data(self.data, self.cfg.dataset.augmentation)
        if self.dataset_name == "DBLP":
            self.data.edge_index = add_self_loops(self.data.edge_index)[0]
        # transform = T.NormalizeFeatures()
        num_nodes = self.data.x.shape[0]
        num_edges = (self.data.edge_index.shape[1])
        labels = self.data.y.flatten()
        if not isinstance(labels, torch.Tensor):
            labels = torch.from_numpy(labels).long()
        else:
            if labels.dtype != torch.long:
                labels = labels.long()
        oh_labels = F.one_hot(labels, num_classes=max(labels) + 1)
        sparse_adj = sp.csr_matrix((np.ones(num_edges), self.data.edge_index.cpu().numpy()),
                                   shape=(num_nodes, num_nodes))
        degree = torch.tensor(sparse_adj.sum(axis=1)).squeeze().float().to(self.device)
        num_edges = int((self.data.edge_index.shape[1]) / 2)

        self.data.oh_labels = oh_labels
        self.data.sparse_adj = sparse_adj
        self.data.degree = degree
        self.cfg.dataset.num_edges = num_edges

        self.data.to(self.device)

    def build_model(self):
        model = DGCLUSTER(self.logger, self.cfg)
        self.logger.model_info(model)
        return model
