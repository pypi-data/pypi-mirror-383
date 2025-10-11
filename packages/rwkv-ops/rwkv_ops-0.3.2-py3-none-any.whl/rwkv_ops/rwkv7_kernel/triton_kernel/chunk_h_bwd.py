# -*- coding: utf-8 -*-
# Copyright (c) 2023-2025, Songlin Yang, Yu Zhang


import triton
import triton.language as tl

from ..triton_kernel.utils import exp, use_cuda_graph


@triton.heuristics(
    {
        "USE_FINAL_STATE_GRADIENT": lambda args: args["dht"] is not None,
        "USE_INITIAL_STATE": lambda args: args["dh0"] is not None,
    }
)
@triton.autotune(
    configs=[
        triton.Config({}, num_warps=num_warps, num_stages=num_stages)
        for num_warps in [2, 4, 8, 16, 32]
        for num_stages in [2, 3, 4]
    ],
    key=["BT", "BK", "BV", "V"],
    use_cuda_graph=use_cuda_graph,
)
@triton.jit(do_not_specialize=["T"])
def chunk_dplr_bwd_kernel_dhu(
    qg,
    bg,
    w,
    gk,
    dht,
    dv,
    do,
    T,
    dh,
    dh0,
    dv2,
    H: tl.constexpr,
    K: tl.constexpr,
    V: tl.constexpr,
    BT: tl.constexpr,
    BC: tl.constexpr,
    BK: tl.constexpr,
    BV: tl.constexpr,
    USE_FINAL_STATE_GRADIENT: tl.constexpr,
    USE_INITIAL_STATE: tl.constexpr,
):
    i_k, i_v, i_nh = tl.program_id(0), tl.program_id(1), tl.program_id(2)
    i_n, i_h = i_nh // H, i_nh % H
    if False:
        bos, eos = (
            tl.load(cu_seqlens + i_n).to(tl.int32),
            tl.load(cu_seqlens + i_n + 1).to(tl.int32),
        )
        T = eos - bos
        NT = tl.cdiv(T, BT)
        boh = tl.load(chunk_offsets + i_n).to(tl.int32)
    else:
        bos, eos = i_n * T, i_n * T + T
        NT = tl.cdiv(T, BT)
        boh = i_n * NT

    # [BK, BV]
    b_dh = tl.zeros([BK, BV], dtype=tl.float32)
    if USE_FINAL_STATE_GRADIENT:
        p_dht = tl.make_block_ptr(
            dht + i_nh * K * V, (K, V), (V, 1), (i_k * BK, i_v * BV), (BK, BV), (1, 0)
        )
        b_dh += tl.load(p_dht, boundary_check=(0, 1))

    mask_k = tl.arange(0, BK) < K
    for i_t in range(NT - 1, -1, -1):
        p_dh = tl.make_block_ptr(
            dh + ((boh + i_t) * H + i_h) * K * V,
            (K, V),
            (V, 1),
            (i_k * BK, i_v * BV),
            (BK, BV),
            (1, 0),
        )
        tl.store(p_dh, b_dh.to(p_dh.dtype.element_ty), boundary_check=(0, 1))
        b_dh_tmp = tl.zeros([BK, BV], dtype=tl.float32)
        for i_c in range(tl.cdiv(BT, BC) - 1, -1, -1):
            p_qg = tl.make_block_ptr(
                qg + (bos * H + i_h) * K,
                (K, T),
                (1, H * K),
                (i_k * BK, i_t * BT + i_c * BC),
                (BK, BC),
                (0, 1),
            )
            p_bg = tl.make_block_ptr(
                bg + (bos * H + i_h) * K,
                (T, K),
                (H * K, 1),
                (i_t * BT + i_c * BC, i_k * BK),
                (BC, BK),
                (1, 0),
            )
            p_w = tl.make_block_ptr(
                w + (bos * H + i_h) * K,
                (K, T),
                (1, H * K),
                (i_k * BK, i_t * BT + i_c * BC),
                (BK, BC),
                (0, 1),
            )
            p_dv = tl.make_block_ptr(
                dv + (bos * H + i_h) * V,
                (T, V),
                (H * V, 1),
                (i_t * BT + i_c * BC, i_v * BV),
                (BC, BV),
                (1, 0),
            )
            p_do = tl.make_block_ptr(
                do + (bos * H + i_h) * V,
                (T, V),
                (H * V, 1),
                (i_t * BT + i_c * BC, i_v * BV),
                (BC, BV),
                (1, 0),
            )
            p_dv2 = tl.make_block_ptr(
                dv2 + (bos * H + i_h) * V,
                (T, V),
                (H * V, 1),
                (i_t * BT + i_c * BC, i_v * BV),
                (BC, BV),
                (1, 0),
            )
            # [BK, BT]
            b_qg = tl.load(p_qg, boundary_check=(0, 1))
            # [BT, BK]
            b_bg = tl.load(p_bg, boundary_check=(0, 1))
            b_w = tl.load(p_w, boundary_check=(0, 1))
            # [BT, V]
            b_do = tl.load(p_do, boundary_check=(0, 1))
            b_dv = tl.load(p_dv, boundary_check=(0, 1))
            b_dv2 = b_dv + tl.dot(b_bg, b_dh.to(b_bg.dtype))
            tl.store(p_dv2, b_dv2.to(p_dv.dtype.element_ty), boundary_check=(0, 1))
            # [BK, BV]
            b_dh_tmp += tl.dot(b_qg, b_do.to(b_qg.dtype))
            b_dh_tmp += tl.dot(b_w, b_dv2.to(b_qg.dtype))
        last_idx = min((i_t + 1) * BT, T) - 1
        bg_last = tl.load(
            gk + ((bos + last_idx) * H + i_h) * K + tl.arange(0, BK), mask=mask_k
        )
        b_dh *= exp(bg_last)[:, None]
        b_dh += b_dh_tmp

    if USE_INITIAL_STATE:
        p_dh0 = tl.make_block_ptr(
            dh0 + i_nh * K * V, (K, V), (V, 1), (i_k * BK, i_v * BV), (BK, BV), (1, 0)
        )
        tl.store(p_dh0, b_dh.to(p_dh0.dtype.element_ty), boundary_check=(0, 1))
