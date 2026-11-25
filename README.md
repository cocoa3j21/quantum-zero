# QuantumZero

**ゼロ除算をどう扱うか**を、ブラックホールや宇宙の比喩で遊びながらコードにした、小さな実験用ライブラリです。  
物理公式の正しさを証明するものではありません。Zenn の記事を読んだあと、この README だけで v1 / v2 の使い分けが分かるように書いています。

| リンク | URL |
|--------|-----|
| GitHub（本リポジトリ） | https://github.com/cocoa3j21/quantum-zero |
| **Zenn v2（監査ログ）** | **[公開済み](https://zenn.dev/cocoa3j21/articles/40d0f05d16b40f)** |
| Zenn v1（比喩デモ） | [公開済み](https://zenn.dev/cocoa3j21/articles/e612809f1ed613) |
| Labs 索引（開発正本の親） | [`../README.md`](../README.md) |
| Buy Me a Coffee | https://www.buymeacoffee.com/cocoa3j21 |

**ライセンス:** [MIT License](LICENSE)

## 開発正本と公開リポジトリ

| 役割 | 場所 |
| :--- | :--- |
| **開発正本** | `D:\Workspace\Labs\blackhole_sim\`（ワークスペース内。`ai-budget-meter` にはサブツリーとして未収録） |
| **公開リポジトリ（一本化）** | [github.com/cocoa3j21/quantum-zero](https://github.com/cocoa3j21/quantum-zero)（`origin` のみ） |
| **Zenn** | v2 [40d0f05d16b40f](https://zenn.dev/cocoa3j21/articles/40d0f05d16b40f)（公開）· 原稿 [`zenn_quantum_zero_v2.md`](zenn_quantum_zero_v2.md) · v1 [e612809f1ed613](https://zenn.dev/cocoa3j21/articles/e612809f1ed613) |

**テスト（2026-11-25）:** `python -m pytest -q` → **70 passed**, **4 xfailed**（v1 の既知設計課題を記録した期待失敗）。

---

## QuantumZero とは

Python では `10 / 0` のように **0 で割ると `ZeroDivisionError`（ゼロ除算エラー）** になり、プログラムが止まります。

QuantumZero は、そのときに代わりに **特別な状態オブジェクト** を返し、デモや実験的パイプラインを止めずに進める仕組みです。

- **v1**（`quantum_zero.py`）… `QuantumState`。**`* 0` で被除数が戻る**など、情報パラドックスの**比喩デモ**向け。
- **v2**（`quantum_zero_v2.py`）… `AuditState`。**いつ・何を 0 で割ったかを記録**し、あとから `resolve()` などで**明示的に**扱う向け。

---

## v1 と v2 の違い（一覧）

| 項目 | v1 `QuantumState` | v2 `AuditState` |
|------|-------------------|-----------------|
| ねらい | 比喩的な「情報復元」デモ | 監査（audit＝記録・追跡）可能な未定義状態 |
| 0 除算後の `* 0` | 直後なら**数値**が戻る場合がある | 常に **AuditState のまま** |
| 復元 | `* 0` に埋め込み | **`restore()`** のみ（比喩・明示 API） |
| 同士の `==` | どの QS も **常に True** | 被除数・除数・理由が同じときだけ True |
| dict / set | 使いにくい（キーにできない） | **キー・要素に使える** |
| 未定義の見分け | 公開 API ほぼ無し | `is_undefined`, `to_log()`, `to_dict()` |
| 数値として続ける | 暗黙の挙動が多い | **`resolve()` / `raise_if_undefined()`** |

**おすすめ:** 記事・デモの雰囲気は **v1**、ログや「あとでどうするか決める」コードは **v2**。

---

## v1: QuantumState

- ファイル: [`quantum_zero.py`](quantum_zero.py)
- `safe_divide(質量, 距離)` … 距離が 0 のとき `QuantumState`、それ以外は通常の数値（float）
- `QuantumState * 0` … **safe_divide 直後**なら被除数が返る比喩（一度でも足し算などすると復元できない）
- 詳しい挙動は `tests/test_quantum_state_contract.py` などに **現状仕様として固定** 済み

### v1 最小例

```python
from quantum_zero import safe_divide

density = safe_divide(100, 0)
print(density)       # QuantumState(dividend=100)
print(density * 0)   # 100（比喩的な「復元」）
```

### v1 の 4 デモ

ルートで実行すると、次の 4 シミュレーションが順に動きます。

```bash
cd Labs/blackhole_sim   # リポジトリを clone した場合は blackhole_sim へ
python quantum_zero.py
```

| # | 内容 |
|---|------|
| 1 | ブラックホール（距離 r → 0） |
| 2 | ビッグバン（時刻 t → 0 を超える） |
| 3 | 自己エネルギー（r → 0 の発散） |
| 4 | 情報パラドックス（`* 0` で被除数復元のデモ） |

---

## v2: AuditState

- ファイル: [`quantum_zero_v2.py`](quantum_zero_v2.py)
- `safe_divide(dividend, divisor)` … divisor が 0 のとき `AuditState`（例外なし）
- **監査情報:** 被除数・除数・理由・作成時刻・説明文
- **明示 API:** `resolve()`, `raise_if_undefined()`, `restore()`, `to_log()`, `to_dict()`

### v2 最小例

```python
from quantum_zero_v2 import AuditState, safe_divide

state = safe_divide(100, 0)
assert isinstance(state, AuditState)
assert state.is_undefined

print(state.to_log())              # ログ1行
print(state.resolve(0))            # 代わりに 0 を使う
# state.raise_if_undefined()      # ここで初めて ZeroDivisionError にしてもよい
```

`restore()` は被除数を返しますが、**数学的に 0 除算を正しい結果にするものではありません**（デモ用の比喩です）。

### v2 の 8 デモ

```bash
python quantum_zero_v2.py
```

| # | 関数 | 内容 |
|---|------|------|
| 1 | `simulate_blackhole_v2` | ブラックホール |
| 2 | `simulate_bigbang_v2` | ビッグバン |
| 3 | `simulate_self_energy_v2` | 自己エネルギー |
| 4 | `simulate_information_paradox_v2` | 情報パラドックス（`restore()` と `* 0` の違い） |
| 5 | `simulate_auditable_undefined` | `to_dict()` の監査記録 |
| 6 | `simulate_resolve` | `resolve(default)` |
| 7 | `simulate_raise_if_undefined` | 例外に戻す |
| 8 | `simulate_to_log` | ログ1行出力 |

---

## テスト（pytest）

**pytest** … Python 用の自動テストツールです。

```bash
cd Labs/blackhole_sim
python -m pip install pytest    # 初回のみ
python -m pytest tests/ -v --tb=short
```

| テスト群 | ファイル | 役割 |
|----------|----------|------|
| v1 契約 | `test_quantum_state_contract.py` ほか v1 系 4 ファイル | 現状仕様の固定・既知の問題の記録 |
| v2 | `test_quantum_zero_v2.py` | AuditState の必須 API |

開発用依存は `pyproject.toml` の `dev` オプション（`pytest` のみ）に記載しています。

```bash
python -m pip install -e ".[dev]"
```

---

## これは何で、何でないか

### これは

- Zenn 記事や GitHub とつなげる **実験・デモ用** のサンプル
- 「0 除算をどう設計するか」を議論するための **2 つの対照実装**（v1 比喩 / v2 監査）
- **学習用**のシミュレーション出力（宇宙・ブラックホールのたとえ）

### これではない

- 物理学や宇宙論の正当なシミュレータ
- 銀行・医療・インフラなど **本番のクリティカルな計算** のゼロ除算対策
- 「ゼロ除算を数学的に正しく解く」ライブラリ

---

## 本番環境での使用に関する注意

- **v1** は合計・平均・`+=` が **静かに別の型** になるなど、既知の設計上の問題があります（テストに記録済み）。
- **v2** でも `bool(AuditState)` は常に **True** です。**if 文だけでは「正常」とは判定できません。** `is_undefined` や `resolve()` を使ってください。
- **v2** の `AuditState` は `min` / `max` / `sorted` / `<` などで **TypeError** になります（未定義同士を大小比較できないため）。
- いずれも **必ずテストを読み、自分の用途で再検証** してから使ってください。

---

## プロジェクト構成

```
blackhole_sim/
├── quantum_zero.py          # v1
├── quantum_zero_v2.py       # v2
├── quantum_physics_research/  # QuantumZero と物理学の関係（調査メモ）
├── tests/
├── README.md
├── LICENSE
├── pyproject.toml
└── .gitignore
```

物理学・数学の正確な位置づけは [quantum_physics_research/INVESTIGATION.md](quantum_physics_research/INVESTIGATION.md) を参照してください（コードの比喩と現実の量子論を分けて記載）。

---

## 今後の予定

比喩デモと監査 API の**解釈実験**です。物理学の「正解」や本番保証とは書きません。

| # | 項目 | 状態 |
| :---: | :--- | :--- |
| 1 | pytest 回帰 | **確認済み**（2026-11-25: 70 passed / 4 xfailed） |
| 2 | Zenn v2 | **公開済み** — [記事](https://zenn.dev/cocoa3j21/articles/40d0f05d16b40f)（2026-11-20） |
| 3 | リモート一本化 | **済** — 公開先は [quantum-zero](https://github.com/cocoa3j21/quantum-zero) のみ（Labs 索引からリンク） |

---

## Support

記事やコードが役に立った・面白かったら、激励やコーヒー代をいただけると嬉しいです。

- [Buy Me a Coffee](https://www.buymeacoffee.com/cocoa3j21)
- [GitHub](https://github.com/cocoa3j21)

---

## MIT License

Copyright (c) 2026 cocoa3j21

詳細は [LICENSE](LICENSE) を参照してください。