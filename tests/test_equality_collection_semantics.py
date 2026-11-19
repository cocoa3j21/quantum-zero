"""等価性（==）とコレクション（リスト・集合など）の現状挙動。"""

import pytest

from quantum_zero import QuantumState, safe_divide


class TestEquality:
    """QuantumState の等価比較。"""

    def test_two_different_dividends_compare_equal(self):
        """
        分類: 既知の設計上の問題

        被除数が違っても QuantumState 同士は常に True。
        """
        a = safe_divide(100, 0)
        b = safe_divide(999, 0)
        assert a == b

    def test_quantum_not_equal_to_int(self):
        """
        分類: 現状仕様の記録

        QuantumState == 100 は False。
        """
        q = safe_divide(100, 0)
        assert (q == 100) is False

    def test_int_not_equal_to_quantum(self):
        """
        分類: 現状仕様の記録

        100 == QuantumState も False（対称的に不一致）。
        """
        q = safe_divide(100, 0)
        assert (100 == q) is False


class TestListSemantics:
    """リストでの重複・長さ。"""

    def test_two_distinct_safe_divides_collapse_in_list_membership(self):
        """
        分類: 既知の設計上の問題

        == が常に True のため、「別の QS」を二回 append しても len は 1。
        """
        lst = []
        a = safe_divide(100, 0)
        b = safe_divide(999, 0)
        if a not in lst:
            lst.append(a)
        if b not in lst:
            lst.append(b)
        assert len(lst) == 1


class TestSetSemantics:
    """集合（set）：重複排除用。要素は hash 可能である必要がある。"""

    def test_quantum_state_unhashable_cannot_build_set(self):
        """
        分類: 現状仕様の記録

        QuantumState は hash 不可のため set に入れると TypeError。
        """
        a = safe_divide(100, 0)
        b = safe_divide(999, 0)
        with pytest.raises(TypeError):
            {a, b}

    def test_single_quantum_in_set_via_manual_attempt(self):
        """
        分類: 現状仕様の記録

        1 つだけ追加しようとしても unhashable で失敗する。
        """
        q = safe_divide(1, 0)
        with pytest.raises(TypeError):
            {q}


class TestDictSemantics:
    """辞書（dict）のキー。"""

    def test_quantum_state_cannot_be_dict_key(self):
        """
        分類: 現状仕様の記録

        キーにすると TypeError（unhashable）。
        """
        q = safe_divide(100, 0)
        with pytest.raises(TypeError):
            {q: "value"}


class TestOrdering:
    """大小比較・min/max/sorted。"""

    def test_min_raises(self):
        """
        分類: 現状仕様の記録

        min() は < 比較が無いため TypeError。
        """
        vals = [safe_divide(1, 0), safe_divide(2, 0)]
        with pytest.raises(TypeError):
            min(vals)

    def test_max_raises(self):
        """
        分類: 現状仕様の記録

        max() も同様に TypeError。
        """
        vals = [safe_divide(1, 0), safe_divide(2, 0)]
        with pytest.raises(TypeError):
            max(vals)

    def test_sorted_raises(self):
        """
        分類: 現状仕様の記録

        sorted() も TypeError。
        """
        vals = [safe_divide(3, 0), safe_divide(1, 0)]
        with pytest.raises(TypeError):
            sorted(vals)

    def test_greater_than_int_raises(self):
        """
        分類: 現状仕様の記録

        density > 10 は TypeError（閾値判定に使えない）。
        """
        density = safe_divide(100, 0)
        with pytest.raises(TypeError):
            _ = density > 10


@pytest.mark.xfail(reason="既知の設計上の問題：被除数で QuantumState を区別できる等価性が欲しい")
def test_future_equality_distinguishes_dividend():
    """
    分類: 将来の改善目標

    将来: 被除数が違えば == は False になる想定。
    """
    assert safe_divide(100, 0) != safe_divide(999, 0)