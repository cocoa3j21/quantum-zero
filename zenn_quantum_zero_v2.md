---
title: "QuantumZero v2：ブラックホールでは解けないが、監査ログなら残る"
emoji: "⎔"
type: "tech"
topics: ["Python", "量子力学", "ブラックホール", "テスト", "設計"]
published: true
# Zenn 公開: https://zenn.dev/cocoa3j21/articles/40d0f05d16b40f (2026-11-20)
# v1 前編: https://zenn.dev/cocoa3j21/articles/e612809f1ed613
---

# はじめに：前回の「天才的な無駄遣い」の続き

前回、暇人（筆者）が AI と語り合ってできた **QuantumZero v1** は、

> ゼロ除算を `QuantumState` にすれば、`* 0` で情報は復元できる！

という **宇宙を救う（つもりの）妄想** でした。

スクレイピングが `ZeroDivisionError` で止まらなくなる、という副作用付き。

……ところが **pytest を書いたら、自分で自分の顔を殴る結果** になりました。

- `QuantumState == QuantumState` は、中身が違っても **常に True**
- 合計や `+=` が **静かに壊れる**
- `* 0` で戻るのは **safe_divide 直後だけ**（一回足し算したらおしまい）

物理学の「ブラックホール情報パラドックス」を解いたわけではなく、  
**「情報は失われない」という主張は、数学的にも物理的にも誤り** だと調査メモに冷静に書かれています（リポジトリ内 `quantum_physics_research/INVESTIGATION.md`）。

というわけで続編です。  
**物理学の解決編ではありません。監査ログ設計の実験編です。**

---

# 免責：これは物理学の論文ではない

冒頭に固定文言を置きます（Zenn でも GitHub でも同じ）。

- 本リポジトリは **ゼロ除算をどう扱うか** の **プログラミング実験** です。
- ブラックホール・量子場・ユニタリ性の話は **比喩（メタファー）** です。
- **標準的な宇宙論・量子重力の「答え」を提供しません。**
- 本番の請求・安全制御・医療計算の代替 **には使わないでください。**

「AI と検証したから物理的に正しい」などと **は書きません**。  
根拠は **`pytest` の実行結果** と、自分で書いた調査メモだけです。

---

# v1 の `QuantumState` と `* 0` の限界

## 何が便利だったか

```python
from quantum_zero import safe_divide

density = safe_divide(100, 0)
restored = density * 0   # → 100 になる（直後のみ）
```

デモ上は **「ホーキング放射のあとも、ゼロを掛ければ被除数が戻る」** というネタに使えました。

## 何がダメだったか（pytest が教えてくれた）

リポジトリの **現状仕様ロック用テスト**（計 50 本＋α）では、次が **意図的に記録** されています。

| 現象 | テスト的な意味 |
|------|----------------|
| 別の `QuantumState` 同士が `== True` | 辞書・リストで **区別できない** |
| `(density + 1) * 0` は 100 に戻らない | **情報復元は一度の演算で途切れる** |
| `total += safe_divide(...)` で型が化ける | **静かにパイプラインが壊れる** |
| `min` / `max` / `>` は `TypeError` | 数値として扱えない |

つまり v1 の `* 0` は、

- **数学的復元ではない**（0 を掛けて元の商が戻る、という代数は成り立たない）
- **プログラム設計としても罠だらけ**

……という結論です。

妄想は楽しい。でも **監査可能なソフトウェア** には向いていませんでした。

---

# v2 の `AuditState`：`resolve` と `raise_if_undefined`

v2（`quantum_zero_v2.py`）では、名前からも **量子状態をやめました**。  
代わりに **監査（audit＝記録・追跡）可能な未定義状態** `AuditState` です。

## 心構え

- `* 0` しても **数値に戻らない**（未定義は未定義のまま伝播）
- 「元の被除数を見たい」は **`restore()`** だけ（**比喩用**。数学的正当化ではない）
- ちゃんと数に戻す／止めるのは **呼び手の明示 API**

```python
from quantum_zero_v2 import safe_divide, AuditState

state = safe_divide(100, 0)
assert isinstance(state, AuditState)

# 黙って 0 扱い、などはしない
value = state.resolve(0)              # 代わりに 0 を使うと決める
# state.raise_if_undefined()          # ここで初めて例外にしてもよい

print(state.to_log())    # 1 行ログ
print(state.to_dict())   # 辞書（CSV/JSON 向け）
```

### `resolve(default=None)`

- 未定義なら `default` を返す
- `default` が省略されて `None` のときは **`ZeroDivisionError`**

「いつ例外に戻すか」を **コードの一目で分かる場所** に寄せました。

### `raise_if_undefined()`

- 未定義なら **即 `ZeroDivisionError`**
- バッチの最後に **まとめて人間に渡す** とき用

前回の「絶対に止まらない」から、**「止めるタイミングを選べる」** へ。

---

# `HorizonLogger`：イベントホライズンは比喩、中身は辞書リスト

APPLICATIONS.md の **案2** を、最小実装しました（`horizon_logger.py`）。

**イベントホライズン（事象の地平線）** ＝ 物理学用語ですが、ここでは  
**「計算パイプラインの中では未確定だが、ログとしては外に出す境界」** という比喩だけです。

```python
from horizon_logger import HorizonLogger

logger = HorizonLogger()

density = logger.observe(100, 0)   # AuditState
ratio   = logger.observe(10, 2)    # 5.0（記録なし）

records = logger.flush()           # 未定義だけ to_dict() のリスト
logger.raise_if_any()              # 一度でも未定義があれば ZeroDivisionError
```

- `observe` … `safe_divide` の薄いラッパ
- `flush` … 監査レコードを回収（バッファは空になるが、未定義フラグは残る）
- `raise_if_any` … **「もう黙ってスキップしない」** ための最終関門

ブラックホールの **情報パラドックスの解** ではありません。  
**「黙って欠損しないログ」** の実験です。

---

# pytest で何が言えるか

ローカルで実行した結果（記事執筆時点）：

```text
python -m pytest tests/ -v --tb=short

======================== 70 passed, 4 xfailed in 0.21s ========================
```

内訳の読み方：

| 区分 | 件数 | 意味 |
|------|------|------|
| **passed** | 70 | 今の仕様として **再現できた挙動** |
| **xfailed** | 4 | v1 の **「将来直したい」設計問題**（失敗が期待どおり） |
| **HorizonLogger** | 6 passed | 監査ログ最小版のテスト |

v1 は **アンチパターンの博物館** として残し、テストで **「やってはいけないこと」** を固定。  
v2 と `HorizonLogger` は **これから伸ばす幹**、という位置づけです。

「なんとなく動く」ではなく、**ターミナルに緑色の数字が出るまで** が暇人のゴールでした。

---

# v1 → v2 の一行まとめ

| | v1 `QuantumState` | v2 `AuditState` + `HorizonLogger` |
|--|-------------------|-----------------------------------|
| タグライン | ゼロ除算を量子状態に | ゼロ除算を **記録** する |
| 復元 | `* 0`（罠多し） | `restore()` は比喩、`resolve()` は明示 |
| 同一性 | 全部同じと見なす | 被除数・除数・理由で区別 |
| 物理学 | 語りが盛れがち | **比喩のみ** と明記 |

---

# おわりに：失敗した仮説は、教材になる

前回の記事は「ブラックホールでゼロ除算を殴り飛ばす」系のノリでした。  
続編で分かったのは、

- **面白い物語** と **正しい設計** は別物
- 物語は `quantum_physics_research/` に隔離し、コードは **監査ログ** に寄せた方が、読者も筆者も安全

意外とまとも、というのは宇宙論の問題が**解けた**からではなく、  
**「未定義をオブジェクトとして扱い、ログと `resolve` で責任の所在を決める」** という地味な設計が、テストで**示唆**として支えられたからです（玩具・解釈実験）。

暇人と AI の妄想は続きます。ただし次は **妄想の末尾に pytest を置く** 誓いをしました。

---

# リンク

- **GitHub（ソース）:** https://github.com/cocoa3j21/quantum-zero  
- **Buy Me a Coffee:** https://www.buymeacoffee.com/cocoa3j21  

「監査ログにコーヒー1杯分のカフェインを」と言うとかっこいいので、  
そういう建前で投げ銭を受け付けています（ブラックホール観測予算、と前作ネタで言い続けてもよい）。

---

# 参考（リポジトリ内）

| ファイル | 内容 |
|----------|------|
| `quantum_zero.py` | v1（変更せず温存） |
| `quantum_zero_v2.py` | v2 `AuditState` |
| `horizon_logger.py` | 監査ログ最小版 |
| `quantum_physics_research/INVESTIGATION.md` | 物理とコードの線引き |
| `quantum_physics_research/APPLICATIONS.md` | 応用案と採用理由 |
| `tests/` | 仕様ロック（v1 契約 + v2 + HorizonLogger） |

---

*ローカル原稿。公開記事: [Zenn v2](https://zenn.dev/cocoa3j21/articles/40d0f05d16b40f)。エディタ差し替えは任意。*