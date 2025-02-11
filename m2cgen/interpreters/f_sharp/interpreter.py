from pathlib import Path

from m2cgen.ast import BinNumOpType
from m2cgen.interpreters.f_sharp.code_generator import FSharpCodeGenerator
from m2cgen.interpreters.interpreter import FunctionalToCodeInterpreter
from m2cgen.interpreters.mixins import BinExpressionDepthTrackingMixin, LinearAlgebraMixin
from m2cgen.interpreters.utils import get_file_content


class FSharpInterpreter(FunctionalToCodeInterpreter,
                        LinearAlgebraMixin,
                        BinExpressionDepthTrackingMixin):

    # Too long lines causes F# compiler to crash with
    # error FS0193 : internal error :
    # Specified argument was out of the range of valid values.
    # (Parameter 'value').
    # Refer to https://github.com/dotnet/fsharp/issues/3866.
    bin_depth_threshold = 250

    supported_bin_vector_ops = {
        BinNumOpType.ADD: "addVectors",
    }

    supported_bin_vector_num_ops = {
        BinNumOpType.MUL: "mulVectorNumber",
    }

    abs_function_name = "abs"
    atan_function_name = "atan"
    exponent_function_name = "exp"
    logarithm_function_name = "log"
    log1p_function_name = "log1p"
    sigmoid_function_name = "sigmoid"
    softmax_function_name = "softmax"
    sqrt_function_name = "sqrt"
    tanh_function_name = "tanh"

    with_log1p_expr = False
    with_sigmoid_expr = False
    with_softmax_expr = False

    def __init__(self, indent=4, function_name="score", *args, **kwargs):
        self.indent = indent
        self.function_name = function_name

        super().__init__(self.create_code_generator(), *args, **kwargs)

    def interpret(self, expr):
        self._cg.reset_state()
        self._reset_reused_expr_cache()

        args = [(True, self._feature_array_name)]
        func_name = self.function_name

        with self._cg.function_definition(name=func_name, args=args):
            last_result = self._do_interpret(expr)
            self._dump_cache()
            self._cg.add_code_line(last_result)

        current_dir = Path(__file__).absolute().parent

        if self.with_linear_algebra:
            filename = current_dir / "linear_algebra.fs"
            self._cg.prepend_code_lines(get_file_content(filename))

        if self.with_log1p_expr:
            filename = current_dir / "log1p.fs"
            self._cg.prepend_code_lines(get_file_content(filename))

        if self.with_softmax_expr:
            filename = current_dir / "softmax.fs"
            self._cg.prepend_code_lines(get_file_content(filename))

        if self.with_sigmoid_expr:
            filename = current_dir / "sigmoid.fs"
            self._cg.prepend_code_lines(get_file_content(filename))

        return self._cg.finalize_and_get_generated_code()

    def create_code_generator(self):
        return FSharpCodeGenerator(indent=self.indent)

    def interpret_pow_expr(self, expr, **kwargs):
        base_result = self._do_interpret(expr.base_expr, **kwargs)
        exp_result = self._do_interpret(expr.exp_expr, **kwargs)
        return self._cg.infix_expression(
            left=base_result, right=exp_result, op="**")

    def interpret_log1p_expr(self, expr, **kwargs):
        self.with_log1p_expr = True
        return super().interpret_log1p_expr(expr, **kwargs)

    def interpret_softmax_expr(self, expr, **kwargs):
        self.with_softmax_expr = True
        return super().interpret_softmax_expr(expr, **kwargs)

    def interpret_sigmoid_expr(self, expr, **kwargs):
        self.with_sigmoid_expr = True
        return super().interpret_sigmoid_expr(expr, **kwargs)

    def _dump_cache(self):
        if self._cached_expr_results:
            for func_name, expr_result in self._cached_expr_results.values():
                self._cg.add_function(
                    function_name=func_name, function_body=expr_result)

    def bin_depth_threshold_hook(self, expr, **kwargs):
        if expr in self._cached_expr_results:
            return self._cached_expr_results[expr].var_name
        result = self._do_interpret(expr, **kwargs)
        return self._cache_reused_expr(expr, result)
