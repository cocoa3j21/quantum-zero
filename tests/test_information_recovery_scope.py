"""情報復元（* 0 で被除数が戻る）が有効な範囲の固定。"""

import pytest

from quantum_zero import QuantumState, safe_divide


class TestRecoveryOnlyOnFreshQuantumState:
    """safe_divide 直後の QuantumState に限る復元挙動。"""

    def test_fresh_safe_divide_mult_zero_returns_100(self):
        """
        分類: 現状仕様の記録

        デモの主張どおり、safe_divide(100, 0) 直後の * 0 は 100。
        """
        density = safe_divide(100, 0)
        assert density * 0 == 100
        assert 0 * density == 100

    def test_rmul_zero_restores_dividend(self):
        """
        分類: 現状仕様の記録

        0 * QuantumState（左から掛ける）でも被除数が復元される。
        """
        density = safe_divide(100, 0)
        assert 0 * density == 100

    @pytest.mark.parametrize(
        "transform,label",
        [
            pytest.param(lambda q: q * 5, "times_5", id="after_times_5"),
            pytest.param(lambda q: q + 1, "plus_1", id="after_plus_1"),
            pytest.param(lambda q: q + q, "plus_self", id="after_plus_self"),
            pytest.param(lambda q: (q + 10) / 2, "avg_like", id="after_avg_like"),
        ],
    )
    def test_after_transform_mult_zero_does_not_restore(self, transform, label):
        """
        分類: 既知の設計上の問題

        一度でも四則演算を挟むと * 0 は 100 に戻らない。
        """
        base = safe_divide(100, 0)
        derived = transform(base)
        assert isinstance(derived, QuantumState)
        restored = derived * 0
        assert restored != 100
        assert isinstance(restored, QuantumState)

    def test_nested_mult_five_then_zero_not_100(self):
        """
        分類: 既知の設計上の問題

        (safe_divide(100, 0) * 5) * 0 は 100 にならない（必須要件）。
        """
        q = safe_divide(100, 0)
        assert (q * 5) * 0 != 100
        assert isinstance((q * 5) * 0, QuantumState)

    def test_add_one_then_mult_zero_not_100(self):
        """
        分類: 既知の設計上の問題

        (safe_divide(100, 0) + 1) * 0 は 100 にならない（必須要件）。
        """
        q = safe_divide(100, 0) + 1
        assert q * 0 != 100
        assert isinstance(q * 0, QuantumState)

    def test_second_safe_divide_still_recovers_own_dividend(self):
        """
        分類: 現状仕様の記録

        別の safe_divide 直後なら、その被除数だけ * 0 で復元できる（混同しない）。
        """
        a = safe_divide(100, 0)
        b = safe_divide(200, 0)
        assert a * 0 == 100
        assert b * 0 == 200

    def test_derived_state_has_no_dividend(self):
        """
        分類: 現状仕様の記録

        + 1 後の QuantumState では内部 _dividend が None（復元の根拠が失われる）。
        """
        derived = safe_divide(100, 0) + 1
        assert derived._dividend is None


@pytest.mark.xfail(reason="既知の設計上の問題：演算チェーン全体で被除数を保持する仕様は未実装")
def test_future_recovery_after_arithmetic_chain():
    """
    分類: 将来の改善目標

    将来: 任意の演算後でも追跡可能な情報復元がある想定（現状は未実装）。
    """
    q = safe_divide(100, 0)
    chain = ((q + 1) * 2) - 3
    assert chain * 0 == 100