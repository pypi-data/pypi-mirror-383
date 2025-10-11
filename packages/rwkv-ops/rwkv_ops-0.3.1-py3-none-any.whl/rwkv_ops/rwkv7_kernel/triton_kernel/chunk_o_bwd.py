# -*- coding: utf-8 -*-
# Copyright (c) 2023-2025, Songlin Yang, Yu Zhang


import triton
import triton.language as tl

from ..triton_kernel.utils import (
    exp,
    check_shared_mem,
    use_cuda_graph,
)

BK_LIST = [32, 64, 128] if check_shared_mem() else [16, 32]


@triton.autotune(
    configs=[
        triton.Config({}, num_warps=num_warps, num_stages=num_stages)
        for num_warps in [2, 4, 8, 16, 32]
        for num_stages in [2, 3, 4]
    ],
    key=["BV", "BT"],
    use_cuda_graph=use_cuda_graph,
)
@triton.jit(do_not_specialize=["T"])
def chunk_dplr_bwd_kernel_dAu(
    v,
    do,
    v_new,
    A_qb,
    T,
    dA_qk,
    dA_qb,
    dv_new,
    scale: tl.constexpr,
    H: tl.constexpr,
    V: tl.constexpr,
    BT: tl.constexpr,
    BV: tl.constexpr,
):
    i_t, i_bh = tl.program_id(0), tl.program_id(1)
    i_b, i_h = i_bh // H, i_bh % H
    if False:
        i_n, i_t = (
            tl.load(chunk_indices + i_t * 2).to(tl.int32),
            tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32),
        )
        bos, eos = (
            tl.load(cu_seqlens + i_n).to(tl.int32),
            tl.load(cu_seqlens + i_n + 1).to(tl.int32),
        )
    else:
        bos, eos = i_b * T, i_b * T + T
    T = eos - bos

    b_dA_qk = tl.zeros([BT, BT], dtype=tl.float32)
    b_dA_qb = tl.zeros([BT, BT], dtype=tl.float32)

    p_A_qb = tl.make_block_ptr(
        A_qb + (bos * H + i_h) * BT,
        (T, BT),
        (H * BT, 1),
        (i_t * BT, 0),
        (BT, BT),
        (1, 0),
    )

    b_A_qb = tl.load(p_A_qb, boundary_check=(0, 1))
    # causal mask
    b_A_qb = tl.where(
        tl.arange(0, BT)[:, None] >= tl.arange(0, BT)[None, :], b_A_qb, 0.0
    ).to(b_A_qb.dtype)

    for i_v in range(tl.cdiv(V, BV)):
        p_do = tl.make_block_ptr(
            do + (bos * H + i_h) * V,
            (T, V),
            (H * V, 1),
            (i_t * BT, i_v * BV),
            (BT, BV),
            (1, 0),
        )
        p_v = tl.make_block_ptr(
            v + (bos * H + i_h) * V,
            (V, T),
            (1, H * V),
            (i_v * BV, i_t * BT),
            (BV, BT),
            (0, 1),
        )
        p_v_new = tl.make_block_ptr(
            v_new + (bos * H + i_h) * V,
            (V, T),
            (1, H * V),
            (i_v * BV, i_t * BT),
            (BV, BT),
            (0, 1),
        )
        p_dv_new = tl.make_block_ptr(
            dv_new + (bos * H + i_h) * V,
            (T, V),
            (H * V, 1),
            (i_t * BT, i_v * BV),
            (BT, BV),
            (1, 0),
        )
        b_v = tl.load(p_v, boundary_check=(0, 1))
        b_do = tl.load(p_do, boundary_check=(0, 1))
        b_v_new = tl.load(p_v_new, boundary_check=(0, 1))
        b_dA_qk += tl.dot(b_do, b_v)
        b_dA_qb += tl.dot(b_do, b_v_new)
        b_dv_new = tl.dot(tl.trans(b_A_qb), b_do)
        # for recurrent
        tl.store(
            p_dv_new, b_dv_new.to(p_dv_new.dtype.element_ty), boundary_check=(0, 1)
        )

    p_dA_qk = tl.make_block_ptr(
        dA_qk + (bos * H + i_h) * BT,
        (T, BT),
        (H * BT, 1),
        (i_t * BT, 0),
        (BT, BT),
        (1, 0),
    )
    p_dA_qb = tl.make_block_ptr(
        dA_qb + (bos * H + i_h) * BT,
        (T, BT),
        (H * BT, 1),
        (i_t * BT, 0),
        (BT, BT),
        (1, 0),
    )
    m_s = tl.arange(0, BT)[:, None] >= tl.arange(0, BT)[None, :]
    b_dA_qk = tl.where(m_s, b_dA_qk * scale, 0.0)
    tl.store(p_dA_qk, b_dA_qk.to(p_dA_qk.dtype.element_ty), boundary_check=(0, 1))
    b_dA_qb = tl.where(m_s, b_dA_qb * scale, 0.0)
    tl.store(p_dA_qb, b_dA_qb.to(p_dA_qb.dtype.element_ty), boundary_check=(0, 1))


@triton.autotune(
    configs=[
        triton.Config({}, num_warps=num_warps, num_stages=num_stages)
        for num_warps in [2, 4, 8, 16, 32]
        for num_stages in [2, 3, 4]
    ],
    key=["BT", "BK", "BV"],
    use_cuda_graph=use_cuda_graph,
)
@triton.jit
def chunk_dplr_bwd_o_kernel(
    v,
    v_new,
    h,
    do,
    dh,
    w,
    dv,
    gk,
    k,
    b,
    T,
    dq,
    dk,
    dw,
    db,
    dgk_last,
    H: tl.constexpr,
    K: tl.constexpr,
    V: tl.constexpr,
    BT: tl.constexpr,
    BK: tl.constexpr,
    BV: tl.constexpr,
):
    i_k, i_t, i_bh = tl.program_id(0), tl.program_id(1), tl.program_id(2)
    i_b, i_h = i_bh // H, i_bh % H

    if False:
        i_tg = i_t
        i_n, i_t = (
            tl.load(chunk_indices + i_t * 2).to(tl.int32),
            tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32),
        )
        bos, eos = (
            tl.load(cu_seqlens + i_n).to(tl.int32),
            tl.load(cu_seqlens + i_n + 1).to(tl.int32),
        )
        T = eos - bos
        NT = tl.cdiv(T, BT)
    else:
        NT = tl.cdiv(T, BT)
        i_tg = i_b * NT + i_t
        bos, eos = i_b * T, i_b * T + T

    # offset calculation
    v += (bos * H + i_h) * V
    v_new += (bos * H + i_h) * V
    do += (bos * H + i_h) * V
    h += (i_tg * H + i_h) * K * V
    dh += (i_tg * H + i_h) * K * V
    dk += (bos * H + i_h) * K
    k += (bos * H + i_h) * K
    db += (bos * H + i_h) * K
    b += (bos * H + i_h) * K
    dw += (bos * H + i_h) * K
    dv += (bos * H + i_h) * V
    dq += (bos * H + i_h) * K
    w += (bos * H + i_h) * K

    dgk_last += (i_tg * H + i_h) * K
    gk += (bos * H + i_h) * K

    stride_qk = H * K
    stride_vo = H * V

    b_dq = tl.zeros([BT, BK], dtype=tl.float32)
    b_dk = tl.zeros([BT, BK], dtype=tl.float32)
    b_dw = tl.zeros([BT, BK], dtype=tl.float32)
    b_db = tl.zeros([BT, BK], dtype=tl.float32)
    b_dgk_last = tl.zeros([BK], dtype=tl.float32)

    for i_v in range(tl.cdiv(V, BV)):
        p_v = tl.make_block_ptr(
            v, (T, V), (stride_vo, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0)
        )
        p_v_new = tl.make_block_ptr(
            v_new, (T, V), (stride_vo, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0)
        )
        p_do = tl.make_block_ptr(
            do, (T, V), (stride_vo, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0)
        )
        p_h = tl.make_block_ptr(
            h, (V, K), (1, V), (i_v * BV, i_k * BK), (BV, BK), (0, 1)
        )
        p_dh = tl.make_block_ptr(
            dh, (V, K), (1, V), (i_v * BV, i_k * BK), (BV, BK), (0, 1)
        )
        # [BT, BV]
        b_v = tl.load(p_v, boundary_check=(0, 1))
        b_v_new = tl.load(p_v_new, boundary_check=(0, 1))
        b_do = tl.load(p_do, boundary_check=(0, 1))
        # [BV, BK]
        b_h = tl.load(p_h, boundary_check=(0, 1))
        b_dh = tl.load(p_dh, boundary_check=(0, 1))
        b_dgk_last += tl.sum((b_h * b_dh).to(tl.float32), axis=0)

        # [BT, BV] @ [BV, BK] -> [BT, BK]
        b_dq += tl.dot(b_do, b_h.to(b_do.dtype))
        # [BT, BV] @ [BV, BK] -> [BT, BK]
        b_dk += tl.dot(b_v, b_dh.to(b_v.dtype))
        b_db += tl.dot(b_v_new, b_dh.to(b_v_new.dtype))
        p_dv = tl.make_block_ptr(
            dv, (T, V), (stride_vo, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0)
        )
        b_dv = tl.load(p_dv, boundary_check=(0, 1))
        b_dw += tl.dot(b_dv.to(b_v.dtype), b_h.to(b_v.dtype))

    m_k = (i_k * BK + tl.arange(0, BK)) < K
    last_idx = min(i_t * BT + BT, T) - 1
    b_gk_last = tl.load(
        gk + last_idx * stride_qk + i_k * BK + tl.arange(0, BK),
        mask=m_k,
        other=float("-inf"),
    )
    b_dgk_last *= exp(b_gk_last)
    p_k = tl.make_block_ptr(
        k, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0)
    )
    p_b = tl.make_block_ptr(
        b, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0)
    )
    b_k = tl.load(p_k, boundary_check=(0, 1))
    b_b = tl.load(p_b, boundary_check=(0, 1))
    b_dgk_last += tl.sum(b_k * b_dk, axis=0)
    b_dgk_last += tl.sum(b_b * b_db, axis=0)
    tl.store(dgk_last + tl.arange(0, BK) + i_k * BK, b_dgk_last, mask=m_k)

    p_dw = tl.make_block_ptr(
        dw, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0)
    )
    p_dk = tl.make_block_ptr(
        dk, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0)
    )
    p_db = tl.make_block_ptr(
        db, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0)
    )
    p_dq = tl.make_block_ptr(
        dq, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0)
    )
    tl.store(p_dw, b_dw.to(p_dw.dtype.element_ty), boundary_check=(0, 1))
    tl.store(p_dk, b_dk.to(p_dk.dtype.element_ty), boundary_check=(0, 1))
    tl.store(p_db, b_db.to(p_db.dtype.element_ty), boundary_check=(0, 1))
    tl.store(p_dq, b_dq.to(p_dq.dtype.element_ty), boundary_check=(0, 1))


@triton.autotune(
    configs=[
        triton.Config({"BK": BK, "BV": BV}, num_warps=num_warps, num_stages=num_stages)
        for num_warps in [2, 4, 8, 16, 32]
        for num_stages in [2, 3, 4]
        for BK in BK_LIST
        for BV in BK_LIST
    ],
    key=["BT"],
    use_cuda_graph=use_cuda_graph,
)
@triton.jit
def chunk_dplr_bwd_kernel_dv(
    A_qk,
    kg,
    do,
    dh,
    T,
    dv,
    H: tl.constexpr,
    K: tl.constexpr,
    V: tl.constexpr,
    BT: tl.constexpr,
    BK: tl.constexpr,
    BV: tl.constexpr,
):
    i_v, i_t, i_bh = tl.program_id(0), tl.program_id(1), tl.program_id(2)
    i_b, i_h = i_bh // H, i_bh % H
    if False:
        i_tg = i_t
        i_n, i_t = (
            tl.load(chunk_indices + i_t * 2).to(tl.int32),
            tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32),
        )
        bos, eos = (
            tl.load(cu_seqlens + i_n).to(tl.int32),
            tl.load(cu_seqlens + i_n + 1).to(tl.int32),
        )
        T = eos - bos
        NT = tl.cdiv(T, BT)
    else:
        NT = tl.cdiv(T, BT)
        i_tg = i_b * NT + i_t
        bos, eos = i_b * T, i_b * T + T

    b_dv = tl.zeros([BT, BV], dtype=tl.float32)

    # offset calculation
    A_qk += (bos * H + i_h) * BT
    do += (bos * H + i_h) * V
    dv += (bos * H + i_h) * V
    kg += (bos * H + i_h) * K
    dh += (i_tg * H + i_h) * K * V

    stride_qk = H * K
    stride_vo = H * V
    stride_A = H * BT

    for i_k in range(tl.cdiv(K, BK)):
        p_dh = tl.make_block_ptr(
            dh, (K, V), (V, 1), (i_k * BK, i_v * BV), (BK, BV), (1, 0)
        )
        p_kg = tl.make_block_ptr(
            kg, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0)
        )
        b_dh = tl.load(p_dh, boundary_check=(0, 1))
        b_kg = tl.load(p_kg, boundary_check=(0, 1))
        b_dv += tl.dot(b_kg, b_dh.to(b_kg.dtype))

    p_Aqk = tl.make_block_ptr(
        A_qk, (BT, T), (1, stride_A), (0, i_t * BT), (BT, BT), (0, 1)
    )
    b_A = tl.where(
        tl.arange(0, BT)[:, None] <= tl.arange(0, BT)[None, :],
        tl.load(p_Aqk, boundary_check=(0, 1)),
        0,
    )
    p_do = tl.make_block_ptr(
        do, (T, V), (stride_vo, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0)
    )
    p_dv = tl.make_block_ptr(
        dv, (T, V), (stride_vo, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0)
    )
    b_do = tl.load(p_do, boundary_check=(0, 1))
    b_dv += tl.dot(b_A.to(b_do.dtype), b_do)
    tl.store(p_dv, b_dv.to(p_dv.dtype.element_ty), boundary_check=(0, 1))
