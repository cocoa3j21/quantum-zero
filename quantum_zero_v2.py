"""
Quantum Zero v2 — 監査可能な未定義状態（AuditState）

概要
----
ゼロ除算などの異常を「なかったこと」にせず、**AuditState** として記録しつつ
処理を継続できるようにする実験用モジュールです。物理公式の正しさは主張しません。

AuditState とは
---------------
**異常を記録しつつ処理を継続する状態オブジェクト**です。
被除数・除数・理由・発生時刻などを保持し、四則演算しても未定義フラグは伝播します。

重要な挙動
----------
- ``restore()`` … 被除数を返す **比喩** であり、数学的な 0 除算の正当化ではありません。
- ``bool(AuditState)`` … 常に True。**「正常な数値」とは判定できません。**
  ``is_undefined`` や ``resolve()`` / ``raise_if_undefined()`` を使ってください。
- ``min`` / ``max`` / ``sorted`` および ``<``, ``>`` など … **TypeError**
  （未定義状態を大小比較できない旨のメッセージ付き）。

本番利用
--------
請求・在庫・安全制御など **クリティカルな計算の本体には使わない** でください。
デモ・学習・ログ付きパイプラインのプロトタイプ向けです。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Union

Number = Union[int, float]
NumericResult = Union[int, float, "AuditState"]


class AuditState:
    """
    異常（例: ゼロ除算）を記録しつつ、後続処理を継続するための監査可能な状態オブジェクト。

    - 四則演算後も ``is_undefined`` は真のまま伝播します（``* 0`` でも数値に戻りません）。
    - ``restore()`` は被除数を返す **ストーリー上の比喩** であり、数学的復元ではありません。
    - ``bool(state)`` は常に True です。**正常判定には使えません。**
      ``is_undefined`` / ``resolve()`` / ``raise_if_undefined()`` を使ってください。
    - ``min(state, ...)`` や ``state > 0`` は **TypeError** になります。

    本番のクリティカルな数値計算にそのまま組み込まないでください。
    """

    __slots__ = (
        "original_dividend",
        "original_divisor",
        "reason",
        "created_at",
        "is_undefined",
        "description",
    )

    def __init__(
        self,
        *,
        original_dividend: Number,
        original_divisor: Number,
        reason: str,
        created_at: str,
        is_undefined: bool = True,
        description: str = "",
    ) -> None:
        self.original_dividend = original_dividend
        self.original_divisor = original_divisor
        self.reason = reason
        self.created_at = created_at
        self.is_undefined = is_undefined
        self.description = description or (
            f"undefined: {original_dividend} / {original_divisor} ({reason})"
        )

    def __repr__(self) -> str:
        return (
            f"AuditState(dividend={self.original_dividend!r}, "
            f"divisor={self.original_divisor!r}, reason={self.reason!r})"
        )

    def __str__(self) -> str:
        return f"⎔ {self.description}"

    def _derived(self, new_description: str) -> "AuditState":
        """演算後も元の監査情報を引き継いだ新しい AuditState を作る。"""
        return AuditState(
            original_dividend=self.original_dividend,
            original_divisor=self.original_divisor,
            reason=self.reason,
            created_at=self.created_at,
            is_undefined=self.is_undefined,
            description=new_description,
        )

    def _comparison_error(self, other: Any, op: str) -> TypeError:
        return TypeError(
            f"未定義状態（AuditState）は大小比較できません: "
            f"{self!r} {op} {other!r}。resolve() または raise_if_undefined() を使ってください。"
        )

    # --- 四則演算（未定義は常に伝播） ---

    def __add__(self, other: Any) -> "AuditState":
        if isinstance(other, AuditState):
            return self._derived(f"({self.description}) + ({other.description})")
        return self._derived(f"({self.description}) + {other}")

    def __sub__(self, other: Any) -> "AuditState":
        if isinstance(other, AuditState):
            return self._derived(f"({self.description}) - ({other.description})")
        return self._derived(f"({self.description}) - {other}")

    def __mul__(self, other: Any) -> "AuditState":
        if isinstance(other, AuditState):
            return self._derived(f"({self.description}) × ({other.description})")
        return self._derived(f"({self.description}) × {other}")

    def __truediv__(self, other: Any) -> "AuditState":
        if isinstance(other, AuditState):
            return self._derived(f"({self.description}) ÷ ({other.description})")
        return self._derived(f"({self.description}) ÷ {other}")

    def __radd__(self, other: Any) -> "AuditState":
        return self._derived(f"{other} + ({self.description})")

    def __rsub__(self, other: Any) -> "AuditState":
        return self._derived(f"{other} - ({self.description})")

    def __rmul__(self, other: Any) -> "AuditState":
        return self._derived(f"{other} × ({self.description})")

    def __rtruediv__(self, other: Any) -> "AuditState":
        return self._derived(f"{other} ÷ ({self.description})")

    # --- 等価性・ハッシュ ---

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AuditState):
            return False
        return (
            self.original_dividend == other.original_dividend
            and self.original_divisor == other.original_divisor
            and self.reason == other.reason
        )

    def __hash__(self) -> int:
        return hash((self.original_dividend, self.original_divisor, self.reason))

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    # --- 比較（禁止） ---

    def __lt__(self, other: Any) -> bool:
        raise self._comparison_error(other, "<")

    def __le__(self, other: Any) -> bool:
        raise self._comparison_error(other, "<=")

    def __gt__(self, other: Any) -> bool:
        raise self._comparison_error(other, ">")

    def __ge__(self, other: Any) -> bool:
        raise self._comparison_error(other, ">=")

    def __bool__(self) -> bool:
        """常に True。数値のゼロ判定の代わりには使えません。"""
        return True

    # --- 監査・復元 API ---

    def restore(self) -> Number:
        """
        保存されていた被除数（original_dividend）を返す。

        これはデモ上の「情報は失われない」という比喩であり、
        数学的に 0 除算した結果を正当化するものではありません。
        """
        return self.original_dividend

    def resolve(self, default: Any = None) -> Any:
        """
        未定義なら default を返す。default が None のときは ZeroDivisionError。
        未定義でなければ自身を返す。
        """
        if self.is_undefined:
            if default is None:
                raise ZeroDivisionError(
                    f"ゼロ除算相当の未定義状態: {self.original_dividend} / {self.original_divisor}"
                )
            return default
        return self

    def raise_if_undefined(self) -> "AuditState":
        """未定義なら ZeroDivisionError。未定義でなければ自身を返す。"""
        if self.is_undefined:
            raise ZeroDivisionError(
                f"ゼロ除算相当の未定義状態: {self.original_dividend} / {self.original_divisor}"
            )
        return self

    def to_log(self) -> str:
        """ログや CSV 1 行向けの文字列。"""
        return (
            f"created_at={self.created_at}"
            f"\tdividend={self.original_dividend}"
            f"\tdivisor={self.original_divisor}"
            f"\treason={self.reason}"
            f"\tis_undefined={self.is_undefined}"
            f"\tdescription={self.description}"
        )

    def to_dict(self) -> dict[str, Any]:
        """構造化データ（JSON 化しやすい辞書）。"""
        return {
            "dividend": self.original_dividend,
            "divisor": self.original_divisor,
            "reason": self.reason,
            "is_undefined": self.is_undefined,
            "created_at": self.created_at,
            "description": self.description,
        }


def safe_divide(dividend: Number, divisor: Number) -> NumericResult:
    """
    除算を行う。divisor が 0 のとき例外は出さず AuditState を返す。

    Returns:
        float | int: 通常の除算結果
        AuditState: divisor == 0 のとき
    """
    if divisor == 0:
        created = datetime.now(timezone.utc).isoformat()
        return AuditState(
            original_dividend=dividend,
            original_divisor=divisor,
            reason="zero_divisor",
            created_at=created,
            is_undefined=True,
            description=f"zero division: {dividend} / {divisor}",
        )
    return dividend / divisor


# --- デモ（v1 と同テーマ + 監査 API） ---


def simulate_blackhole_v2() -> None:
    """ブラックホール特異点（監査状態で密度を追跡）。"""
    mass = 100
    distance = 10
    print("=" * 60)
    print("🚀 [v2] ブラックホール特異点シミュレーター")
    print("=" * 60)
    while distance >= 0:
        density = safe_divide(mass, distance)
        if isinstance(density, AuditState):
            print(f"  r={distance} → 未定義密度: {density.to_log()}")
            break
        print(f"  r={distance} → 密度={density:.4f}")
        distance -= 1
    print()


def simulate_bigbang_v2() -> None:
    """ビッグバン特異点（t=0 で AuditState）。"""
    constant = 100
    print("=" * 60)
    print("🌌 [v2] ビッグバン特異点")
    print("=" * 60)
    for t in range(5, -1, -1):
        d = safe_divide(constant, t)
        if isinstance(d, AuditState):
            print(f"  t={t} → {d}")
        else:
            print(f"  t={t} → 密度={d:.2f}")
    print()


def simulate_self_energy_v2() -> None:
    """自己エネルギー発散（r=0）。"""
    charge = 1.602e-19
    print("=" * 60)
    print("⚛️  [v2] 自己エネルギー発散")
    print("=" * 60)
    for r in range(3, -1, -1):
        e = safe_divide(charge, r)
        if isinstance(e, AuditState):
            print(f"  r={r} → {e}")
        else:
            print(f"  r={r} → E={e:.6e}")
    print()


def simulate_information_paradox_v2() -> None:
    """情報パラドックス比喩 — restore() は * 0 とは別。"""
    mass = 100
    print("=" * 60)
    print("🔐 [v2] 情報パラドックス（restore は比喩）")
    print("=" * 60)
    density = safe_divide(mass, 0)
    print(f"  密度: {density}")
    print(f"  * 0 はまだ AuditState: {density * 0!r}")
    print(f"  restore() → {density.restore()!r}")
    print()


def simulate_auditable_undefined() -> None:
    """監査可能な未定義状態の例。"""
    print("=" * 60)
    print("📋 [v2] 監査可能な未定義状態")
    print("=" * 60)
    state = safe_divide(42, 0)
    assert isinstance(state, AuditState)
    print(state.to_dict())
    print(state.to_log())
    print()


def simulate_resolve() -> None:
    """resolve で明示的にフォールバック。"""
    print("=" * 60)
    print("🛡️  [v2] resolve")
    print("=" * 60)
    state = safe_divide(100, 0)
    assert isinstance(state, AuditState)
    print(f"  resolve(0) → {state.resolve(0)}")
    try:
        state.resolve()
    except ZeroDivisionError as err:
        print(f"  resolve() → ZeroDivisionError: {err}")
    print()


def simulate_raise_if_undefined() -> None:
    """raise_if_undefined で例外化。"""
    print("=" * 60)
    print("⚠️  [v2] raise_if_undefined")
    print("=" * 60)
    state = safe_divide(7, 0)
    assert isinstance(state, AuditState)
    try:
        state.raise_if_undefined()
    except ZeroDivisionError as err:
        print(f"  → {err}")
    print()


def simulate_to_log() -> None:
    """to_log 出力例。"""
    print("=" * 60)
    print("📝 [v2] to_log")
    print("=" * 60)
    line = safe_divide(1, 0)
    assert isinstance(line, AuditState)
    print(line.to_log())
    print()


if __name__ == "__main__":
    simulate_blackhole_v2()
    simulate_bigbang_v2()
    simulate_self_energy_v2()
    simulate_information_paradox_v2()
    simulate_auditable_undefined()
    simulate_resolve()
    simulate_raise_if_undefined()
    simulate_to_log()