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

import torch

import cuequivariance_ops_torch as cops

NS = "cuequivariance"

torch_ops = getattr(torch.ops, NS)

__all__ = []

try:
    import onnxscript
    from onnxscript import BOOL, FLOAT, INT64
    from onnxscript import opset20 as op

    _onnx_opset = onnxscript.values.Opset(NS, version=1)

    @onnxscript.script(_onnx_opset)
    def _identity_2(m: FLOAT, z: FLOAT) -> Tuple[FLOAT, FLOAT]:
        m, z = _onnx_opset.identity_2(m, z, plugin_namespace=NS)
        return m, z

    @onnxscript.script(_onnx_opset)
    def _triangle_attention(
        q: FLOAT, k: FLOAT, v: FLOAT, b: FLOAT, mask: BOOL, scale: float
    ) -> Tuple[FLOAT, FLOAT, FLOAT]:
        o, sm_lse, sm_max = _onnx_opset.triangle_attention(
            q, k, v, b, mask, scale=scale, plugin_namespace=NS
        )
        return o, sm_lse, sm_max

    @onnxscript.script(_onnx_opset)
    def _triangle_attention_mask(
        q: FLOAT, k: FLOAT, v: FLOAT, b: FLOAT, mask: BOOL, scale: float
    ) -> FLOAT:
        o = _onnx_opset.triangle_attention_mask(
            q, k, v, b, mask, scale=scale, plugin_namespace=NS
        )
        return o

    @onnxscript.script(_onnx_opset)
    def _triangle_attention_nomask(
        q: FLOAT, k: FLOAT, v: FLOAT, b: FLOAT, scale: float
    ) -> FLOAT:
        o = _onnx_opset.triangle_attention_nomask(
            q, k, v, b, scale=scale, plugin_namespace=NS
        )
        return o

    @onnxscript.script(_onnx_opset)
    def _layer_norm_transpose(
        x: FLOAT, w: FLOAT, b: FLOAT, eps: float, elementwise_affine: bool, layout: int
    ) -> Tuple[FLOAT, FLOAT, FLOAT]:
        out, mean, rst = _onnx_opset.layer_norm_transpose(
            x,
            w,
            b,
            eps=eps,
            elementwise_affine=elementwise_affine,
            layout=layout,
            plugin_namespace=NS,
        )
        return out, mean, rst

    @onnxscript.script(_onnx_opset)
    def _attention_pair_bias_mask(
        z: FLOAT,
        w_proj_z: FLOAT,
        w_ln: FLOAT,
        b_ln: FLOAT,
        mask: FLOAT,
        num_heads: int,
        multiplicity: int,
        eps: float,
        inf: float,
        is_cached_z_proj: bool,
    ) -> Tuple[FLOAT, FLOAT]:
        out_mask, z_proj = _onnx_opset.attention_pair_bias_mask(
            z,
            w_proj_z,
            w_ln,
            b_ln,
            mask,
            num_heads=num_heads,
            multiplicity=multiplicity,
            eps=eps,
            inf=inf,
            is_cached_z_proj=is_cached_z_proj,
        )
        return out_mask, z_proj

    @onnxscript.script(_onnx_opset)
    def _tri_mul_update(
        x: FLOAT,
        mask: BOOL,
        norm_in_weight: FLOAT,
        norm_in_bias: FLOAT,
        p_in_weight: FLOAT,
        p_in_bias: FLOAT,
        g_in_weight: FLOAT,
        g_in_bias: FLOAT,
        norm_out_weight: FLOAT,
        norm_out_bias: FLOAT,
        p_out_weight: FLOAT,
        p_out_bias: FLOAT,
        g_out_weight: FLOAT,
        g_out_bias: FLOAT,
        direction: str,
        eps: float,
        precision: int,
    ) -> FLOAT:
        return _onnx_opset.tri_mul_update(
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
            direction=direction,
            eps=eps,
            precision=precision,
            plugin_namespace=NS,
        )

    @onnxscript.script(_onnx_opset)
    def _tri_mul_update_noin_bias(
        x: FLOAT,
        mask: BOOL,
        norm_in_weight: FLOAT,
        norm_in_bias: FLOAT,
        p_in_weight: FLOAT,
        g_in_weight: FLOAT,
        norm_out_weight: FLOAT,
        norm_out_bias: FLOAT,
        p_out_weight: FLOAT,
        p_out_bias: FLOAT,
        g_out_weight: FLOAT,
        g_out_bias: FLOAT,
        direction: str,
        eps: float,
        precision: int,
    ) -> FLOAT:
        return _onnx_opset.tri_mul_update_noin_bias(
            x,
            mask,
            norm_in_weight,
            norm_in_bias,
            p_in_weight,
            g_in_weight,
            norm_out_weight,
            norm_out_bias,
            p_out_weight,
            p_out_bias,
            g_out_weight,
            g_out_bias,
            direction=direction,
            eps=eps,
            precision=precision,
            plugin_namespace=NS,
        )

    @onnxscript.script(_onnx_opset)
    def _tri_mul_update_noout_bias(
        x: FLOAT,
        mask: BOOL,
        norm_in_weight: FLOAT,
        norm_in_bias: FLOAT,
        p_in_weight: FLOAT,
        p_in_bias: FLOAT,
        g_in_weight: FLOAT,
        g_in_bias: FLOAT,
        norm_out_weight: FLOAT,
        norm_out_bias: FLOAT,
        p_out_weight: FLOAT,
        g_out_weight: FLOAT,
        direction: str,
        eps: float,
        precision: int,
    ) -> FLOAT:
        return _onnx_opset.tri_mul_update_noout_bias(
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
            g_out_weight,
            direction=direction,
            eps=eps,
            precision=precision,
            plugin_namespace=NS,
        )

    @onnxscript.script(_onnx_opset)
    def _tri_mul_update_noin_bias_noout_bias(
        x: FLOAT,
        mask: BOOL,
        norm_in_weight: FLOAT,
        norm_in_bias: FLOAT,
        p_in_weight: FLOAT,
        g_in_weight: FLOAT,
        norm_out_weight: FLOAT,
        norm_out_bias: FLOAT,
        p_out_weight: FLOAT,
        g_out_weight: FLOAT,
        direction: str,
        eps: float,
        precision: int,
    ) -> FLOAT:
        return _onnx_opset.tri_mul_update_noin_bias_noout_bias(
            x,
            mask,
            norm_in_weight,
            norm_in_bias,
            p_in_weight,
            g_in_weight,
            norm_out_weight,
            norm_out_bias,
            p_out_weight,
            g_out_weight,
            direction=direction,
            eps=eps,
            precision=precision,
            plugin_namespace=NS,
        )

    @onnxscript.script(_onnx_opset)
    def _tri_mul_update_nomask(
        x: FLOAT,
        norm_in_weight: FLOAT,
        norm_in_bias: FLOAT,
        p_in_weight: FLOAT,
        p_in_bias: FLOAT,
        g_in_weight: FLOAT,
        g_in_bias: FLOAT,
        norm_out_weight: FLOAT,
        norm_out_bias: FLOAT,
        p_out_weight: FLOAT,
        p_out_bias: FLOAT,
        g_out_weight: FLOAT,
        g_out_bias: FLOAT,
        direction: str,
        eps: float,
        precision: int,
    ) -> FLOAT:
        return _onnx_opset.tri_mul_update_nomask(
            x,
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
            direction=direction,
            eps=eps,
            precision=precision,
            plugin_namespace=NS,
        )

    @onnxscript.script(_onnx_opset)
    def _tri_mul_update_nomask_noin_bias(
        x: FLOAT,
        norm_in_weight: FLOAT,
        norm_in_bias: FLOAT,
        p_in_weight: FLOAT,
        g_in_weight: FLOAT,
        norm_out_weight: FLOAT,
        norm_out_bias: FLOAT,
        p_out_weight: FLOAT,
        p_out_bias: FLOAT,
        g_out_weight: FLOAT,
        g_out_bias: FLOAT,
        direction: str,
        eps: float,
        precision: int,
    ) -> FLOAT:
        return _onnx_opset.tri_mul_update_nomask_noin_bias(
            x,
            norm_in_weight,
            norm_in_bias,
            p_in_weight,
            g_in_weight,
            norm_out_weight,
            norm_out_bias,
            p_out_weight,
            p_out_bias,
            g_out_weight,
            g_out_bias,
            direction=direction,
            eps=eps,
            precision=precision,
            plugin_namespace=NS,
        )

    @onnxscript.script(_onnx_opset)
    def _tri_mul_update_nomask_noout_bias(
        x: FLOAT,
        norm_in_weight: FLOAT,
        norm_in_bias: FLOAT,
        p_in_weight: FLOAT,
        p_in_bias: FLOAT,
        g_in_weight: FLOAT,
        g_in_bias: FLOAT,
        norm_out_weight: FLOAT,
        norm_out_bias: FLOAT,
        p_out_weight: FLOAT,
        g_out_weight: FLOAT,
        direction: str,
        eps: float,
        precision: int,
    ) -> FLOAT:
        return _onnx_opset.tri_mul_update_nomask_noout_bias(
            x,
            norm_in_weight,
            norm_in_bias,
            p_in_weight,
            p_in_bias,
            g_in_weight,
            g_in_bias,
            norm_out_weight,
            norm_out_bias,
            p_out_weight,
            g_out_weight,
            direction=direction,
            eps=eps,
            precision=precision,
            plugin_namespace=NS,
        )

    @onnxscript.script(_onnx_opset)
    def _tri_mul_update_nomask_noin_bias_noout_bias(
        x: FLOAT,
        norm_in_weight: FLOAT,
        norm_in_bias: FLOAT,
        p_in_weight: FLOAT,
        g_in_weight: FLOAT,
        norm_out_weight: FLOAT,
        norm_out_bias: FLOAT,
        p_out_weight: FLOAT,
        g_out_weight: FLOAT,
        direction: str,
        eps: float,
        precision: int,
    ) -> FLOAT:
        return _onnx_opset.tri_mul_update_nomask_noin_bias_noout_bias(
            x,
            norm_in_weight,
            norm_in_bias,
            p_in_weight,
            g_in_weight,
            norm_out_weight,
            norm_out_bias,
            p_out_weight,
            g_out_weight,
            direction=direction,
            eps=eps,
            precision=precision,
            plugin_namespace=NS,
        )

    @onnxscript.script(_onnx_opset, default_opset=op)
    def _segmented_transpose(
        tensor: FLOAT,
        segment_info: FLOAT,
        input_contiguous_as_info: bool,
    ) -> FLOAT:
        return _onnx_opset.segmented_transpose(
            tensor,
            segment_info,
            contiguous=input_contiguous_as_info,
        )

    @onnxscript.script(_onnx_opset, default_opset=op)
    def _fused_tensor_product_fwd(
        in0: FLOAT,
        in1: FLOAT,
        in2: FLOAT,
        tp_path_csr_offsets_fwd: INT64,
        tp_path_csr_offsets_dgrad_in0: INT64,
        tp_path_csr_offsets_dgrad_in1: INT64,
        tp_path_csr_offsets_dgrad_in2: INT64,
        tp_path_offsets_fwd: INT64,
        tp_path_offsets_dgrad_in0: INT64,
        tp_path_offsets_dgrad_in1: INT64,
        tp_path_offsets_dgrad_in2: INT64,
        tp_path_cg_values_fwd: FLOAT,
        tp_path_cg_values_dgrad_in0: FLOAT,
        tp_path_cg_values_dgrad_in1: FLOAT,
        tp_path_cg_values_dgrad_in2: FLOAT,
        connection_mode: int,
        output_stride: int,
    ) -> FLOAT:
        return _onnx_opset.fused_tensor_product(
            in0,
            in1,
            in2,
            tp_path_csr_offsets_fwd,
            tp_path_csr_offsets_dgrad_in0,
            tp_path_csr_offsets_dgrad_in1,
            tp_path_csr_offsets_dgrad_in2,
            tp_path_offsets_fwd,
            tp_path_offsets_dgrad_in0,
            tp_path_offsets_dgrad_in1,
            tp_path_offsets_dgrad_in2,
            tp_path_cg_values_fwd,
            tp_path_cg_values_dgrad_in0,
            tp_path_cg_values_dgrad_in1,
            tp_path_cg_values_dgrad_in2,
            connection_mode=connection_mode,
            output_stride=output_stride,
        )

    @onnxscript.script(_onnx_opset, default_opset=op)
    def _tensor_product_uniform_1d_jit(
        in0: FLOAT,
        in1: FLOAT,
        in2: FLOAT,
        number_of_output_segments: int,
        number_of_paths: int,
        data: FLOAT,
        math_code: int,
    ):
        return _onnx_opset.tensor_product_uniform_4x1d(
            in0,
            in1,
            in2,
            data,
            number_of_output_segments=number_of_output_segments,
            number_of_paths=number_of_paths,
            math_code=math_code,
        )

    op_table = {
        torch_ops.identity_2.default: _identity_2,
        torch_ops.triangle_attention.default: _triangle_attention,
        torch_ops.triangle_attention_mask.default: _triangle_attention_mask,
        torch_ops.triangle_attention_nomask.default: _triangle_attention_nomask,
        torch_ops.layer_norm_transpose.default: _layer_norm_transpose,
        torch_ops.attention_pair_bias_mask.default: _attention_pair_bias_mask,
        torch_ops.tri_mul_update.default: _tri_mul_update,
        torch_ops.tri_mul_update_noin_bias.default: _tri_mul_update_noin_bias,
        torch_ops.tri_mul_update_noout_bias.default: _tri_mul_update_noout_bias,
        torch_ops.tri_mul_update_noin_bias_noout_bias.default: _tri_mul_update_noin_bias_noout_bias,
        torch_ops.tri_mul_update_nomask.default: _tri_mul_update_nomask,
        torch_ops.tri_mul_update_nomask_noin_bias.default: _tri_mul_update_nomask_noin_bias,
        torch_ops.tri_mul_update_nomask_noout_bias.default: _tri_mul_update_nomask_noout_bias,
        torch_ops.tri_mul_update_nomask_noin_bias_noout_bias.default: _tri_mul_update_nomask_noin_bias_noout_bias,
        torch_ops.segmented_transpose.default: _segmented_transpose,
        torch_ops.fused_tensor_product_fwd.default: _fused_tensor_product_fwd,
        torch_ops.tensor_product_uniform_1d_jit.default: _tensor_product_uniform_1d_jit,
    }

    __all__ += ["op_table"]

except ImportError:
    raise

"""
# This section defines run-time plugins, used when running exported ONNX graph with ONNXruntime
"""

try:
    from onnxruntime import SessionOptions
    from onnxruntime_extensions import PyCustomOpDef, get_library_path, onnx_op

    def _to_numpy(ret):
        if torch.is_tensor(ret):
            return ret.cpu().numpy()
        else:
            return (r.cpu().numpy() for r in ret)

    def _ort_triangle_attention(*args, **kwargs):
        scale = kwargs["scale"]
        return_aux = kwargs.get("return_aux", False)
        cargs = [torch.from_numpy(i).cuda() for i in args]
        return _to_numpy(
            cops.triangle_attention(*cargs, scale=scale, return_aux=return_aux)
        )

    @onnx_op(
        op_type="cuequivariance::triangle_attention",
        inputs=[
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_bool,
        ],
        outputs=[
            PyCustomOpDef.dt_float,  # Output: o
            PyCustomOpDef.dt_float,  # Output: sm_lse
            PyCustomOpDef.dt_float,  # Output: sm_max
        ],
        attrs={
            "scale": PyCustomOpDef.dt_float,
        },
    )
    def _(*args, **kwargs):
        return _ort_triangle_attention(*args, **kwargs)

    @onnx_op(
        op_type="cuequivariance::triangle_attention_nomask",
        inputs=[
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
        ],
        outputs=[
            PyCustomOpDef.dt_float,  # Output: o
        ],
        attrs={
            "scale": PyCustomOpDef.dt_float,
        },
    )
    def _(*args, **kwargs):
        return _ort_triangle_attention(*args, **kwargs)

    @onnx_op(
        op_type="cuequivariance::triangle_attention",
        inputs=[
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_bool,
        ],
        outputs=[
            PyCustomOpDef.dt_float,  # Output: o
        ],
        attrs={
            "scale": PyCustomOpDef.dt_float,
        },
    )
    def _(*args, **kwargs):
        return _ort_triangle_attention(*args, **kwargs)

    def ort_fused_tensor_product(*args, **kwargs):
        connection_mode = kwargs["connection_mode"]
        output_stride = kwargs["output_stride"]
        cargs = [torch.from_numpy(i).cuda() for i in args]
        return torch_ops.fused_tensor_product_fwd(
            *cargs, connection_mode, output_stride
        )

    @onnx_op(
        op_type="cuequivariance::fused_tensor_product",
        inputs=[
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
        ],
        attrs={
            "connection_mode": PyCustomOpDef.dt_int64,
            "output_stride": PyCustomOpDef.dt_int64,
        },
    )
    def ort_fused_tensor_product_fp32(*args, **kwargs):
        return ort_fused_tensor_product(*args, **kwargs)

    @onnx_op(
        op_type="cuequivariance::fused_tensor_product",
        inputs=[
            PyCustomOpDef.dt_float16,
            PyCustomOpDef.dt_float16,
            PyCustomOpDef.dt_float16,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
        ],
        attrs={
            "connection_mode": PyCustomOpDef.dt_int64,
            "output_stride": PyCustomOpDef.dt_int64,
        },
    )
    def ort_fused_tensor_product_fp16(*args, **kwargs):
        return ort_fused_tensor_product(*args, **kwargs)

    def ort_segmented_transpose(in1, in2, **kwargs):
        contiguous = kwargs["contiguous"]
        return torch_ops.segmented_transpose(
            torch.from_numpy(in1).cuda(), torch.from_numpy(in2).cuda(), contiguous
        )

    @onnx_op(
        op_type="cuequivariance::segmented_transpose",
        inputs=[PyCustomOpDef.dt_float, PyCustomOpDef.dt_int32],
        attrs={
            "contiguous": PyCustomOpDef.dt_int64,
        },
    )
    def ort_segmented_transpose_fp32(in1, in2, **kwargs):
        return ort_segmented_transpose(in1, in2, **kwargs)

    @onnx_op(
        op_type="cuequivariance::segmented_transpose",
        inputs=[PyCustomOpDef.dt_float16, PyCustomOpDef.dt_int32],
        outputs=[PyCustomOpDef.dt_float16],
        attrs={
            "contiguous": PyCustomOpDef.dt_int64,
        },
    )
    def ort_segmented_transpose_fp16(in1, in2, **kwargs):
        return ort_segmented_transpose(in1, in2, **kwargs)

    """
    @onnx_op(
        op_type="cuequivariance::tensor_product_uniform_1d_jit",
        inputs=[
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_int32,
        ],
        attrs={
            "number_of_output_segments": PyCustomOpDef.dt_int64,
            "number_of_paths": PyCustomOpDef.dt_int64,
            "math_code": PyCustomOpDef.dt_int64,
        },
    )
    def ort_tensor_product_uniform_1d(*args, **kwargs):
        number_of_output_segments = kwargs["number_of_output_segments"]
        number_of_paths = kwargs["number_of_paths"]
        math_code = kwargs["math_code"]
        cargs = [torch.from_numpy(i).cuda() for i in args]
        return torch_ops.tensor_product_uniform_1d_jit(
            cargs[0],
            cargs[1],
            cargs[2],
            number_of_output_segments,
            number_of_paths,
            cargs[3],
            math_code,
        )
    """

    # This function register ORT implementations on runtime side
    def register_custom_ops_library():
        ops = SessionOptions()
        ops.register_custom_ops_library(get_library_path())
        return ops

except ImportError:
    pass
