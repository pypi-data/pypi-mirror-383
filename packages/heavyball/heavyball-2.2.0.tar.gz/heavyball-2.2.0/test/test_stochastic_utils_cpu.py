import os

os.environ.setdefault("TORCH_COMPILE_DISABLE", "1")

import torch

from heavyball.utils import copy_stochastic_, stochastic_add_, stochastic_divide_with_eps_


def _average_stochastic_round(source: torch.Tensor, trials: int = 512) -> torch.Tensor:
    dest = torch.empty_like(source, dtype=torch.bfloat16)
    totals = torch.zeros_like(source, dtype=torch.float64)
    for _ in range(trials):
        copy_stochastic_(dest, source)
        totals += dest.to(dtype=torch.float64)
    return totals / trials


def test_copy_stochastic_round_is_close_to_source_mean():
    torch.manual_seed(0x5566AA)
    values = torch.randn(2048, dtype=torch.float32) * 3.0
    averaged = _average_stochastic_round(values, trials=256)
    delta = averaged - values.double()

    # Stochastic round should stay close to the original float32 values.
    assert delta.abs().mean().item() < 5e-3
    assert delta.abs().max().item() < 2.5e-2


def test_stochastic_add_broadcasts_partner_lists():
    torch.manual_seed(0x172893)
    targets = [torch.zeros(4, dtype=torch.bfloat16) for _ in range(2)]
    partner = [torch.linspace(-1.0, 1.0, 4, dtype=torch.float32)]

    stochastic_add_(targets, partner, alpha=0.25)
    expected = partner[0] * 0.25
    for tensor in targets:
        assert torch.allclose(tensor.float(), expected, atol=5e-3, rtol=0)


def test_stochastic_divide_with_eps_matches_float_result():
    torch.manual_seed(0xABCDEF)
    numerator = torch.randn(32, dtype=torch.bfloat16)
    denominator = torch.rand(32, dtype=torch.bfloat16) + 0.05
    result = numerator.clone()

    stochastic_divide_with_eps_(result, denominator, eps=1e-3)
    expected = numerator.float() / (denominator.float() + 1e-3)
    assert torch.allclose(result.float(), expected, atol=2e-2, rtol=2e-2)
