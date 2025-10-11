# -*- coding: utf-8 -*-
# Copyright (c) 2023-2025, Songlin Yang, Yu Zhang


import triton
import triton.language as tl

from ..triton_kernel.utils import exp, gather, use_cuda_graph


@triton.autotune(
    configs=[
        triton.Config({}, num_warps=num_warps, num_stages=num_stages)
        for num_warps in [2, 4, 8, 16, 32]
        for num_stages in [2, 3, 4]
    ],
    key=["BK", "BT", "K"],
    use_cuda_graph=use_cuda_graph,
)
@triton.jit(do_not_specialize=["T"])
def chunk_dplr_bwd_kernel_intra(
    q,
    k,
    a,
    b,
    gi,
    ge,
    dAqk,
    dAqb,
    dAak,
    dAab,
    dqg,
    dkg,
    dag,
    dbg,
    T,
    dq,
    dk,
    da,
    db,
    dgk,
    dgk_offset,
    scale: tl.constexpr,
    H: tl.constexpr,
    K: tl.constexpr,
    BT: tl.constexpr,
    BC: tl.constexpr,
    BK: tl.constexpr,
    GATHER_SUPPORTED: tl.constexpr,
):
    i_k, i_t, i_bh = tl.program_id(0), tl.program_id(1), tl.program_id(2)
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
        T = eos - bos
    else:
        bos, eos = (i_b * T).to(tl.int32), (i_b * T + T).to(tl.int32)

    if i_t * BT >= T:
        return

    # offset calculation
    ge += (bos * H + i_h) * K
    gi += (bos * H + i_h) * K
    q += (bos * H + i_h) * K
    a += (bos * H + i_h) * K
    b += (bos * H + i_h) * K
    k += (bos * H + i_h) * K
    dq += (bos * H + i_h) * K
    dk += (bos * H + i_h) * K
    da += (bos * H + i_h) * K
    db += (bos * H + i_h) * K
    dqg += (bos * H + i_h) * K
    dag += (bos * H + i_h) * K
    dkg += (bos * H + i_h) * K
    dbg += (bos * H + i_h) * K
    dgk += (bos * H + i_h) * K
    dgk_offset += (bos * H + i_h) * K
    dAqk += (bos * H + i_h) * BT
    dAqb += (bos * H + i_h) * BT
    dAak += (bos * H + i_h) * BT
    dAab += (bos * H + i_h) * BT

    stride_qk = H * K
    stride_A = H * BT

    p_ge = tl.make_block_ptr(
        ge, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_gi = tl.make_block_ptr(
        gi, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    # [BC, BK]
    b_ge = tl.load(p_ge, boundary_check=(0, 1))
    b_gi = tl.load(p_gi, boundary_check=(0, 1))
    b_dq = tl.zeros([BC, BK], dtype=tl.float32)
    b_da = tl.zeros([BC, BK], dtype=tl.float32)
    b_dk = tl.zeros([BC, BK], dtype=tl.float32)
    b_db = tl.zeros([BC, BK], dtype=tl.float32)
    # intra chunk gradient calculation
    p_dAqk = tl.make_block_ptr(
        dAqk, (T, BT), (stride_A, 1), (i_t * BT, 0), (BC, BC), (1, 0)
    )
    p_dAab = tl.make_block_ptr(
        dAab, (T, BT), (stride_A, 1), (i_t * BT, 0), (BC, BC), (1, 0)
    )
    p_dAqb = tl.make_block_ptr(
        dAqb, (T, BT), (stride_A, 1), (i_t * BT, 0), (BC, BC), (1, 0)
    )
    p_dAak = tl.make_block_ptr(
        dAak, (T, BT), (stride_A, 1), (i_t * BT, 0), (BC, BC), (1, 0)
    )
    o_i = tl.arange(0, BC)
    p_k = tl.make_block_ptr(
        k, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_b = tl.make_block_ptr(
        b, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_a = tl.make_block_ptr(
        a, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_q = tl.make_block_ptr(
        q, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    b_k = tl.load(p_k, boundary_check=(0, 1))
    b_b = tl.load(p_b, boundary_check=(0, 1))
    b_q = tl.load(p_q, boundary_check=(0, 1))
    b_a = tl.load(p_a, boundary_check=(0, 1))
    b_dAqk = tl.load(p_dAqk, boundary_check=(0, 1))
    b_dAab = tl.load(p_dAab, boundary_check=(0, 1))
    b_dAqb = tl.load(p_dAqb, boundary_check=(0, 1))
    b_dAak = tl.load(p_dAak, boundary_check=(0, 1))

    # inter chunk gradient calculation
    o_k = i_k * BK + tl.arange(0, BK)
    m_k = o_k < K
    # intra chunk gradient calculation
    for j in range(0, min(BC, T - i_t * BT)):
        # trick to index the block
        if GATHER_SUPPORTED:
            row_idx = tl.full([1, BK], j, dtype=tl.int16)
            col_idx = tl.full([BC, 1], j, dtype=tl.int16)
            row_idx_bc = tl.full([1, BC], j, dtype=tl.int16)
            # [1, BK]
            b_kj = gather(b_k, row_idx, axis=0)
            b_bj = gather(b_b, row_idx, axis=0)
            b_gij = gather(b_gi, row_idx, axis=0)
            b_gej = gather(b_ge, row_idx, axis=0)
            b_qj = gather(b_q, row_idx, axis=0)
            b_aj = gather(b_a, row_idx, axis=0)
            # [BC, 1]
            b_dAqk_j = gather(b_dAqk, col_idx, axis=1)
            b_dAab_j = gather(b_dAab, col_idx, axis=1)
            b_dAqb_j = gather(b_dAqb, col_idx, axis=1)
            b_dAak_j = gather(b_dAak, col_idx, axis=1)
            # [1, BC] -> [BC, 1]
            b_dA_qk_j = tl.sum(gather(b_dAqk, row_idx_bc, axis=0), 0)[:, None]
            b_dA_qk_j = tl.sum(gather(b_dAqk, row_idx_bc, axis=0), 0)[:, None]
            b_dA_ab_j = tl.sum(gather(b_dAab, row_idx_bc, axis=0), 0)[:, None]
            b_dA_qb_j = tl.sum(gather(b_dAqb, row_idx_bc, axis=0), 0)[:, None]
            b_dA_ak_j = tl.sum(gather(b_dAak, row_idx_bc, axis=0), 0)[:, None]
        else:
            mask_idx = tl.arange(0, BC) == j
            b_kj = tl.sum(tl.where(mask_idx[:, None], b_k, 0), 0)[None, :]
            b_bj = tl.sum(tl.where(mask_idx[:, None], b_b, 0), 0)[None, :]
            b_gij = tl.sum(tl.where(mask_idx[:, None], b_gi, 0), 0)[None, :]
            b_gej = tl.sum(tl.where(mask_idx[:, None], b_ge, 0), 0)[None, :]
            b_dAqk_j = tl.sum(tl.where(mask_idx[None, :], b_dAqk, 0), 1)[:, None]
            b_dAab_j = tl.sum(tl.where(mask_idx[None, :], b_dAab, 0), 1)[:, None]
            b_dAqb_j = tl.sum(tl.where(mask_idx[None, :], b_dAqb, 0), 1)[:, None]
            b_dAak_j = tl.sum(tl.where(mask_idx[None, :], b_dAak, 0), 1)[:, None]
            b_dA_qk_j = tl.sum(tl.where(mask_idx[:, None], b_dAqk, 0), 0)[:, None]
            b_dA_ab_j = tl.sum(tl.where(mask_idx[:, None], b_dAab, 0), 0)[:, None]
            b_dA_qb_j = tl.sum(tl.where(mask_idx[:, None], b_dAqb, 0), 0)[:, None]
            b_dA_ak_j = tl.sum(tl.where(mask_idx[:, None], b_dAak, 0), 0)[:, None]
            # [1, BK] b_qj, b_aj
            b_qj = tl.sum(tl.where(mask_idx[:, None], b_q, 0), 0)[None, :]
            b_aj = tl.sum(tl.where(mask_idx[:, None], b_a, 0), 0)[None, :]

        m_e = o_i[:, None] > j
        m_i = o_i[:, None] >= j
        tmp1 = exp(b_gi - b_gij)
        tmp2 = exp(b_ge - b_gij)
        b_dq += tl.where(m_i, b_dAqk_j * b_kj * tmp1, 0.0)
        b_dq += tl.where(m_i, b_dAqb_j * b_bj * tmp1, 0.0)
        b_da += tl.where(m_e, b_dAab_j * b_bj * tmp2, 0.0)
        b_da += tl.where(m_e, b_dAak_j * b_kj * tmp2, 0.0)

        m_i = o_i[:, None] <= j
        m_e = o_i[:, None] < j
        tmp1 = exp(b_gij - b_gi)
        tmp2 = exp(b_gej - b_gi)
        b_dk += tl.where(m_i, b_dA_qk_j * b_qj * tmp1, 0.0)
        b_dk += tl.where(m_e, b_dA_ak_j * b_aj * tmp2, 0.0)
        b_db += tl.where(m_i, b_dA_qb_j * b_qj * tmp1, 0.0)
        b_db += tl.where(m_e, b_dA_ab_j * b_aj * tmp2, 0.0)

    # post processing
    p_dq = tl.make_block_ptr(
        dq, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_dk = tl.make_block_ptr(
        dk, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_da = tl.make_block_ptr(
        da, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_db = tl.make_block_ptr(
        db, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_dgk = tl.make_block_ptr(
        dgk, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_dgk_offset = tl.make_block_ptr(
        dgk_offset, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_dqg = tl.make_block_ptr(
        dqg, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_dkg = tl.make_block_ptr(
        dkg, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_dag = tl.make_block_ptr(
        dag, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_dbg = tl.make_block_ptr(
        dbg, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BC, BK), (1, 0)
    )
    p_gn = gi + (min(i_t * BT + BT, T) - 1) * stride_qk + o_k
    p_gn = tl.max_contiguous(tl.multiple_of(p_gn, BK), BK)
    b_gn = tl.load(p_gn, mask=m_k, other=0)
    b_da += tl.load(p_dag, boundary_check=(0, 1)) * exp(b_ge)
    b_dq += tl.load(p_dqg, boundary_check=(0, 1)) * exp(b_gi) * scale
    tmp = exp(b_gn[None, :] - b_gi)
    b_dk += tl.load(p_dkg, boundary_check=(0, 1)).to(tl.float32) * tmp
    b_db += tl.load(p_dbg, boundary_check=(0, 1)).to(tl.float32) * tmp
    tl.store(p_dq, (b_dq).to(p_dq.dtype.element_ty), boundary_check=(0, 1))
    tl.store(p_dk, b_dk.to(p_dk.dtype.element_ty), boundary_check=(0, 1))
    tl.store(p_da, b_da.to(p_da.dtype.element_ty), boundary_check=(0, 1))
    tl.store(p_db, b_db.to(p_db.dtype.element_ty), boundary_check=(0, 1))
    b_dgk = (b_dq * b_q + b_da * b_a - b_dk * b_k - b_db * b_b).to(tl.float32)
    b_dgk_offset = b_da * b_a
    tl.store(p_dgk, b_dgk.to(p_dgk.dtype.element_ty), boundary_check=(0, 1))
    tl.store(
        p_dgk_offset,
        b_dgk_offset.to(p_dgk_offset.dtype.element_ty),
        boundary_check=(0, 1),
    )


@triton.autotune(
    configs=[
        triton.Config({"BK": BK}, num_warps=num_warps, num_stages=num_stages)
        for num_warps in [2, 4, 8, 16, 32]
        for num_stages in [2, 3, 4]
        for BK in [32, 64]
    ],
    key=["BK", "BT", "K"],
    use_cuda_graph=use_cuda_graph,
)
@triton.jit(do_not_specialize=["T"])
def chunk_dplr_bwd_dgk_kernel(
    dgk,
    dgk_offset,
    dgk_last,
    T,
    dgk_output,
    H: tl.constexpr,
    K: tl.constexpr,
    BT: tl.constexpr,
    BK: tl.constexpr,
):
    i_t, i_k, i_bh = tl.program_id(0), tl.program_id(1), tl.program_id(2)
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
        i_tg = (i_b * NT + i_t).to(tl.int32)
        bos, eos = (i_b * T).to(tl.int32), (i_b * T + T).to(tl.int32)

    stride_qk = H * K
    dgk += (bos * H + i_h) * K
    dgk_offset += (bos * H + i_h) * K
    dgk_last += (i_tg * H + i_h) * K
    dgk_output += (bos * H + i_h) * K
    p_dgk_last = dgk_last + tl.arange(0, BK) + i_k * BK
    m_k = tl.arange(0, BK) + i_k * BK < K
    b_dgk_last = tl.load(p_dgk_last, mask=m_k, other=0)
    p_dgk_offset = tl.make_block_ptr(
        dgk_offset, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0)
    )
    p_dgk = tl.make_block_ptr(
        dgk, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0)
    )
    b_dgk = tl.load(p_dgk, boundary_check=(0, 1))
    b_dgk_offset = tl.load(p_dgk_offset, boundary_check=(0, 1))
    # m_inv_cumsum = (tl.arange(0, BT)[:, None] <= tl.arange(0, BT)[None, :]).to(tl.float32)
    # b_dgk_cumsum = tl.dot(m_inv_cumsum, b_dgk, allow_tf32=False)
    b_dgk_cumsum = tl.cumsum(b_dgk, 0, reverse=True)
    b_dgk_cumsum += b_dgk_last[None, :]
    b_dgk_cumsum -= b_dgk_offset
    p_dgk_output = tl.make_block_ptr(
        dgk_output, (T, K), (stride_qk, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0)
    )
    tl.store(
        p_dgk_output,
        b_dgk_cumsum.to(p_dgk_output.dtype.element_ty),
        boundary_check=(0, 1),
    )
