import pandas as pd
import numpy as np
import torch
import warnings

from bio_fly.functional import build_perturbation_specs
from bio_fly.propagation import (
    PropagationConfig,
    TorchPropagationGraph,
    signed_multihop_response,
    signed_multihop_response_torch,
    summarize_response,
)


def test_signed_multihop_response() -> None:
    edges = pd.DataFrame(
        [
            {"Presynaptic_ID": 1, "Postsynaptic_ID": 2, "Excitatory x Connectivity": 2},
            {"Presynaptic_ID": 2, "Postsynaptic_ID": 3, "Excitatory x Connectivity": -4},
            {"Presynaptic_ID": 1, "Postsynaptic_ID": 4, "Excitatory x Connectivity": 1},
        ]
    )

    response = signed_multihop_response(edges, seed_ids=[1], config=PropagationConfig(steps=2, max_active=10))
    summary = summarize_response("left_activate", [1], response, readout_ids=[3])

    assert set(response["step"]) == {1, 2}
    assert summary.active_neurons == 3
    assert summary.absolute_mass > 0
    assert summary.readout_score < 0


def test_signed_multihop_response_torch_cpu() -> None:
    indices = torch.tensor([[1, 2, 3], [0, 1, 0]], dtype=torch.long)
    values = torch.tensor([2.0, -4.0, 1.0], dtype=torch.float32)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Sparse invariant checks are implicitly disabled.*")
        matrix = torch.sparse_coo_tensor(
            indices, values, size=(4, 4), device="cpu", check_invariants=False
        ).coalesce()
    graph = TorchPropagationGraph(
        matrix=matrix,
        root_ids_by_index=np.array([1, 2, 3, 4], dtype=np.int64),
        root_to_index={1: 0, 2: 1, 3: 2, 4: 3},
        device="cpu",
    )

    response = signed_multihop_response_torch(graph, seed_ids=[1], config=PropagationConfig(steps=2, max_active=10))
    summary = summarize_response("left_activate", [1], response, readout_ids=[3])

    assert set(response["step"]) == {1, 2}
    assert summary.active_neurons == 3
    assert summary.readout_score < 0


def test_build_perturbation_specs() -> None:
    pairwise = pd.DataFrame(
        [
            {
                "pair_token": "roots:1-2",
                "label": "KC",
                "left_root_id": 1,
                "right_root_id": 2,
                "out_laterality": 0.25,
            }
        ]
    )

    specs = build_perturbation_specs(pairwise, top_n=1)

    assert len(specs) == 4
    assert specs[0].activate_ids == (1,)
    assert specs[1].activate_ids == (2,)
