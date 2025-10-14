# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from typing import Tuple

import tensorrt as trt
import tensorrt.plugin as trtp
import torch

import cuequivariance_ops_torch._ext as ops
from cuequivariance_ops_torch.fused_layer_norm_torch import (
    Layout,
    _layer_norm_transpose,
)
from cuequivariance_ops_torch.triangle_attention import (
    _fallback_threshold,
    _should_use_tf32,
    _triangle_attention_torch,
)
from cuequivariance_ops_torch.triangle_multiplicative_update import _tri_mul_update


def register_plugins():
    pass


def _to_torch(*args):
    ret = []
    for a in args:
        if a is None:
            ret = ret + [
                None,
            ]
        elif isinstance(a, trtp.Tensor):
            if a.dtype == trt.bfloat16:
                a._immutable = False
                a._dtype = trt.float16
                tt = torch.as_tensor(a, device="cuda").view(dtype=torch.bfloat16)
            else:
                tt = torch.as_tensor(a, device="cuda")
            ret = ret + [
                tt,
            ]
        else:
            raise ValueError(f"Unexpected type: {type(a)}")
    return ret


@trtp.register("cuequivariance::identity_2")
def _(
    s: trtp.TensorDesc, z: trtp.TensorDesc
) -> Tuple[trtp.TensorDesc, trtp.TensorDesc]:
    return s.like(), z.like()


@trtp.impl("cuequivariance::identity_2")
def _(
    s: trtp.Tensor,
    z: trtp.Tensor,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    with torch.cuda.stream(torch.cuda.ExternalStream(stream)):
        s_, z_, s_copy, z_copy = _to_torch(s, z, outputs[0], outputs[1])
        s_copy.copy_(s_)
        z_copy.copy_(z_)


@trtp.register("cuequivariance::segmented_transpose")
def _(
    tensor: trtp.TensorDesc, segment_info: trtp.TensorDesc, contiguous: bool
) -> trtp.TensorDesc:
    return tensor.like()


@trtp.impl("cuequivariance::segmented_transpose")
def _(
    tensor: trtp.Tensor,
    segment_info: trtp.Tensor,
    contiguous: bool,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    with torch.cuda.stream(torch.cuda.ExternalStream(stream)):
        tensor_ = torch.as_tensor(tensor, device="cuda")
        segment_info_ = torch.as_tensor(segment_info, device="cuda")
        ret = torch.as_tensor(outputs[0], device="cuda")
        ops.segmented_transpose(
            ret,
            tensor_,
            segment_info_,
            contiguous,
            stream,
        )


@trtp.register("cuequivariance::triangle_attention")
def _(
    q: trtp.TensorDesc,
    k: trtp.TensorDesc,
    v: trtp.TensorDesc,
    b: trtp.TensorDesc,
    mask: trtp.TensorDesc,
    scale: float,
) -> Tuple[trtp.TensorDesc, trtp.TensorDesc, trtp.TensorDesc]:
    aux = trtp.from_shape_expr(
        (q.shape_expr[0], q.shape_expr[1], q.shape_expr[2], q.shape_expr[3]),
        dtype=trt.float32,
    )
    return q.like(), aux, aux.like()


@trtp.register("cuequivariance::triangle_attention_mask")
def _(
    q: trtp.TensorDesc,
    k: trtp.TensorDesc,
    v: trtp.TensorDesc,
    b: trtp.TensorDesc,
    mask: trtp.TensorDesc,
    scale: float,
) -> trtp.TensorDesc:
    return q.like()


@trtp.register("cuequivariance::triangle_attention_nomask")
def _(
    q: trtp.TensorDesc,
    k: trtp.TensorDesc,
    v: trtp.TensorDesc,
    b: trtp.TensorDesc,
    scale: float,
) -> trtp.TensorDesc:
    return q.like()


def _tri_attn(q_, k_, v_, b_, mask_, scale, ret, lse, lse_max, stream):
    seq_len = q_.shape[-2]

    # print (f"seq_len = {seq_len}, threshold={_fallback_threshold()}")
    if lse is None and lse_max is None and seq_len <= _fallback_threshold():
        # Use original PyTorch implementation for short sequences
        _triangle_attention_torch(q_, k_, v_, b_, mask_, scale, out=ret)
    else:
        if lse is None:
            lse = q_.new_empty(q_.shape[:-1], dtype=torch.float32)
        if lse_max is None:
            lse_max = q_.new_empty(q_.shape[:-1], dtype=torch.float32)

        ops.triangle_attention(
            ret,
            lse,
            lse_max,
            q_,
            k_,
            v_,
            mask_,
            b_,
            scale,
            _should_use_tf32(),
            stream,
        )


@trtp.impl("cuequivariance::triangle_attention")
def _(
    q: trtp.Tensor,
    k: trtp.Tensor,
    v: trtp.Tensor,
    b: trtp.Tensor,
    mask: trtp.Tensor,
    scale: float,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    with torch.cuda.stream(torch.cuda.ExternalStream(stream)):
        q_, k_, v_, b_, mask_, ret, lse, lse_max = _to_torch(q, k, v, b, mask, *outputs)
        _tri_attn(q_, k_, v_, b_, mask_, scale, ret, lse, lse_max, stream)


@trtp.impl("cuequivariance::triangle_attention_mask")
def _(
    q: trtp.Tensor,
    k: trtp.Tensor,
    v: trtp.Tensor,
    b: trtp.Tensor,
    mask: trtp.Tensor,
    scale: float,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    with torch.cuda.stream(torch.cuda.ExternalStream(stream)):
        ret, q_, k_, v_, b_, mask_ = _to_torch(outputs[0], q, k, v, b, mask)
        # bfomitchev: this workaround does not work (yet?), crashes elsewhere
        # mask_ = None if mask.numel() == 0 else torch.as_tensor(mask, device="cuda")
        _tri_attn(q_, k_, v_, b_, mask_, scale, ret, None, None, stream)


@trtp.impl("cuequivariance::triangle_attention_nomask")
def _(
    q: trtp.Tensor,
    k: trtp.Tensor,
    v: trtp.Tensor,
    b: trtp.Tensor,
    scale: float,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    with torch.cuda.stream(torch.cuda.ExternalStream(stream)):
        ret, q_, k_, v_, b_ = _to_torch(outputs[0], q, k, v, b)
        _tri_attn(q_, k_, v_, b_, None, scale, ret, None, None, stream)


@trtp.register("cuequivariance::layer_norm_transpose")
def _(
    x: trtp.TensorDesc,
    w: trtp.TensorDesc,
    b: trtp.TensorDesc,
    eps: float,
    elementwise_affine: bool,
    layout: int,
) -> Tuple[trtp.TensorDesc, trtp.TensorDesc, trtp.TensorDesc]:
    if layout == Layout.BND_BND:
        B, N, D = x.shape_expr
        out = trtp.from_shape_expr((B, N, D), dtype=x.dtype)
    elif layout == Layout.BDN_BND:
        B, D, N = x.shape_expr
        out = trtp.from_shape_expr((B, N, D), dtype=x.dtype)
    elif layout == Layout.BND_BDN:
        B, N, D = x.shape_expr
        out = trtp.from_shape_expr((B, D, N), dtype=x.dtype)
    elif layout == Layout.DBN_BND:
        D, B, N = x.shape_expr
        out = trtp.from_shape_expr((B, N, D), dtype=x.dtype)
    elif layout == Layout.BND_DBN:
        B, N, D = x.shape_expr
        out = trtp.from_shape_expr((D, B, N), dtype=x.dtype)
    else:
        raise ValueError

    mean = trtp.from_shape_expr((B, N), dtype=trt.float32)
    rstd = trtp.from_shape_expr((B, N), dtype=trt.float32)
    return out, mean, rstd


@trtp.impl("cuequivariance::layer_norm_transpose")
def _(
    x: trtp.Tensor,
    w: trtp.Tensor,
    b: trtp.Tensor,
    eps: float,
    elementwise_affine: bool,
    layout: int,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    x_, w_, b_ = _to_torch(x, w, b)
    out, mean, rstd = _to_torch(*outputs)
    if layout == Layout.BND_BND:
        B, N, D = x_.shape
    elif layout == Layout.BDN_BND:
        B, D, N = x_.shape
    elif layout == Layout.BND_BDN:
        B, N, D = x_.shape
    elif layout == Layout.DBN_BND:
        D, B, N = x_.shape
    elif layout == Layout.BND_DBN:
        B, N, D = x_.shape
    _layer_norm_transpose(
        x_, w_, b_, eps, elementwise_affine, layout, out, mean, rstd, B, N, D
    )


@trtp.register("cuequivariance::attention_pair_bias_mask")
def _(
    z: trtp.TensorDesc,
    w_proj_z: trtp.TensorDesc,
    w_ln: trtp.TensorDesc,
    b_ln: trtp.TensorDesc,
    mask: trtp.TensorDesc,
    num_heads: int,
    multiplicity: int,
    eps: float,
    inf: float,
    is_cached_z_proj: bool,
) -> Tuple[trtp.TensorDesc, trtp.TensorDesc]:
    if is_cached_z_proj:
        B, _, U, V = z.shape_expr
        DIM_Z = None
    else:
        B, U, V, DIM_Z = z.shape_expr

    out_mask = trtp.from_shape_expr((B * multiplicity, num_heads, U, V), dtype=z.dtype)
    if is_cached_z_proj:
        z_proj = z.like()
    else:
        z_proj = trtp.from_shape_expr((B, num_heads, U, V), dtype=z.dtype)
    return out_mask, z_proj


@trtp.impl("cuequivariance::attention_pair_bias_mask")
def _(
    z: trtp.Tensor,
    w_proj_z: trtp.Tensor,
    w_ln: trtp.Tensor,
    b_ln: trtp.Tensor,
    mask: trtp.Tensor,
    num_heads: int,
    multiplicity: int,
    eps: float,
    inf: float,
    is_cached_z_proj: bool,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    with torch.cuda.stream(torch.cuda.ExternalStream(stream)):
        (z_, w_proj_z_, w_ln_, b_ln_, mask_) = _to_torch(z, w_proj_z, w_ln, b_ln, mask)
        out_mask_, z_proj_ = _to_torch(*outputs)
        out_mask, z_proj = torch.ops.cuequivariance.attention_pair_bias_mask(
            z_,
            w_proj_z_,
            w_ln_,
            b_ln_,
            mask_,
            num_heads,
            multiplicity,
            eps,
            inf,
            is_cached_z_proj,
        )
        out_mask_.copy_(out_mask)
        z_proj_.copy_(z_proj)


@trtp.register("cuequivariance::tri_mul_update")
def _(
    x: trtp.TensorDesc,
    mask: trtp.TensorDesc,
    norm_in_weight: trtp.TensorDesc,
    norm_in_bias: trtp.TensorDesc,
    p_in_weight: trtp.TensorDesc,
    p_in_bias: trtp.TensorDesc,
    g_in_weight: trtp.TensorDesc,
    g_in_bias: trtp.TensorDesc,
    norm_out_weight: trtp.TensorDesc,
    norm_out_bias: trtp.TensorDesc,
    p_out_weight: trtp.TensorDesc,
    p_out_bias: trtp.TensorDesc,
    g_out_weight: trtp.TensorDesc,
    g_out_bias: trtp.TensorDesc,
    direction: str,
    eps: float,
    precision: int,
) -> trtp.TensorDesc:
    return x.like()


@trtp.register("cuequivariance::tri_mul_update_noin_bias")
def _(
    x: trtp.TensorDesc,
    mask: trtp.TensorDesc,
    norm_in_weight: trtp.TensorDesc,
    norm_in_bias: trtp.TensorDesc,
    p_in_weight: trtp.TensorDesc,
    g_in_weight: trtp.TensorDesc,
    norm_out_weight: trtp.TensorDesc,
    norm_out_bias: trtp.TensorDesc,
    p_out_weight: trtp.TensorDesc,
    p_out_bias: trtp.TensorDesc,
    g_out_weight: trtp.TensorDesc,
    g_out_bias: trtp.TensorDesc,
    direction: str,
    eps: float,
    precision: int,
) -> trtp.TensorDesc:
    return x.like()


@trtp.register("cuequivariance::tri_mul_update_noout_bias")
def _(
    x: trtp.TensorDesc,
    mask: trtp.TensorDesc,
    norm_in_weight: trtp.TensorDesc,
    norm_in_bias: trtp.TensorDesc,
    p_in_weight: trtp.TensorDesc,
    p_in_bias: trtp.TensorDesc,
    g_in_weight: trtp.TensorDesc,
    g_in_bias: trtp.TensorDesc,
    norm_out_weight: trtp.TensorDesc,
    norm_out_bias: trtp.TensorDesc,
    p_out_weight: trtp.TensorDesc,
    g_out_weight: trtp.TensorDesc,
    direction: str,
    eps: float,
    precision: int,
) -> trtp.TensorDesc:
    return x.like()


@trtp.register("cuequivariance::tri_mul_update_noin_bias_noout_bias")
def _(
    x: trtp.TensorDesc,
    mask: trtp.TensorDesc,
    norm_in_weight: trtp.TensorDesc,
    norm_in_bias: trtp.TensorDesc,
    p_in_weight: trtp.TensorDesc,
    g_in_weight: trtp.TensorDesc,
    norm_out_weight: trtp.TensorDesc,
    norm_out_bias: trtp.TensorDesc,
    p_out_weight: trtp.TensorDesc,
    g_out_weight: trtp.TensorDesc,
    direction: str,
    eps: float,
    precision: int,
) -> trtp.TensorDesc:
    return x.like()


@trtp.register("cuequivariance::tri_mul_update_nomask")
def _(
    x: trtp.TensorDesc,
    norm_in_weight: trtp.TensorDesc,
    norm_in_bias: trtp.TensorDesc,
    p_in_weight: trtp.TensorDesc,
    p_in_bias: trtp.TensorDesc,
    g_in_weight: trtp.TensorDesc,
    g_in_bias: trtp.TensorDesc,
    norm_out_weight: trtp.TensorDesc,
    norm_out_bias: trtp.TensorDesc,
    p_out_weight: trtp.TensorDesc,
    p_out_bias: trtp.TensorDesc,
    g_out_weight: trtp.TensorDesc,
    g_out_bias: trtp.TensorDesc,
    direction: str,
    eps: float,
    precision: int,
) -> trtp.TensorDesc:
    return x.like()


@trtp.register("cuequivariance::tri_mul_update_nomask_noin_bias")
def _(
    x: trtp.TensorDesc,
    norm_in_weight: trtp.TensorDesc,
    norm_in_bias: trtp.TensorDesc,
    p_in_weight: trtp.TensorDesc,
    g_in_weight: trtp.TensorDesc,
    norm_out_weight: trtp.TensorDesc,
    norm_out_bias: trtp.TensorDesc,
    p_out_weight: trtp.TensorDesc,
    p_out_bias: trtp.TensorDesc,
    g_out_weight: trtp.TensorDesc,
    g_out_bias: trtp.TensorDesc,
    direction: str,
    eps: float,
    precision: int,
) -> trtp.TensorDesc:
    return x.like()


@trtp.register("cuequivariance::tri_mul_update_nomask_noout_bias")
def _(
    x: trtp.TensorDesc,
    norm_in_weight: trtp.TensorDesc,
    norm_in_bias: trtp.TensorDesc,
    p_in_weight: trtp.TensorDesc,
    p_in_bias: trtp.TensorDesc,
    g_in_weight: trtp.TensorDesc,
    g_in_bias: trtp.TensorDesc,
    norm_out_weight: trtp.TensorDesc,
    norm_out_bias: trtp.TensorDesc,
    p_out_weight: trtp.TensorDesc,
    g_out_weight: trtp.TensorDesc,
    direction: str,
    eps: float,
    precision: int,
) -> trtp.TensorDesc:
    return x.like()


@trtp.register("cuequivariance::tri_mul_update_nomask_noin_bias_noout_bias")
def _(
    x: trtp.TensorDesc,
    norm_in_weight: trtp.TensorDesc,
    norm_in_bias: trtp.TensorDesc,
    p_in_weight: trtp.TensorDesc,
    g_in_weight: trtp.TensorDesc,
    norm_out_weight: trtp.TensorDesc,
    norm_out_bias: trtp.TensorDesc,
    p_out_weight: trtp.TensorDesc,
    g_out_weight: trtp.TensorDesc,
    direction: str,
    eps: float,
    precision: int,
) -> trtp.TensorDesc:
    return x.like()


def _tri_mul_update_impl(
    stream: int, direction: str, eps: float, precision: int, *inouts
):
    with torch.cuda.stream(torch.cuda.ExternalStream(stream)):
        (
            out,
            x,
            mask,
            norm_in_weight,
            norm_in_bias,
            p_in_weight,
            p_in_bias,
            g_in_weight,
            g_in_bias,
            norm_out_weight,
            norm_out_bias,
            p_out_weight,
            p_out_bias,
            g_out_weight,
            g_out_bias,
        ) = _to_torch(*inouts)
        # QDP has issues with sending string arguments
        direction = direction.rstrip("\0")
        ret = _tri_mul_update(
            x,
            mask,
            norm_in_weight,
            norm_in_bias,
            p_in_weight,
            p_in_bias,
            g_in_weight,
            g_in_bias,
            norm_out_weight,
            norm_out_bias,
            p_out_weight,
            p_out_bias,
            g_out_weight,
            g_out_bias,
            direction,
            eps,
            precision,
        )
        out.copy_(ret)


@trtp.impl("cuequivariance::tri_mul_update")
def _(
    x: trtp.Tensor,
    mask: trtp.Tensor,
    norm_in_weight: trtp.Tensor,
    norm_in_bias: trtp.Tensor,
    p_in_weight: trtp.Tensor,
    p_in_bias: trtp.Tensor,
    g_in_weight: trtp.Tensor,
    g_in_bias: trtp.Tensor,
    norm_out_weight: trtp.Tensor,
    norm_out_bias: trtp.Tensor,
    p_out_weight: trtp.Tensor,
    p_out_bias: trtp.Tensor,
    g_out_weight: trtp.Tensor,
    g_out_bias: trtp.Tensor,
    direction: str,
    eps: float,
    precision: int,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    _tri_mul_update_impl(
        stream,
        direction,
        eps,
        precision,
        outputs[0],
        x,
        mask,
        norm_in_weight,
        norm_in_bias,
        p_in_weight,
        p_in_bias,
        g_in_weight,
        g_in_bias,
        norm_out_weight,
        norm_out_bias,
        p_out_weight,
        p_out_bias,
        g_out_weight,
        g_out_bias,
    )


@trtp.impl("cuequivariance::tri_mul_update_noout_bias")
def _(
    x: trtp.Tensor,
    mask: trtp.Tensor,
    norm_in_weight: trtp.Tensor,
    norm_in_bias: trtp.Tensor,
    p_in_weight: trtp.Tensor,
    p_in_bias: trtp.Tensor,
    g_in_weight: trtp.Tensor,
    g_in_bias: trtp.Tensor,
    norm_out_weight: trtp.Tensor,
    norm_out_bias: trtp.Tensor,
    p_out_weight: trtp.Tensor,
    g_out_weight: trtp.Tensor,
    direction: str,
    eps: float,
    precision: int,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    _tri_mul_update_impl(
        stream,
        direction,
        eps,
        precision,
        outputs[0],
        x,
        mask,
        norm_in_weight,
        norm_in_bias,
        p_in_weight,
        p_in_bias,
        g_in_weight,
        g_in_bias,
        norm_out_weight,
        norm_out_bias,
        p_out_weight,
        None,
        g_out_weight,
        None,
    )


@trtp.impl("cuequivariance::tri_mul_update_noin_bias")
def _(
    x: trtp.Tensor,
    mask: trtp.Tensor,
    norm_in_weight: trtp.Tensor,
    norm_in_bias: trtp.Tensor,
    p_in_weight: trtp.Tensor,
    g_in_weight: trtp.Tensor,
    norm_out_weight: trtp.Tensor,
    norm_out_bias: trtp.Tensor,
    p_out_weight: trtp.Tensor,
    p_out_bias: trtp.Tensor,
    g_out_weight: trtp.Tensor,
    g_out_bias: trtp.Tensor,
    direction: str,
    eps: float,
    precision: int,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    _tri_mul_update_impl(
        stream,
        direction,
        eps,
        precision,
        outputs[0],
        x,
        mask,
        norm_in_weight,
        norm_in_bias,
        p_in_weight,
        None,
        g_in_weight,
        None,
        norm_out_weight,
        norm_out_bias,
        p_out_weight,
        p_out_bias,
        g_out_weight,
        g_out_bias,
    )


@trtp.impl("cuequivariance::tri_mul_update_noin_bias_noout_bias")
def _(
    x: trtp.Tensor,
    mask: trtp.Tensor,
    norm_in_weight: trtp.Tensor,
    norm_in_bias: trtp.Tensor,
    p_in_weight: trtp.Tensor,
    g_in_weight: trtp.Tensor,
    norm_out_weight: trtp.Tensor,
    norm_out_bias: trtp.Tensor,
    p_out_weight: trtp.Tensor,
    g_out_weight: trtp.Tensor,
    direction: str,
    eps: float,
    precision: int,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    _tri_mul_update_impl(
        stream,
        direction,
        eps,
        precision,
        outputs[0],
        x,
        mask,
        norm_in_weight,
        norm_in_bias,
        p_in_weight,
        None,
        g_in_weight,
        None,
        norm_out_weight,
        norm_out_bias,
        p_out_weight,
        None,
        g_out_weight,
        None,
    )


@trtp.impl("cuequivariance::tri_mul_update_nomask")
def _(
    x: trtp.Tensor,
    norm_in_weight: trtp.Tensor,
    norm_in_bias: trtp.Tensor,
    p_in_weight: trtp.Tensor,
    p_in_bias: trtp.Tensor,
    g_in_weight: trtp.Tensor,
    g_in_bias: trtp.Tensor,
    norm_out_weight: trtp.Tensor,
    norm_out_bias: trtp.Tensor,
    p_out_weight: trtp.Tensor,
    p_out_bias: trtp.Tensor,
    g_out_weight: trtp.Tensor,
    g_out_bias: trtp.Tensor,
    direction: str,
    eps: float,
    precision: int,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    _tri_mul_update_impl(
        stream,
        direction,
        eps,
        precision,
        outputs[0],
        x,
        None,
        norm_in_weight,
        norm_in_bias,
        p_in_weight,
        p_in_bias,
        g_in_weight,
        g_in_bias,
        norm_out_weight,
        norm_out_bias,
        p_out_weight,
        p_out_bias,
        g_out_weight,
        g_out_bias,
    )


@trtp.impl("cuequivariance::tri_mul_update_nomask_noin_bias")
def _(
    x: trtp.Tensor,
    norm_in_weight: trtp.Tensor,
    norm_in_bias: trtp.Tensor,
    p_in_weight: trtp.Tensor,
    g_in_weight: trtp.Tensor,
    norm_out_weight: trtp.Tensor,
    norm_out_bias: trtp.Tensor,
    p_out_weight: trtp.Tensor,
    p_out_bias: trtp.Tensor,
    g_out_weight: trtp.Tensor,
    g_out_bias: trtp.Tensor,
    direction: str,
    eps: float,
    precision: int,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    _tri_mul_update_impl(
        stream,
        direction,
        eps,
        precision,
        outputs[0],
        x,
        None,
        norm_in_weight,
        norm_in_bias,
        p_in_weight,
        None,
        g_in_weight,
        None,
        norm_out_weight,
        norm_out_bias,
        p_out_weight,
        p_out_bias,
        g_out_weight,
        g_out_bias,
    )


@trtp.impl("cuequivariance::tri_mul_update_nomask_noout_bias")
def _(
    x: trtp.Tensor,
    norm_in_weight: trtp.Tensor,
    norm_in_bias: trtp.Tensor,
    p_in_weight: trtp.Tensor,
    p_in_bias: trtp.Tensor,
    g_in_weight: trtp.Tensor,
    g_in_bias: trtp.Tensor,
    norm_out_weight: trtp.Tensor,
    norm_out_bias: trtp.Tensor,
    p_out_weight: trtp.Tensor,
    g_out_weight: trtp.Tensor,
    direction: str,
    eps: float,
    precision: int,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    _tri_mul_update_impl(
        stream,
        direction,
        eps,
        precision,
        outputs[0],
        x,
        None,
        norm_in_weight,
        norm_in_bias,
        p_in_weight,
        p_in_bias,
        g_in_weight,
        g_in_bias,
        norm_out_weight,
        norm_out_bias,
        p_out_weight,
        None,
        g_out_weight,
        None,
    )


@trtp.impl("cuequivariance::tri_mul_update_nomask_noin_bias_noout_bias")
def _(
    x: trtp.Tensor,
    norm_in_weight: trtp.Tensor,
    norm_in_bias: trtp.Tensor,
    p_in_weight: trtp.Tensor,
    g_in_weight: trtp.Tensor,
    norm_out_weight: trtp.Tensor,
    norm_out_bias: trtp.Tensor,
    p_out_weight: trtp.Tensor,
    g_out_weight: trtp.Tensor,
    direction: str,
    eps: float,
    precision: int,
    outputs: Tuple[trtp.Tensor],
    stream: int,
):
    _tri_mul_update_impl(
        stream,
        direction,
        eps,
        precision,
        outputs[0],
        x,
        None,
        norm_in_weight,
        norm_in_bias,
        p_in_weight,
        None,
        g_in_weight,
        None,
        norm_out_weight,
        norm_out_bias,
        p_out_weight,
        None,
        g_out_weight,
        None,
    )


"""
try:
    from torch_tensorrt.dynamo.conversion.plugins import generate_plugin_converter

    generate_plugin_converter(
        "cuequivariance::triangle_attention", supports_dynamic_shapes=True
    )
    generate_plugin_converter(
        "cuequivariance::triangle_attention_mask", supports_dynamic_shapes=True
    )
    generate_plugin_converter(
        "cuequivariance::triangle_attention_nomask", supports_dynamic_shapes=True
    )
except Exception as e:
    raise e
"""
