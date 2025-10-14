import torch

def cosine_similarity_matrix(A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
    """Compute cosine similarity between all rows of A and B."""
    A_norm = A / A.norm(dim=1, keepdim=True)
    B_norm = B / B.norm(dim=1, keepdim=True)
    return A_norm @ B_norm.T  # shape: [A.size(0), B.size(0)]


def bin_similarities(sim_matrix: torch.Tensor, thresholds=None) -> torch.Tensor:
    """
    Discretize cosine similarity scores into bins (0=bad, 1=ok, 2=good, 3=excellent).
    thresholds: list of 3 cutoffs between 0 and 1, e.g. [0.6, 0.75, 0.9]
    """
    if thresholds is None:
        thresholds = [0.6, 0.75, 0.9]
    bins = torch.bucketize(sim_matrix, torch.tensor(thresholds))
    return bins