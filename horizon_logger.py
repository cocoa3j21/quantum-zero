"""
HorizonLogger — AuditState の監査バッファ（案2 最小実装）

ブラックホール情報パラドックスの比喩として「測定はできないが記録は外へ出す」層。
物理学の情報保存を主張するものではない。
"""

from __future__ import annotations

from typing import Any

from quantum_zero_v2 import AuditState, NumericResult, safe_divide


class HorizonLogger:
    """safe_divide の結果のうち未定義（AuditState）だけ to_dict() として蓄積する。"""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []
        self._undefined_count: int = 0

    def observe(self, dividend: int | float, divisor: int | float) -> NumericResult:
        """除算し、AuditState なら辞書を内部バッファへ追加してから結果を返す。"""
        result = safe_divide(dividend, divisor)
        if isinstance(result, AuditState):
            self._undefined_count += 1
            self._records.append(result.to_dict())
        return result

    def flush(self) -> list[dict[str, Any]]:
        """蓄積した記録のコピーを返し、バッファだけを空にする。"""
        snapshot = list(self._records)
        self._records.clear()
        return snapshot

    def raise_if_any(self) -> None:
        """observe 以降に未定義が1件でもあれば ZeroDivisionError。"""
        if self._undefined_count > 0:
            raise ZeroDivisionError(
                f"HorizonLogger: undefined division recorded {self._undefined_count} time(s)"
            )