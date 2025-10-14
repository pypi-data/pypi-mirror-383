# -*- coding: utf-8 -*-
import torch
from torch_sparse import SparseTensor

from ..models import MAGIBatch
from . import BasePipeline
from argparse import Namespace
from ..utils import perturb_data


def get_sim(batch, adj, wt=20, wl=3):
    """Get similarity matrix.

    Args:
        batch (torch.Tensor): Batch indices.
        adj (SparseTensor): Adjacency matrix.
        wt (int, optional): Number of random walks. Defaults to 20.
        wl (int, optional): Length of random walks. Defaults to 3.

    Returns:
        torch.Tensor: Similarity matrix.
    """
    rowptr, col, _ = adj.csr()
    batch_size = batch.shape[0]
    batch_repeat = batch.repeat(wt)
    rw = adj.random_walk(batch_repeat, wl)[:, 1:]

    if not isinstance(rw, torch.Tensor):
        rw = rw[0]
    rw = rw.t().reshape(-1, batch_size).t()

    row, col, val = [], [], []
    for i in range(batch.shape[0]):
        rw_nodes, rw_times = torch.unique(rw[i], return_counts=True)
        row += [batch[i].item()] * rw_nodes.shape[0]
        col += rw_nodes.tolist()
        val += rw_times.tolist()

    unique_nodes = list(set(row + col))
    subg2g = dict(zip(unique_nodes, list(range(len(unique_nodes)))))

    row = [subg2g[x] for x in row]
    col = [subg2g[x] for x in col]
    idx = torch.tensor([subg2g[x] for x in batch.tolist()])

    adj_ = SparseTensor(row=torch.LongTensor(row), col=torch.LongTensor(col), value=torch.tensor(val),
                        sparse_sizes=(len(unique_nodes), len(unique_nodes)))

    adj_batch, _ = adj_.saint_subgraph(idx)
    adj_batch = adj_batch.set_diag(0.)
    # src, dst = dict_r[idx[adj_batch.storage.row()[3].item()].item()], dict_r[idx[adj_batch.storage.col()[3].item()].item()]
    return batch, adj_batch


def get_mask(adj):
    """Get mask matrix.

    Args:
        adj (SparseTensor): Adjacency matrix.

    Returns:
        SparseTensor: Mask matrix.
    """
    batch_mean = adj.mean(dim=1)
    mean = batch_mean[torch.LongTensor(adj.storage.row())]
    mask = (adj.storage.value() - mean) > - 1e-10
    row, col, val = adj.storage.row()[mask], adj.storage.col()[
        mask], adj.storage.value()[mask]
    adj_ = SparseTensor(row=row, col=col, value=val,
                        sparse_sizes=(adj.size(0), adj.size(1)))
    return adj_


class MAGIBatchPipeline(BasePipeline):
    """MAGI-Batch pipeline.

    Args:
        args (Namespace): Arguments.
    """
    def __init__(self, args: Namespace):
        super().__init__(args)

    def augment_data(self):
        self.data = perturb_data(self.data, self.cfg.dataset.augmentation)

        N, E, num_features = self.data.x.shape[0], self.data.edge_index.shape[-1], self.data.x.shape[-1]

        adj = SparseTensor(row=self.data.edge_index[0],
                           col=self.data.edge_index[1], sparse_sizes=(N, N))
        adj.fill_value_(1.)
        assert len(self.cfg.model.dims.encoder) == len(self.cfg.dataset.size)

        self.data.adj = adj

    def build_model(self):
        model = MAGIBatch(self.logger, self.cfg)
        self.logger.model_info(model)
        return model
