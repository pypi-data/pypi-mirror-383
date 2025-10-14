from typing import Optional, Tuple

import pytest
import torch

import chamfer


def brute_force_closest(query: torch.Tensor, reference: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    query = query.to(torch.float32).contiguous()
    reference = reference.to(torch.float32).contiguous()
    diff = query[:, None, :] - reference[None, :, :]
    dists = torch.sum(diff * diff, dim=-1)
    min_dists, indices = torch.min(dists, dim=1)
    return indices.to(torch.int32), min_dists


def brute_chamfer(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    _, d1 = brute_force_closest(a, b)
    _, d2 = brute_force_closest(b, a)
    return d1.mean() + d2.mean()


@pytest.mark.parametrize("dims", [2, 3, 5])
@pytest.mark.parametrize("use_mps", [None, False])
def test_closest_points_matches_bruteforce(dims: int, use_mps: Optional[bool]) -> None:
    torch.manual_seed(42 + dims)
    query = torch.rand(128, dims)
    reference = torch.rand(200, dims)

    idx_gpu, dist_gpu = chamfer.closest_points(query, reference, use_mps=use_mps)
    idx_cpu, dist_cpu = brute_force_closest(query, reference)

    assert idx_gpu.shape == idx_cpu.shape == (query.size(0),)
    assert torch.all(idx_gpu >= 0)
    torch.testing.assert_close(dist_gpu, dist_cpu, atol=1e-5, rtol=1e-4)


@pytest.mark.parametrize("dims", [2, 3])
def test_chamfer_distance_matches_bruteforce(dims: int) -> None:
    torch.manual_seed(123 + dims)
    a = torch.rand(64, dims)
    b = torch.rand(96, dims)

    chamfer_gpu = chamfer.chamfer_distance(a, b, use_mps=False)
    chamfer_cpu = brute_chamfer(a, b)

    torch.testing.assert_close(chamfer_gpu, chamfer_cpu, atol=1e-5, rtol=1e-4)


@pytest.mark.parametrize("dims", [2, 3])
def test_grad_disabled_by_default(dims: int) -> None:
    a = torch.randn(8, dims, requires_grad=False)
    b = torch.randn(12, dims, requires_grad=False)

    _, dists = chamfer.closest_points(a, b)
    assert not dists.requires_grad


@pytest.mark.parametrize("dims", [2, 3])
def test_chamfer_distance_gradients_match_bruteforce(dims: int) -> None:
    torch.manual_seed(321 + dims)
    a = torch.rand(32, dims, requires_grad=True)
    b = torch.rand(40, dims, requires_grad=True)

    loss_kd = chamfer.chamfer_distance(a, b, use_mps=False)
    grad_a_kd, grad_b_kd = torch.autograd.grad(loss_kd, (a, b), create_graph=False)

    a_ref = a.detach().clone().requires_grad_(True)
    b_ref = b.detach().clone().requires_grad_(True)
    loss_brute = brute_chamfer(a_ref, b_ref)
    grad_a_brute, grad_b_brute = torch.autograd.grad(loss_brute, (a_ref, b_ref), create_graph=False)

    torch.testing.assert_close(grad_a_kd, grad_a_brute, atol=1e-4, rtol=1e-4)
    torch.testing.assert_close(grad_b_kd, grad_b_brute, atol=1e-4, rtol=1e-4)


def test_closest_points_use_mps_requires_device() -> None:
    query = torch.rand(16, 3)
    reference = torch.rand(32, 3)
    expected_exception = ValueError if torch.backends.mps.is_available() else RuntimeError
    with pytest.raises(expected_exception):
        chamfer.closest_points(query, reference, use_mps=True)


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS backend unavailable")
def test_closest_points_mps_matches_cpu() -> None:
    torch.manual_seed(7)
    query_cpu = torch.rand(64, 3)
    reference_cpu = torch.rand(96, 3)

    query_mps = query_cpu.to("mps")
    reference_mps = reference_cpu.to("mps")

    idx_mps, dist_mps = chamfer.closest_points(query_mps, reference_mps, use_mps=True)

    assert idx_mps.device.type == "mps"
    assert dist_mps.device.type == "mps"

    _, dist_cpu = brute_force_closest(query_cpu, reference_cpu)
    torch.testing.assert_close(dist_mps.cpu(), dist_cpu, atol=1e-5, rtol=1e-4)


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS backend unavailable")
def test_closest_points_mps_rejects_cpu_inputs() -> None:
    query_mps = torch.rand(8, 3, device="mps")
    reference_cpu = torch.rand(8, 3)
    with pytest.raises(ValueError):
        chamfer.closest_points(query_mps, reference_cpu, use_mps=True)
