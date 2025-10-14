import numpy as np
import torch
import torch.nn.functional as F

# Optional imports for graph-based functionality
try:
    import torch_cluster
    import torch_geometric
    GRAPH_SUPPORT = True
except ImportError:
    torch_cluster = None
    torch_geometric = None
    GRAPH_SUPPORT = False

LETTER_TO_NUM = {'A': 0, 'G': 1, 'C': 2, 'U': 3}

def get_posenc(edge_index, num_posenc=16):
    # From https://github.com/jingraham/neurips19-graph-protein-design
    num_posenc = num_posenc
    d = edge_index[0] - edge_index[1]

    frequency = torch.exp(
        torch.arange(0, num_posenc, 2, dtype=torch.float32, device=d.device)
        * -(np.log(10000.0) / num_posenc)
    )

    angles = d.unsqueeze(-1) * frequency
    E = torch.cat((torch.cos(angles), torch.sin(angles)), -1)
    return E


def get_orientations(X):
    # X : num_conf x num_res x 3
    forward = normalize(X[:, 1:] - X[:, :-1])
    backward = normalize(X[:, :-1] - X[:, 1:])
    forward = F.pad(forward, [0, 0, 0, 1])
    backward = F.pad(backward, [0, 0, 1, 0])
    return torch.cat([forward.unsqueeze(-2), backward.unsqueeze(-2)], -2)


def get_orientations_single(X):
    # X : num_res x 3
    forward = normalize(X[1:] - X[:-1])
    backward = normalize(X[:-1] - X[1:])
    forward = F.pad(forward, [0, 0, 0, 1])
    backward = F.pad(backward, [0, 0, 1, 0])
    return torch.cat([forward.unsqueeze(-2), backward.unsqueeze(-2)], -2)

def get_sidechains(X):
    # X : num_conf x num_res x 3 x 3
    p, origin, n = X[:, :, 0], X[:, :, 1], X[:, :, 2]
    n, p = normalize(n - origin), normalize(p - origin)
    return torch.cat([n.unsqueeze_(-2), p.unsqueeze_(-2)], -2)

def get_sidechains_single(X):
    # X : num_res x 3 x 3
    p, origin, n = X[:, 0], X[:, 1], X[:, 2]
    n, p = normalize(n - origin), normalize(p - origin)
    return torch.cat([n.unsqueeze_(-2), p.unsqueeze_(-2)], -2)

def normalize(tensor, dim=-1):
    '''
    Normalizes a `torch.Tensor` along dimension `dim` without `nan`s.
    '''
    return torch.nan_to_num(
        torch.div(tensor, torch.linalg.norm(tensor, dim=dim, keepdim=True)))


def rbf(D, D_min=0., D_max=20., D_count=16):
    '''
    From https://github.com/jingraham/neurips19-graph-protein-design

    Returns an RBF embedding of `torch.Tensor` `D` along a new axis=-1.
    That is, if `D` has shape [...dims], then the returned tensor will have
    shape [...dims, D_count].

    TODO switch to DimeNet RBFs
    '''
    D_mu = torch.linspace(D_min, D_max, D_count, device=D.device)
    D_mu = D_mu.view([1, -1])
    D_sigma = (D_max - D_min) / D_count
    D_expand = torch.unsqueeze(D, -1)

    RBF = torch.exp(-((D_expand - D_mu) / D_sigma) ** 2)
    return RBF


@torch.no_grad()
def construct_data_single(coords, seq=None, mask=None, num_posenc=16, num_rbf=16, knn_num=10):
    if not GRAPH_SUPPORT:
        raise ImportError("torch_cluster and torch_geometric are required for construct_data_single function")
    
    coords = torch.as_tensor(coords, dtype=torch.float32) # num_res x 3 x 3
    # seq is np.array/string, convert to torch.tensor
    if isinstance(seq, np.ndarray):
        seq = torch.as_tensor(seq, dtype=torch.long)
    else:
        seq = torch.as_tensor(
            [LETTER_TO_NUM[residue] for residue in seq],
            dtype=torch.long
        )

    # Compute features
    # node positions: num_res x 3
    coord_C = coords[:, 1].clone()
    # Construct merged edge index
    edge_index = torch_cluster.knn_graph(coord_C, k=knn_num)
    edge_index = torch_geometric.utils.coalesce(edge_index)

    # Node attributes: num_res x 2 x 3, each
    orientations = get_orientations_single(coord_C)
    sidechains = get_sidechains_single(coords)

    # Edge displacement vectors: num_edges x  3
    edge_vectors = coord_C[edge_index[0]] - coord_C[edge_index[1]]

    # Edge RBF features: num_edges x num_rbf
    edge_rbf = rbf(edge_vectors.norm(dim=-1), D_count=num_rbf)
    # Edge positional encodings: num_edges x num_posenc
    edge_posenc = get_posenc(edge_index, num_posenc)

    node_s = (seq.unsqueeze(-1) == torch.arange(4).unsqueeze(0)).float()
    node_v = torch.cat([orientations, sidechains], dim=-2)
    edge_s = torch.cat([edge_rbf, edge_posenc], dim=-1)
    edge_v = normalize(edge_vectors).unsqueeze(-2)

    node_s, node_v, edge_s, edge_v = map(
        torch.nan_to_num,
        (node_s, node_v, edge_s, edge_v)
    )

    # add mask for invalid residues
    if mask is None:
        mask = coords.sum(dim=(2, 3)) == 0.
    mask = torch.tensor(mask)

    return {'seq': seq,
            'coords': coords,
            'node_s': node_s,
            'node_v': node_v,
            'edge_s': edge_s,
            'edge_v': edge_v,
            'edge_index': edge_index,
            'mask': mask}
