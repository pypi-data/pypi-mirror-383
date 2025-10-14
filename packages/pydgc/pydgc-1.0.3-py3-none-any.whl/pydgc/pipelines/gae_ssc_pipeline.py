# -*- coding: utf-8 -*-
from . import BasePipeline
from ..models import GAESSC
from argparse import Namespace
from ..utils import perturb_data
from torch_geometric.utils import add_remaining_self_loops


class GAESSCPipeline(BasePipeline):
    """GAE-SSC pipeline.

    Args:
        args (Namespace): Arguments.
    """
    def __init__(self, args: Namespace):
        super().__init__(args)

    def augment_data(self):
        """Data augmentation"""
        self.data = perturb_data(self.data, self.cfg.dataset.augmentation)
        if hasattr(self.cfg.dataset.augmentation, 'add_self_loops'):
            if self.cfg.dataset.augmentation.add_self_loops:
                edge_index, _ = add_remaining_self_loops(self.data.edge_index, num_nodes=self.data.num_nodes)
                self.data.edge_index = edge_index

    def build_model(self):
        model = GAESSC(self.logger, self.cfg)
        self.logger.model_info(model)
        return model
