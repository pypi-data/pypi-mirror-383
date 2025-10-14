# -*- coding: utf-8 -*-
import torch

from ..models import DAEGC
from . import BasePipeline
from argparse import Namespace
from ..utils import get_M, perturb_data
from sklearn.preprocessing import normalize
from torch_geometric.utils import to_dense_adj, add_remaining_self_loops


class DAEGCPipeline(BasePipeline):
    """DAEGC pipeline.

    Args:
        args (Namespace): Arguments.
    """
    def __init__(self, args: Namespace):
        super().__init__(args)

    def augment_data(self):
        self.data = perturb_data(self.data, self.cfg.dataset.augmentation)
        if hasattr(self.cfg.dataset.augmentation, 'add_self_loops'):
            if self.cfg.dataset.augmentation.add_self_loops:
                edge_index, _ = add_remaining_self_loops(self.data.edge_index, num_nodes=self.data.num_nodes)
                self.data.edge_index = edge_index
        if hasattr(self.cfg.dataset.augmentation, 'dense_adj'):
            if self.cfg.dataset.augmentation.dense_adj:
                adj = to_dense_adj(self.data.edge_index)[0]
                self.data.adj = torch.from_numpy(normalize(adj.numpy(), norm="l1"))
        if hasattr(self.cfg.dataset.augmentation, 't'):
            if int(self.cfg.dataset.augmentation.t) > 0:
                self.data.M = get_M(self.data.adj, t=int(self.cfg.dataset.augmentation.t))

        self.data.adj_label = to_dense_adj(self.data.edge_index)[0]

    def build_model(self):
        model = DAEGC(self.logger, self.cfg)
        self.logger.model_info(model)
        return model
