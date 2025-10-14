from __future__ import annotations

import os
import site
from pathlib import Path
from typing import Tuple

import torch

__all__ = ["closest_points", "chamfer_distance"]

_EXTENSION = None


def _extension() -> object:
    global _EXTENSION
    if _EXTENSION is not None:
        return _EXTENSION

    try:
        import chamfer_ext  # type: ignore
    except ImportError:
        src_dir = Path(__file__).resolve().parent / "src"
        if not src_dir.exists():
            raise RuntimeError(
                "chamfer_ext extension not built. Install from wheel or run setup.py."
            ) from None

        from torch.utils.cpp_extension import load
        import nanobind

        nanobind_root = Path(nanobind.__file__).resolve().parent
        nb_combined = nanobind_root / "src" / "nb_combined.cpp"

        sources = [
            src_dir / "metal_bridge.mm",
            src_dir / "kd_tree.cpp",
            nb_combined,
        ]
        include_dirs = [
            str(src_dir),
            str(nanobind_root / "include"),
            str(nanobind_root / "ext" / "robin_map" / "include"),
        ]

        os.environ.setdefault("MACOSX_DEPLOYMENT_TARGET", "13.0")
        user_bin = Path(site.getuserbase()) / "bin"
        if user_bin.exists():
            current_path = os.environ.get("PATH", "")
            if str(user_bin) not in current_path.split(os.pathsep):
                os.environ["PATH"] = os.pathsep.join(
                    [str(user_bin)] + ([current_path] if current_path else [])
                )

        extra_cflags = ["-std=c++20", "-fobjc-arc", "-fvisibility=hidden"]
        extra_ldflags = ["-framework", "Metal", "-framework", "Foundation"]

        chamfer_ext = load(
            name="chamfer_ext",
            sources=[str(path) for path in sources if path.exists()],
            extra_include_paths=include_dirs,
            extra_cflags=extra_cflags,
            extra_ldflags=extra_ldflags,
            verbose=False,
        )

    _EXTENSION = chamfer_ext
    return _EXTENSION


def _mps_available() -> bool:
    return bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available())


def _validate_pair(query: torch.Tensor, reference: torch.Tensor) -> None:
    if query.dim() != 2:
        raise ValueError("query tensor must be 2D [N, K]")
    if reference.dim() != 2:
        raise ValueError("reference tensor must be 2D [M, K]")
    if query.size(1) != reference.size(1):
        raise ValueError("query and reference tensors must have matching feature dimensions")

def _require_device(tensor: torch.Tensor, device: str, name: str) -> None:
    if tensor.device.type != device:
        raise ValueError(f"{name} tensor must live on {device}, but found {tensor.device.type}")


def _require_float32(tensor: torch.Tensor, name: str) -> None:
    if tensor.dtype != torch.float32:
        raise ValueError(f"{name} tensor must be float32, but found {tensor.dtype}")


def _prepare_backend_tensors(
    query: torch.Tensor, reference: torch.Tensor, *, is_mps: bool
) -> Tuple[torch.Tensor, torch.Tensor]:
    device = "mps" if is_mps else "cpu"
    _require_device(query, device, "query")
    _require_device(reference, device, "reference")
    _require_float32(query, "query")
    _require_float32(reference, "reference")
    return query.contiguous(), reference.contiguous()


def _decide_backend(
    query: torch.Tensor, reference: torch.Tensor, use_mps: bool | None
) -> bool:
    mps_available = _mps_available()
    inputs_on_mps = query.device.type == "mps" and reference.device.type == "mps"
    inputs_on_cpu = query.device.type == "cpu" and reference.device.type == "cpu"

    if use_mps is True:
        if not mps_available:
            raise RuntimeError("MPS was requested, but torch.backends.mps.is_available() is False")
        if not inputs_on_mps:
            raise ValueError("MPS execution requires both tensors to be on the mps device")
        return True

    if use_mps is False:
        if not inputs_on_cpu:
            raise ValueError("CPU execution requires both tensors to be on the cpu device")
        return False

    if inputs_on_mps:
        if not mps_available:
            raise RuntimeError("Input tensors are on MPS, but the MPS backend is unavailable")
        return True

    if inputs_on_cpu:
        return False

    raise ValueError("query and reference must both reside on either CPU or MPS device")


def closest_points(
    query: torch.Tensor,
    reference: torch.Tensor,
    *,
    use_mps: bool | None = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Return (indices, squared distances) of nearest neighbours in *reference* for each query point.

    The search uses a kd-tree constructed on the CPU but traversed on the GPU via MPS/Metal.
    """

    _validate_pair(query, reference)
    use_mps_flag = _decide_backend(query, reference, use_mps)
    query_prepped, reference_prepped = _prepare_backend_tensors(query, reference, is_mps=use_mps_flag)
    ext = _extension()
    if use_mps_flag:
        return ext.kd_query(query_prepped, reference_prepped)
    if not hasattr(ext, "kd_query_cpu"):
        raise RuntimeError("CPU kd-tree query is not available in the compiled extension")
    return ext.kd_query_cpu(query_prepped, reference_prepped)


class _ChamferDistanceFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, a: torch.Tensor, b: torch.Tensor, use_mps_flag: bool | None = None) -> torch.Tensor:
        if a.device != b.device:
            raise ValueError("points_a and points_b must be on the same device")
        assert a.device.type in {"cpu", "mps"}, "Unsupported device for chamfer_distance"

        _validate_pair(a, b)
        backend_is_mps = _decide_backend(a, b, use_mps_flag)
        a_prepped, b_prepped = _prepare_backend_tensors(a, b, is_mps=backend_is_mps)

        idx_ab_tensor, _ = closest_points(a_prepped, b_prepped, use_mps=backend_is_mps)
        idx_ba_tensor, _ = closest_points(b_prepped, a_prepped, use_mps=backend_is_mps)

        idx_ab = idx_ab_tensor.to(device=b_prepped.device, dtype=torch.long)
        idx_ba = idx_ba_tensor.to(device=a_prepped.device, dtype=torch.long)

        nn_ab = torch.index_select(b_prepped, 0, idx_ab)
        nn_ba = torch.index_select(a_prepped, 0, idx_ba)

        diff_ab = a_prepped - nn_ab
        diff_ba = b_prepped - nn_ba

        loss_ab = torch.sum(diff_ab * diff_ab, dim=1).mean()
        loss_ba = torch.sum(diff_ba * diff_ba, dim=1).mean()
        loss = loss_ab + loss_ba

        ctx.save_for_backward(
            a_prepped,
            b_prepped,
            idx_ab_tensor.to(torch.long),
            idx_ba_tensor.to(torch.long),
        )
        ctx.sizes = (a_prepped.shape[0], b_prepped.shape[0])

        return loss

    @staticmethod
    def backward(ctx, grad_output: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, None]:
        a, b, idx_ab_saved, idx_ba_saved = ctx.saved_tensors
        n_a, n_b = ctx.sizes

        grad_a = grad_b = None
        scalar_a = grad_output.to(device=a.device, dtype=a.dtype)
        scalar_b = grad_output.to(device=b.device, dtype=b.dtype)

        # All tensors are either on CPU or MPS; keep computations there.
        assert a.device == b.device == idx_ab_saved.device == idx_ba_saved.device

        if ctx.needs_input_grad[0] or ctx.needs_input_grad[1]:
            idx_ab = idx_ab_saved.to(device=b.device)
            nn_ab = torch.index_select(b, 0, idx_ab)
            diff_ab = a - nn_ab

            coeff_ab = (2.0 / float(n_a)) * scalar_a

        if ctx.needs_input_grad[1] or ctx.needs_input_grad[0]:
            idx_ba = idx_ba_saved.to(device=a.device)
            nn_ba = torch.index_select(a, 0, idx_ba)
            diff_ba = b - nn_ba

            coeff_ba = (2.0 / float(n_b)) * scalar_b

        if ctx.needs_input_grad[0]:
            grad_a = coeff_ab * diff_ab
            grad_a = grad_a.contiguous()
            scatter_idx = idx_ba_saved
            grad_a.index_add_(0, scatter_idx, (-coeff_ba) * diff_ba)

        if ctx.needs_input_grad[1]:
            grad_b = coeff_ba * diff_ba
            grad_b = grad_b.contiguous()
            scatter_idx = idx_ab_saved
            grad_b.index_add_(0, scatter_idx, (-coeff_ab) * diff_ab)

        return grad_a, grad_b, None


def chamfer_distance(
    points_a: torch.Tensor,
    points_b: torch.Tensor,
    *,
    use_mps: bool | None = None,
) -> torch.Tensor:
    return _ChamferDistanceFunction.apply(points_a, points_b, use_mps)
