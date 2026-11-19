"""0 除算が混ざった計算パイプラインで静かに壊れる例の再現。"""

import pytest

from quantum_zero import QuantumState, safe_divide


class TestSilentTotalAccumulation:
    """+= で合計すると型が数値から QuantumState に変わる。"""

    def test_mixed_loop_total_becomes_quantum_state(self):
        """
        分類: 既知の設計上の問題

        int から始めても safe_divide 混入後は QuantumState になり、数値合計ではない。
        """
        total = 0
        for v in [10, safe_divide(1, 0), 20]:
            total += v
        assert isinstance(total, QuantumState)
        assert not isinstance(total, (int, float))

    def test_mixed_loop_total_not_equal_30(self):
        """
        分類: 既知の設計上の問題

        見た目の合計 10+?+20 は 30 にならない（例外も出ない）。
        """
        total = 0
        for v in [10, safe_divide(1, 0), 20]:
            total += v
        assert total != 30


class TestSilentPartialSum:
    """isinstance で QS を 0 扱いすると特異点項が消える。"""

    def test_sum_with_else_zero_ignores_zero_divide_term(self):
        """
        分類: 既知の設計上の問題

        QS を else 0 にすると、0 除算した 10 が合計から消える。
        """
        parts = [safe_divide(10, d) for d in [5, 2, 0, 3]]
        total = sum(p if isinstance(p, (int, float)) else 0 for p in parts)
        # 10/5 + 10/2 + (QS→0) + 10/3
        expected_without_singular = 2.0 + 5.0 + 0 + (10 / 3)
        assert total == pytest.approx(expected_without_singular)
        assert 10 not in (total,)  # 欠損した 10 が合計に含まれていない

    def test_parts_contains_quantum_state_at_zero_distance(self):
        """
        分類: 現状仕様の記録

        d=0 の要素だけ QuantumState、他は float。
        """
        parts = [safe_divide(10, d) for d in [5, 2, 0, 3]]
        assert isinstance(parts[0], float)
        assert isinstance(parts[2], QuantumState)


class TestAverageNotNumeric:
    """平均のように見せかけても数値にならない。"""

    def test_avg_of_two_singular_states_stays_quantum(self):
        """
        分類: 既知の設計上の問題

        (d + d) / 2 は QuantumState のまま、50 などにはならない。
        """
        d = safe_divide(100, 0)
        avg = (d + d) / 2
        assert isinstance(avg, QuantumState)
        assert avg != 50
        assert not isinstance(avg, (int, float))


class TestThresholdComparison:
    """閾値比較は例外になるか、静かに別経路になる。"""

    def test_density_greater_than_10_raises_type_error(self):
        """
        分類: 現状仕様の記録

        density > 10 は TypeError（必須要件）。
        """
        density = safe_divide(100, 0)
        with pytest.raises(TypeError):
            _ = density > 10


class TestConsumerBranchCollapse:
    """呼び出し側の isinstance 分岐で QS が 0 に潰れる例。"""

    def test_helper_returns_zero_for_quantum(self):
        """
        分類: 既知の設計上の問題

        よくある分岐で QS は 0 扱いされ、データが消える。
        """

        def use(x):
            return x * 2 if isinstance(x, (int, float)) else 0

        assert use(safe_divide(1, 0)) == 0


@pytest.mark.xfail(reason="既知の設計上の問題：特異点混入時にパイプラインが失敗または警告すべき")
def test_future_pipeline_raises_on_singular():
    """
    分類: 将来の改善目標

    将来: safe_divide が混ざった合計で検出可能なエラー／警告がある想定。
    """
    total = 0
    for v in [10, safe_divide(1, 0), 20]:
        total += v
    pytest.fail("singular should have been detected")