"""QuantumState の基本契約（現状挙動の固定）。"""

import pytest

from quantum_zero import QuantumState, safe_divide


class TestMultZeroRestoration:
    """QuantumState * 0（ゼロを掛けると被除数が戻る特例）の契約。"""

    @pytest.mark.parametrize(
        "zero",
        [
            pytest.param(0, id="int_0"),
            pytest.param(0.0, id="float_0"),
            pytest.param(False, id="bool_False"),
            pytest.param(0 + 0j, id="complex_0j"),
        ],
    )
    def test_safe_divide_then_mult_zero_restores_mass(self, zero):
        """
        分類: 現状仕様の記録

        safe_divide 直後の QuantumState に 0 相当を掛けると被除数 100 が返る。
        """
        q = safe_divide(100, 0)
        assert q * zero == 100

    def test_mult_zero_return_type_is_int_for_integer_mass(self):
        """
        分類: 現状仕様の記録

        被除数が整数のとき * 0 の戻り値型は int（float ではない）。
        """
        q = safe_divide(100, 0)
        result = q * 0
        assert result == 100
        assert type(result) is int

    def test_mult_zero_return_type_for_float_mass(self):
        """
        分類: 現状仕様の記録

        被除数が float のとき * 0 の戻り値型は元の数値型に依存する（現状は float のまま）。
        """
        q = safe_divide(100.5, 0)
        result = q * 0
        assert result == 100.5
        assert type(result) is float

    def test_mult_five_then_mult_zero_does_not_restore(self):
        """
        分類: 既知の設計上の問題

        一度 * 5 したあとの * 0 は 100 に戻らず QuantumState のまま。
        """
        q = safe_divide(100, 0)
        intermediate = q * 5
        assert isinstance(intermediate, QuantumState)
        final = intermediate * 0
        assert final != 100
        assert isinstance(final, QuantumState)

    def test_add_one_then_mult_zero_does_not_restore(self):
        """
        分類: 既知の設計上の問題

        + 1 したあとの * 0 は 100 に戻らない。
        """
        q = safe_divide(100, 0) + 1
        final = q * 0
        assert final != 100
        assert isinstance(final, QuantumState)


class TestMultNonZeroStaysQuantum:
    """通常の掛け算は QuantumState を維持する。"""

    def test_mult_scalar_stays_quantum_state(self):
        """
        分類: 現状仕様の記録

        safe_divide 直後に非ゼロを掛けると QuantumState のまま。
        """
        q = safe_divide(100, 0)
        result = q * 5
        assert isinstance(result, QuantumState)

    def test_add_scalar_stays_quantum_state(self):
        """
        分類: 現状仕様の記録

        + 0 しても数値には戻らない（文字列表現付き QS）。
        """
        q = safe_divide(50, 0) + 0
        assert isinstance(q, QuantumState)


class TestBoolAndTruthy:
    """真偽値（if 文で使うときの挙動）。"""

    def test_quantum_state_is_always_truthy(self):
        """
        分類: 既知の設計上の問題

        QuantumState は常に True 扱い（空や無効値と区別できない）。
        """
        q = safe_divide(1, 0)
        assert bool(q) is True
        assert q or False is True


class TestUndefinedStatePublicApi:
    """未定義状態を外部から追跡する公式 API の有無。"""

    def test_no_public_is_undefined_method(self):
        """
        分類: 現状仕様の記録

        is_undefined() のような公開メソッドは無い。
        """
        q = safe_divide(100, 0)
        assert not hasattr(q, "is_undefined")

    def test_no_public_divisor_attribute(self):
        """
        分類: 現状仕様の記録

        除数（0 だった距離など）を返す公開属性は無い。
        """
        q = safe_divide(100, 0)
        assert not hasattr(q, "divisor")
        assert not hasattr(q, "distance")

    def test_no_public_reason_property(self):
        """
        分類: 現状仕様の記録

        発生理由を構造化して返す公開 API は無い（説明は description 文字列のみ）。
        """
        q = safe_divide(100, 0)
        assert not hasattr(q, "reason")
        assert hasattr(q, "_state_description")

    def test_no_raises_or_to_exception(self):
        """
        分類: 現状仕様の記録

        未定義状態を明示的に例外へ変換するメソッドは無い。
        """
        q = safe_divide(100, 0)
        assert not hasattr(q, "raise_if_undefined")
        assert not hasattr(q, "to_exception")

    def test_private_dividend_exists_after_safe_divide(self):
        """
        分類: 現状仕様の記録

        被除数は公開属性ではなく _dividend（先頭アンダースコア＝内部用）にのみ保持される。
        """
        q = safe_divide(100, 0)
        assert q._dividend == 100

    def test_isinstance_detects_quantum_vs_float(self):
        """
        分類: 現状仕様の記録

        型チェック（isinstance）で float と QuantumState は区別できる。
        """
        assert isinstance(safe_divide(10, 2), float)
        assert isinstance(safe_divide(10, 0), QuantumState)

    def test_str_usable_for_log_or_csv_row(self):
        """
        分類: 現状仕様の記録

        str()/repr() は取れるため、ログや CSV の「文字列1列」にはできる。
        """
        q = safe_divide(100, 0)
        line = f"id,1,density,{q}"
        assert "QuantumState" in line
        assert len(str(q)) > 0


@pytest.mark.xfail(reason="既知の設計上の問題：未定義状態に公式フラグが無く、isinstance 以外の統一判定がない")
def test_future_public_undefined_flag():
    """
    分類: 将来の改善目標

    将来: 未定義であることを示す読み取り専用の公開属性がある想定（現状は無いので失敗）。
    """
    q = safe_divide(100, 0)
    assert hasattr(q, "is_singular")
    assert q.is_singular is True