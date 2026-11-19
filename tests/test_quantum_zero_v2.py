"""quantum_zero_v2（AuditState）の契約テスト。"""

import pytest

from quantum_zero_v2 import AuditState, safe_divide


class TestSafeDivideReturnsAuditState:
    """safe_divide と AuditState の基本属性。"""

    def test_zero_divisor_returns_audit_state(self):
        """
        分類: 現状仕様の記録

        divisor が 0 のとき AuditState が返る。
        """
        result = safe_divide(100, 0)
        assert isinstance(result, AuditState)

    def test_is_undefined_true(self):
        """
        分類: 現状仕様の記録
        """
        state = safe_divide(100, 0)
        assert isinstance(state, AuditState)
        assert state.is_undefined is True

    def test_original_dividend_and_divisor(self):
        """
        分類: 現状仕様の記録
        """
        state = safe_divide(100, 0)
        assert isinstance(state, AuditState)
        assert state.original_dividend == 100
        assert state.original_divisor == 0

    def test_nonzero_divisor_returns_numeric(self):
        """
        分類: 現状仕様の記録

        通常除算は数値（float）を返す。
        """
        assert safe_divide(10, 2) == 5.0
        assert not isinstance(safe_divide(10, 2), AuditState)


class TestArithmeticPropagation:
    """演算後も AuditState のまま伝播する。"""

    def test_mult_zero_stays_audit_state(self):
        """
        分類: 現状仕様の記録

        * 0 でも数値に戻らない（v1 との違い）。
        """
        state = safe_divide(100, 0)
        assert isinstance(state * 0, AuditState)
        assert isinstance(0 * state, AuditState)

    def test_add_and_mult_stay_audit_state(self):
        """
        分類: 現状仕様の記録
        """
        state = safe_divide(100, 0)
        assert isinstance(state + 1, AuditState)
        assert isinstance(state * 5, AuditState)


class TestResolveAndRaise:
    """resolve / raise_if_undefined。"""

    def test_resolve_with_default_returns_default(self):
        """
        分類: 現状仕様の記録
        """
        state = safe_divide(100, 0)
        assert isinstance(state, AuditState)
        assert state.resolve(0) == 0

    def test_resolve_without_default_raises(self):
        """
        分類: 現状仕様の記録
        """
        state = safe_divide(100, 0)
        assert isinstance(state, AuditState)
        with pytest.raises(ZeroDivisionError):
            state.resolve()

    def test_raise_if_undefined_raises(self):
        """
        分類: 現状仕様の記録
        """
        state = safe_divide(100, 0)
        assert isinstance(state, AuditState)
        with pytest.raises(ZeroDivisionError):
            state.raise_if_undefined()


class TestEqualityAndHash:
    """等価性とハッシュ（集合・辞書で使える）。"""

    def test_same_operation_equal(self):
        """
        分類: 現状仕様の記録
        """
        assert safe_divide(100, 0) == safe_divide(100, 0)

    def test_different_dividend_not_equal(self):
        """
        分類: 現状仕様の記録
        """
        assert safe_divide(100, 0) != safe_divide(999, 0)

    def test_not_equal_to_int(self):
        """
        分類: 現状仕様の記録
        """
        state = safe_divide(100, 0)
        assert (state == 100) is False
        assert (100 == state) is False

    def test_usable_as_dict_key(self):
        """
        分類: 現状仕様の記録
        """
        a = safe_divide(100, 0)
        b = safe_divide(100, 0)
        d = {a: "first"}
        d[b] = "second"
        assert len(d) == 1
        assert d[a] == "second"

    def test_usable_in_set(self):
        """
        分類: 現状仕様の記録
        """
        s = {safe_divide(100, 0), safe_divide(100, 0), safe_divide(999, 0)}
        assert len(s) == 2


class TestLoggingSerialization:
    """to_log / to_dict。"""

    def test_to_log_returns_nonempty_str(self):
        """
        分類: 現状仕様の記録
        """
        state = safe_divide(100, 0)
        assert isinstance(state, AuditState)
        log = state.to_log()
        assert isinstance(log, str)
        assert "dividend=100" in log
        assert "divisor=0" in log

    def test_to_dict_has_required_keys(self):
        """
        分類: 現状仕様の記録
        """
        state = safe_divide(100, 0)
        assert isinstance(state, AuditState)
        data = state.to_dict()
        assert isinstance(data, dict)
        for key in (
            "dividend",
            "divisor",
            "reason",
            "is_undefined",
            "created_at",
            "description",
        ):
            assert key in data
        assert data["dividend"] == 100
        assert data["divisor"] == 0
        assert data["is_undefined"] is True


class TestRestoreMetaphor:
    """restore() は * 0 とは別経路。"""

    def test_restore_returns_dividend(self):
        """
        分類: 現状仕様の記録

        restore() だけが被除数を返す（比喩）。
        """
        state = safe_divide(100, 0)
        assert isinstance(state, AuditState)
        assert state.restore() == 100
        assert not isinstance(state * 0, (int, float))


class TestComparisonErrors:
    """大小比較は TypeError。"""

    def test_gt_int_raises_with_message(self):
        """
        分類: 現状仕様の記録
        """
        state = safe_divide(100, 0)
        assert isinstance(state, AuditState)
        with pytest.raises(TypeError) as exc:
            _ = state > 10
        assert "未定義状態" in str(exc.value)