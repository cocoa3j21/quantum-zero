"""HorizonLogger（監査ログ最小版）のテスト。"""

import pytest

from horizon_logger import HorizonLogger
from quantum_zero_v2 import AuditState


class TestHorizonLoggerBasics:
    def test_observe_zero_divisor_returns_audit_state(self):
        """
        分類: 現状仕様の記録

        observe(100, 0) は AuditState を返す。
        """
        logger = HorizonLogger()
        result = logger.observe(100, 0)
        assert isinstance(result, AuditState)

    def test_flush_returns_one_record_after_undefined(self):
        """
        分類: 現状仕様の記録

        未定義1件のあと flush() は1件の辞書リストを返す。
        """
        logger = HorizonLogger()
        logger.observe(100, 0)
        records = logger.flush()
        assert len(records) == 1
        assert records[0]["dividend"] == 100
        assert records[0]["divisor"] == 0
        assert records[0]["is_undefined"] is True

    def test_raise_if_any_raises_after_undefined(self):
        """
        分類: 現状仕様の記録

        未定義を observe したあと raise_if_any() は ZeroDivisionError。
        """
        logger = HorizonLogger()
        logger.observe(100, 0)
        logger.flush()
        with pytest.raises(ZeroDivisionError):
            logger.raise_if_any()

    def test_normal_division_not_recorded(self):
        """
        分類: 現状仕様の記録

        observe(10, 2) は通常の数値で、flush は空。
        """
        logger = HorizonLogger()
        result = logger.observe(10, 2)
        assert result == 5.0
        assert logger.flush() == []
        logger.raise_if_any()  # 例外なし

    def test_multiple_undefined_recorded(self):
        """
        分類: 現状仕様の記録

        複数の未定義がそれぞれ記録される。
        """
        logger = HorizonLogger()
        logger.observe(100, 0)
        logger.observe(50, 0)
        records = logger.flush()
        assert len(records) == 2
        dividends = {r["dividend"] for r in records}
        assert dividends == {100, 50}

    def test_mixed_normal_and_undefined(self):
        """
        分類: 現状仕様の記録

        正常と異常が混ざっても記録は異常分だけ。
        """
        logger = HorizonLogger()
        logger.observe(10, 2)
        logger.observe(7, 0)
        logger.observe(8, 4)
        records = logger.flush()
        assert len(records) == 1
        assert records[0]["dividend"] == 7
        with pytest.raises(ZeroDivisionError):
            logger.raise_if_any()