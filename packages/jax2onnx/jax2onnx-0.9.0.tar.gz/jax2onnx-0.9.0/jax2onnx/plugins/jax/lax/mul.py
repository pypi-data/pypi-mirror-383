# jax2onnx/plugins/jax/lax/mul.py

from typing import TYPE_CHECKING, Optional
import jax
import numpy as np
from jax2onnx.plugins.plugin_system import PrimitiveLeafPlugin, register_primitive

if TYPE_CHECKING:
    pass  # hints


@register_primitive(
    jaxpr_primitive=jax.lax.mul_p.name,
    jax_doc="https://docs.jax.dev/en/latest/_autosummary/jax.lax.mul.html",
    onnx=[{"component": "Mul", "doc": "https://onnx.ai/onnx/operators/onnx__Mul.html"}],
    since="v0.1.0",
    context="primitives.lax",
    component="mul",
    testcases=[
        {
            "testcase": "mul_test1",
            "callable": lambda x1, x2: x1 * x2,
            "input_shapes": [(3,), (3,)],
        },
        {
            "testcase": "mul_test2",
            "callable": lambda x1, x2: x1 * x2,
            "input_shapes": [(2, 2), (2, 2)],
        },
        {
            "testcase": "mul_pyfloat_promotes_to_array_dtype_f64",
            "callable": lambda x: x * 1.5,
            "input_values": [np.array([1.0, 2.0], dtype=np.float64)],
            "expected_output_dtypes": [np.float64],
            "run_only_f64_variant": True,
        },
        {
            "testcase": "mul_scalar_broadcast_promote_to_f64",
            "callable": lambda x: x.astype(np.float64) * 1.5,
            "input_values": [np.array([1.0, 2.0], dtype=np.float32)],
            "expected_output_dtypes": [np.float64],
            "run_only_f64_variant": True,
        },
    ],
)
class MulPlugin(PrimitiveLeafPlugin):
    def lower(self, ctx, eqn):
        x_var, y_var = eqn.invars
        out_var = eqn.outvars[0]

        prefer_dt: Optional[np.dtype] = np.dtype(
            getattr(x_var.aval, "dtype", np.float32)
        )
        a_val = ctx.get_value_for_var(x_var, name_hint=ctx.fresh_name("mul_lhs"))
        b_val = ctx.get_value_for_var(
            y_var, name_hint=ctx.fresh_name("mul_rhs"), prefer_np_dtype=prefer_dt
        )
        out_spec = ctx.get_value_for_var(out_var, name_hint=ctx.fresh_name("mul_out"))
        result = ctx.builder.Mul(a_val, b_val, _outputs=[out_spec.name])
        result.type = out_spec.type
        result.shape = out_spec.shape
        ctx.bind_value_for_var(out_var, result)
