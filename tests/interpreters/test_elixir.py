from m2cgen import ast
from m2cgen.interpreters import ElixirInterpreter

from tests.utils import assert_code_equal


def test_if_expr():
    expr = ast.IfExpr(
        ast.CompExpr(ast.NumVal(1), ast.FeatureRef(0), ast.CompOpType.EQ),
        ast.NumVal(2),
        ast.NumVal(3))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        func0 = fn ->
            cond do (1.0) == (read(input,0)) ->
                2.0
            true ->
                3.0
            end
        end
        <<func0.()::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_bin_num_expr():
    expr = ast.BinNumExpr(
        ast.BinNumExpr(
            ast.FeatureRef(0), ast.NumVal(-2), ast.BinNumOpType.DIV),
        ast.NumVal(2),
        ast.BinNumOpType.MUL)

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        <<((read(input,0)) / (-2.0)) * (2.0)::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_dependable_condition():
    left = ast.BinNumExpr(
        ast.IfExpr(
            ast.CompExpr(ast.NumVal(1),
                         ast.NumVal(1),
                         ast.CompOpType.EQ),
            ast.NumVal(1),
            ast.NumVal(2)),
        ast.NumVal(2),
        ast.BinNumOpType.ADD)
    right = ast.BinNumExpr(ast.NumVal(1), ast.NumVal(2), ast.BinNumOpType.DIV)
    bool_test = ast.CompExpr(left, right, ast.CompOpType.GTE)
    expr = ast.IfExpr(bool_test, ast.NumVal(1), ast.FeatureRef(0))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        func0 = fn ->
            cond do (1.0) == (1.0) ->
                1.0
            true ->
                2.0
            end
        end
        func1 = fn ->
            cond do ((func0.()) + (2.0)) >= ((1.0) / (2.0)) ->
                1.0
            true ->
                read(input,0)
            end
        end
        <<func1.()::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_nested_condition():
    left = ast.BinNumExpr(
        ast.IfExpr(
            ast.CompExpr(ast.NumVal(1),
                         ast.NumVal(1),
                         ast.CompOpType.EQ),
            ast.NumVal(1),
            ast.NumVal(2)),
        ast.NumVal(2),
        ast.BinNumOpType.ADD)
    bool_test = ast.CompExpr(ast.NumVal(1), left, ast.CompOpType.EQ)
    expr_nested = ast.IfExpr(bool_test, ast.FeatureRef(2), ast.NumVal(2))
    expr = ast.IfExpr(bool_test, expr_nested, ast.NumVal(2))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        func0 = fn ->
            cond do (1.0) == (1.0) ->
                1.0
            true ->
                2.0
            end
        end
        func1 = fn ->
            cond do (1.0) == ((func0.()) + (2.0)) ->
                cond do (1.0) == ((func0.()) + (2.0)) ->
                    read(input,2)
                true ->
                    2.0
                end
            true ->
                2.0
            end
        end
        <<func1.()::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_raw_array():
    expr = ast.VectorVal([ast.NumVal(3), ast.NumVal(4)])

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        <<3.0::float, 4.0::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_multi_output():
    expr = ast.IfExpr(
        ast.CompExpr(
            ast.NumVal(1),
            ast.NumVal(1),
            ast.CompOpType.NOT_EQ),
        ast.VectorVal([ast.NumVal(1), ast.NumVal(2)]),
        ast.VectorVal([ast.NumVal(3), ast.NumVal(4)]))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        func0 = fn ->
            cond do (1.0) != (1.0) ->
                <<1.0::float, 2.0::float>>
            true ->
                <<3.0::float, 4.0::float>>
            end
        end
        func0.()
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_bin_vector_expr():
    expr = ast.BinVectorExpr(
        ast.VectorVal([ast.NumVal(1), ast.NumVal(2)]),
        ast.VectorVal([ast.NumVal(3), ast.NumVal(4)]),
        ast.BinNumOpType.ADD)

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        add_vectors(<<1.0::float, 2.0::float>>, <<3.0::float, 4.0::float>>)
    end
defp add_vectors(v1, v2) do
  v1_list = for <<f::float <- v1>>, do: f
  v2_list = for <<f::float <- v2>>, do: f
  for {a,b} <- Enum.zip(v1_list, v2_list), into: <<>>, do: <<(a+b)::float>>
end

defp mul_vector_number(v1, num) do
  for <<f::float <- v1>>, into: <<>>, do: <<(f * num)::float>>
end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_bin_vector_num_expr():
    expr = ast.BinVectorNumExpr(
        ast.VectorVal([ast.NumVal(1), ast.NumVal(2)]),
        ast.NumVal(1),
        ast.BinNumOpType.MUL)

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        mul_vector_number(<<1.0::float, 2.0::float>>, 1.0)
    end
defp add_vectors(v1, v2) do
  v1_list = for <<f::float <- v1>>, do: f
  v2_list = for <<f::float <- v2>>, do: f
  for {a,b} <- Enum.zip(v1_list, v2_list), into: <<>>, do: <<(a+b)::float>>
end

defp mul_vector_number(v1, num) do
  for <<f::float <- v1>>, into: <<>>, do: <<(f * num)::float>>
end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


class CustomElixirInterpreter(ElixirInterpreter):
    bin_depth_threshold = 2


def test_depth_threshold_with_bin_expr():
    expr = ast.NumVal(1)
    for _ in range(4):
        expr = ast.BinNumExpr(ast.NumVal(1), expr, ast.BinNumOpType.ADD)

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        func0 = fn ->
            (1.0) + ((1.0) + (1.0))
        end
        <<(1.0) + ((1.0) + (func0.()))::float>>
    end
end
"""

    interpreter = CustomElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_depth_threshold_without_bin_expr():
    expr = ast.NumVal(1)
    for _ in range(4):
        expr = ast.IfExpr(
            ast.CompExpr(
                ast.NumVal(1), ast.NumVal(1), ast.CompOpType.EQ),
            ast.NumVal(1),
            expr)

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        func0 = fn ->
            cond do (1.0) == (1.0) ->
                1.0
            true ->
                cond do (1.0) == (1.0) ->
                    1.0
                true ->
                    cond do (1.0) == (1.0) ->
                        1.0
                    true ->
                        cond do (1.0) == (1.0) ->
                            1.0
                        true ->
                            1.0
                        end
                    end
                end
            end
        end
        <<func0.()::float>>
    end
end
"""

    interpreter = CustomElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_deep_mixed_exprs_not_reaching_threshold():
    expr = ast.NumVal(1)
    for _ in range(4):
        inner = ast.NumVal(1)
        for __ in range(2):
            inner = ast.BinNumExpr(ast.NumVal(1), inner, ast.BinNumOpType.ADD)
        expr = ast.IfExpr(
            ast.CompExpr(
                inner, ast.NumVal(1), ast.CompOpType.EQ),
            ast.NumVal(1),
            expr)

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        func0 = fn ->
            cond do ((1.0) + ((1.0) + (1.0))) == (1.0) ->
                1.0
            true ->
                cond do ((1.0) + ((1.0) + (1.0))) == (1.0) ->
                    1.0
                true ->
                    cond do ((1.0) + ((1.0) + (1.0))) == (1.0) ->
                        1.0
                    true ->
                        cond do ((1.0) + ((1.0) + (1.0))) == (1.0) ->
                            1.0
                        true ->
                            1.0
                        end
                    end
                end
            end
        end
        <<func0.()::float>>
    end
end
"""

    interpreter = CustomElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_deep_mixed_exprs_exceeding_threshold():
    expr = ast.NumVal(1)
    for i in range(4):
        inner = ast.NumVal(1)
        for j in range(4):
            inner = ast.BinNumExpr(ast.NumVal(i), inner, ast.BinNumOpType.ADD)
        expr = ast.IfExpr(
            ast.CompExpr(
                inner, ast.NumVal(j), ast.CompOpType.EQ),
            ast.NumVal(1),
            expr)

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        func0 = fn ->
            (3.0) + ((3.0) + (1.0))
        end
        func1 = fn ->
            (2.0) + ((2.0) + (1.0))
        end
        func2 = fn ->
            (1.0) + ((1.0) + (1.0))
        end
        func3 = fn ->
            (0.0) + ((0.0) + (1.0))
        end
        func4 = fn ->
            cond do ((3.0) + ((3.0) + (func0.()))) == (3.0) ->
                1.0
            true ->
                cond do ((2.0) + ((2.0) + (func1.()))) == (3.0) ->
                    1.0
                true ->
                    cond do ((1.0) + ((1.0) + (func2.()))) == (3.0) ->
                        1.0
                    true ->
                        cond do ((0.0) + ((0.0) + (func3.()))) == (3.0) ->
                            1.0
                        true ->
                            1.0
                        end
                    end
                end
            end
        end
        <<func4.()::float>>
    end
end
"""

    interpreter = CustomElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_abs_expr():
    expr = ast.AbsExpr(ast.NumVal(-1.0))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        <<abs(-1.0)::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_exp_expr():
    expr = ast.ExpExpr(ast.NumVal(1.0))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        <<:math.exp(1.0)::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_pow_expr():
    expr = ast.PowExpr(ast.NumVal(2.0), ast.NumVal(3.0))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        <<:math.pow(2.0, 3.0)::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_sqrt_expr():
    expr = ast.SqrtExpr(ast.NumVal(2.0))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        <<:math.sqrt(2.0)::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_tanh_expr():
    expr = ast.TanhExpr(ast.NumVal(2.0))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        <<:math.tanh(2.0)::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_log_expr():
    expr = ast.LogExpr(ast.NumVal(2.0))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        <<:math.log(2.0)::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_log1p_expr():
    expr = ast.Log1pExpr(ast.NumVal(2.0))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        <<log1p(2.0)::float>>
    end
defp log1p(x) do
    cond do
        x == 0.0 -> 0.0
        x == -1.0 -> -1.7976931348623157e+308
        x < 1.0 -> :nan
        abs(x) < 0.5 * 4.94065645841247e-324 -> x
        (x > 0.0 && x < 1.0e-8) || (x > -1.0e-9 && x < 0.0) -> x * (1.0 - x * 0.5)
        abs(x) < 0.375 ->
            coeffs = [
                0.10378693562743769800686267719098e+1,
               -0.13364301504908918098766041553133e+0,
                0.19408249135520563357926199374750e-1,
               -0.30107551127535777690376537776592e-2,
                0.48694614797154850090456366509137e-3,
               -0.81054881893175356066809943008622e-4,
                0.13778847799559524782938251496059e-4,
               -0.23802210894358970251369992914935e-5,
                0.41640416213865183476391859901989e-6,
               -0.73595828378075994984266837031998e-7,
                0.13117611876241674949152294345011e-7,
               -0.23546709317742425136696092330175e-8,
                0.42522773276034997775638052962567e-9,
               -0.77190894134840796826108107493300e-10,
                0.14075746481359069909215356472191e-10,
               -0.25769072058024680627537078627584e-11,
                0.47342406666294421849154395005938e-12,
               -0.87249012674742641745301263292675e-13,
                0.16124614902740551465739833119115e-13,
               -0.29875652015665773006710792416815e-14,
                0.55480701209082887983041321697279e-15,
               -0.10324619158271569595141333961932e-15]
            x * (1.0 - x * chebyshev_broucke(x / 0.375, coeffs))
        true -> :math.log(1.0+x)
    end
end

defp chebyshev_broucke(x, coeffs) do

    {b0, _b1, b2} = coeffs
    |> Enum.reverse()
    |> Enum.reduce({0.0, 0.0, 0.0}, fn k, {b0, b1, _b2} ->
        {(k + x * 2.0 * b0 - b1), b0, b1}
    end)

    (b0 - b2) * 0.5

end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_atan_expr():
    expr = ast.AtanExpr(ast.NumVal(2.0))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        <<:math.atan(2.0)::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_softmax_expr():
    expr = ast.SoftmaxExpr([ast.NumVal(2.0), ast.NumVal(3.0)])

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        softmax(<<2.0::float, 3.0::float>>)
    end
defp softmax(x) do
    max_elem = Enum.max(for <<f::float <- x>>, do: f)
    exps = for <<f::float <- x>>, do: :math.exp(f-max_elem)
    sum_exps = Enum.sum(exps)
    for i <- exps, into: <<>>, do: <<(i/sum_exps)::float>>
end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_sigmoid_expr():
    expr = ast.SigmoidExpr(ast.NumVal(2.0))

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        <<sigmoid(2.0)::float>>
    end
defp sigmoid(x) do
    1.0 / (1.0 + :math.exp(-x))
end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)


def test_reused_expr():
    reused_expr = ast.ExpExpr(ast.NumVal(1.0), to_reuse=True)
    expr = ast.BinNumExpr(reused_expr, reused_expr, ast.BinNumOpType.DIV)

    expected_code = """
defmodule Model do
    @compile {:inline, read: 2}
    defp read(bin, pos) do
        <<_::size(pos)-unit(64)-binary, value::float, _::binary>> = bin
        value
    end
    def score(input) do
        func0 = fn ->
            :math.exp(1.0)
        end
        <<(func0.()) / (func0.())::float>>
    end
end
"""

    interpreter = ElixirInterpreter()
    assert_code_equal(interpreter.interpret(expr), expected_code)
