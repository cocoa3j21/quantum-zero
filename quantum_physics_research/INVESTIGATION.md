# QuantumZero と量子論 — 調査レポート（初版）

**作成日:** 2026-11-20  
**対象コード:** `../quantum_zero.py`（v1）、`../quantum_zero_v2.py`（v2）  
**方針:** **事実**（教科書・論文・公式資料に書かれていること）と **推測・比喩**（コード作者の意図や命名から読み取れること）を分けて記す。

---

## 0. この文書の読み方

| ラベル | 意味 |
|--------|------|
| **【事実】** | 数学・物理学の標準的記述。下の「参考文献」から辿れる。 |
| **【コードの事実】** | リポジトリ内の実装・pytest で固定された挙動。 |
| **【比喩・設計意図】** | README やデモが示すストーリー。物理学の定理ではない。 |
| **【調査者の整理】** | 上記を突き合わせた結論・類似点の指摘（議論のたたき台）。 |

---

## 1. ゼロ除算と「0 に近づける極限」の違い

### 1.1 初心者向け解説

**除算（わり算）** は「かけると元に戻る数」を求める操作です。  
 \(a \div b = q\) は、\(q \times b = a\) が成り立つ \(q\) を探す、と定義されます。

**【事実】** 実数（ふつうの数直線上の数）では、\(b = 0\) のとき \(q \times 0 = 0\) しかできないので、\(a \neq 0\) なら \(q\) は存在しません。だから **\(a \div 0\) は「未定義」** です（0 で割ることはできない、というルール）。

**極限（リミット）** は別の話です。「点 \(x = 0\) そのもの」ではなく、**0 にどんどん近づく \(x\)** で式の値がどう振る舞うかを調べます。

**【事実】** 例: \(f(x) = 1/x\)。\(x = 0\) では定義できませんが、

\[
\lim_{x \to 0^+} \frac{1}{x} = +\infty,\quad
\lim_{x \to 0^-} \frac{1}{x} = -\infty
\]

のように「限界の振る舞い」は数学的に議論できます（[Wikipedia: Division by zero](https://en.wikipedia.org/wiki/Division_by_zero)、[Wolfram MathWorld: Division by Zero](https://mathworld.wolfram.com/DivisionbyZero.html)）。

**【事実】** 極限では **「\(x \neq 0\) のときだけ成り立つ等式」** を使ってから限界に入ります。  
例: \(x \neq 1\) のとき \(\frac{x^2-1}{x-1} = x+1\) なので、\(\lim_{x\to 1}\frac{x^2-1}{x-1} = 2\)（[Math.StackExchange 3185307](https://math.stackexchange.com/questions/3185307/why-can-we-divide-by-zero-in-limits)）。

**【事実】** 分子も分母も 0 に近づく \(\frac{0}{0}\) 型は **不定形（indeterminate form）** と呼ばれ、式ごとに答えが変わります。OpenStax の微積分教科書は、\(0/0\) は「実際に 0 を 0 で割っているのではなく、両方の極限が 0 である商の極限の記号」と説明しています（[OpenStax Calculus 4.8 L'Hôpital's Rule](https://openstax.org/books/calculus-volume-1/pages/4-8-lhopitals-rule)）。

### 1.2 QuantumZero との関係

| 話題 | 数学 | QuantumZero v1 |
|------|------|----------------|
| \(100 \div 0\) をその場で計算 | **未定義** | `safe_divide(100, 0)` → `QuantumState`（例外なし） |
| \(100 / x\) を \(x \to 0\) | 発散や不定形として極限で扱う | **コードは極限を計算しない**（\(x=0\) だけ特別扱い） |
| \(100 / 10^{-308}\) のような極小除算 | 巨大な有限値になりうる | **【コードの事実】** 通常の float 除算のまま（pytest で未カバーなら「未検証」） |

**【調査者の整理】** v1 の `safe_divide` は **「点 \(r=0\) での式の値」** を置き換えているのであって、**「\(r \to 0\) の極限」** を計算しているわけではありません。ブラックホールの「中心に近づく」デモは、物理学の極限処理の厳密なモデルではありません。

---

## 2. 量子場理論における発散・正則化・繰り込み

### 2.1 初心者向け解説

**量子場理論（QFT）** … 粒子ではなく「場」を量子化して、生成・消滅を扱う理論。素粒子物理学の標準的枠組みの一部です。

**【事実】** 摂動論（小さな摂動を級数で足す方法）でループ積分などを計算すると、ときに **発散（divergence）** — 答えが無限大に見える — が出ます（[Encyclopedia of Mathematics: Renormalization](https://encyclopediaofmath.org/wiki/Renormalization)）。

用語の短い説明:

| 用語 | 短い説明 |
|------|----------|
| **正則化（regularization）** | 発散を一時的に有限にする手続き（切断（cutoff）や次元正則化など）。**補助パラメータ**が入る。 |
| **繰り込み（renormalization）** | 有限化のあと、無限部分を **質量・結合定数・場の定義のやり直し** に吸収し、**観測可能な有限の予言** だけを残す。 |
| **紫外発散** | 非常に小さい距離・大きい運動量で悪化する発散。 |
| **赤外発散** | 長距離・零運動量側の発散（別問題として扱う）。 |

**【事実】** CERN の入門講義資料では、発散を除外して有限な予言を得るプロセスとして繰り込みの物理的アイデアが説明されています（[CERN Yellow Report 1996-004](https://doi.org/10.5170/cern-1996-004.1)、[Introductory Lectures on QFT (arXiv:hep-th/0510040)](https://arxiv.org/pdf/hep-th/0510040)）。  
CERN Courier の歴史記事は、QED で繰り込み後の計算が実験と高精度で一致したことから、繰り込みが「使える理論」の条件になった経緯を述べています（[Fifty years of the renormalization group](https://cern-courier.web.cern.ch/a/fifty-years-of-the-renormalization-group/)）。

### 2.2 正則化と AuditState の類似点・相違点

| | 量子場論の正則化＋繰り込み | QuantumZero v2 の `AuditState` |
|--|---------------------------|--------------------------------|
| **目的** | 無限大の中から **再現可能な有限の予測** を得る | プログラムを止めず **異常を記録** し、あとで `resolve` 等を選ぶ |
| **数学的地位** | 長い検証歴のある手続き（理論 community の標準） | **Python の自作クラス**（実験用） |
| **「元の値」** | 裸質量・裸結合定数は観測に直接出てこない | `original_dividend` を **ログ用に保持**（監査） |
| **演算** | 厳密な Feynman ルール・カウンター項 | **【コードの事実】** 四則演算で未定義が伝播（`* 0` でも数値に戻らない） |
| **終わり方** | 正則化パラメータの極限を取り、有限結果 | `resolve(0)` や `raise_if_undefined()` を **呼び手が明示** |

**【比喩・設計意図】** v2 は「異常を握りつぶさず記録する」点で、正則化前に「ここで発散が出た」と棚卸しする **運用上の気分** に少し似ます。

**【調査者の整理】** しかし QFT の正則化は **予測可能な物理量** と結びついた数学手続きであり、`AuditState` は **会計・監査のメタファ** に近いです。**同型の理論ではありません。**

---

## 3. ブラックホール情報パラドックスと量子力学

### 3.1 初心者向け解説

**【事実】** ホーキング（1975）は、量子効果によりブラックホールが熱的な粒子を放射する（ホーキング放射）ことを示しました（[Hawking 1975, Commun. Math. Phys. 43, 199–220](https://doi.org/10.1007/BF02345020)）。

**【事実】** その後の議論（情報パラドックス）の中心は次の衝突です。

1. **量子力学のユニタリ性（unitarity）** … 閉じた系の時間発展で **情報（純粋状態の識別可能性）が失われない** という原理（詳細は専門家の間で定式化の議論あり）。
2. **ホーキングの初期議論** … 放射が **完全に熱的** だと、蒸発完了後に **元の落入情報を一意に復元できない** のでは、という懸念（[Hawking 1976, Phys. Rev. D 14, 2460](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.14.2460)、解説系年表: [blackhole.org 年表](https://blackhole.org/reference/history/black-hole-thermodynamics-information/)）。
3. **ページ曲線（Page curve）** … **ユニタリ性を仮定** したモデルでは、放射のエントロピー（ざっくり「不確かさ」）が途中で減り始める、という予想（Page 1993。上記年表参照）。
4. **近年** … 「島（island）」公式などでページ曲線を再現する計算が進んだ一方、**解釈（何が「測定可能」か）** について活発な議論が続く（例: [arXiv:2601.11363](https://arxiv.org/html/2601.11363)、[arXiv:2602.06543](https://arxiv.org/html/2602.06543)、[JHEP 2025「An apologia for islands」](https://link.springer.com/article/10.1007/JHEP10(2025)034)）。

**【事実】** Nature Reviews Physics のレビューは、情報パラドックスが「重力と量子の深い矛盾」を表す未解決問題の一つだと述べています（[Black-hole thermodynamics (2026)](https://www.nature.com/articles/s42254-026-00942-9)）。

**未確定部分（専門家の間でも議論中）:** 完全な量子重力の最終答え、島の操作的な意味づけなど。**本レポートでは「現在も研究領域」とだけ記す。**

### 3.2 「情報保持」と QuantumZero

| | 物理学（情報パラドックスの文脈） | QuantumZero v1 |
|--|--------------------------------|----------------|
| 何の情報？ | 落入物質の量子状態と放射の **相関・ユニタリ性** | 被除数 `dividend` を `_dividend` に保存 |
| 復元の意味 | 放射の **微妙な相関** から状態を再構成（仮説・計算対象） | **`* 0` → 被除数**（【コードの事実】直後のみ） |
| 数学 | ヒルベルト空間・密度行列・エントロピー | Python の `__mul__` 特例 |

**【比喩・設計意図】** v1 のデモ `simulate_information_paradox` は、ホーキング放射と「情報が戻る」話を **ストーリーとして借りている**（README もデモ用途）。

**【調査者の整理】**  
- 物理学の「情報保存」と v1 の「`* 0` で 100 が戻る」は **同名異義** です。  
- v2 の `restore()` も docstring で **比喩であり数学的復元ではない** と明記されています。  
- いずれも **ブラックホール物理学の検証モデルではありません。**

---

## 4. QuantumState と量子力学の「量子状態」の違い

### 4.1 量子力学における量子状態（物理学）

**【事実】** 非相対論的量子力学では、系の状態は通常 **ヒルベルト空間（状態ベクトル）** または **密度行列** で表されます。観測結果の確率法則と、時間発展（シュレーディンガー方程式など）がこの表現に結びつきます（入門: [Stanford Encyclopedia of Philosophy: Quantum Mechanics](https://plato.stanford.edu/entries/qm/)）。

「量子状態」は **物理系の完全な（または統計的な）記述** であり、数値 \(100\) でも `QuantumState` でもありません。

### 4.2 QuantumZero の QuantumState（コード）

**【コードの事実】** `QuantumState` は Python クラスで、主に:

- ゼロ除算の結果を **文字列付きオブジェクト** として保持
- 四則演算で **別の `QuantumState`** を生成
- 一部演算（`* 0`）だけ **int/float に戻る**

**【調査者の整理】** 名前は「量子」だが、**ヒルベルト空間・重ね合わせ・観測演算子・ユニタリ発展とは無関係** です。  
**量子力学の量子状態の特殊実装でも、近似でもありません。** 比喩的ネーミングです。

### 4.3 AuditState との対照

| | 物理学の量子状態 | `QuantumState` (v1) | `AuditState` (v2) |
|--|------------------|---------------------|-------------------|
| 役割 | 物理予測 | デモ用の未定義マーカー | 監査付き未定義マーカー |
| 観測 | 演算子・確率 | `observe()` → ランダム文言 | なし（`resolve` 等は明示 API） |
| 同士の `==` | 状態ベクトルの同一性（物理条件付き） | **常に True**（【コードの事実】） | 被除数・除数・理由が一致で True |

---

## 5. v1 の「* 0 で元の値を返す」は物理学として正しいか

**結論（【調査者の整理】）: いいえ。数学・物理学の標準的意味では正しくありません。**

**【事実・数学】** \(a \div 0\) は実数では未定義。不定形の極限 \(\lim_{x\to 0} a/x\) は **\(+\infty\) や \(-\infty\)** になりうるが、**\(a\) そのものにはならない**（\(a \neq 0\) のとき）。

**【事実・数学】** \(q \times 0 = 0\) が常に成り立つので、未定義だった「商」\(q\) に 0 を掛けて **元の被除数 \(a\) だけを取り出す** 操作は、通常の数体系と矛盾します（\(0 \times \infty\) 型の曖昧さとも別問題）。

**【コードの事実】** `other == 0` 判定のため `False`、`0.0`、`0+0j` でも同じ経路になる（pytest 記録済み）。

**【比喩・設計意図】** 「情報パラドックスで情報が残る」という **物語上のギミック** として理解するのが妥当です。**物理学の定理の実装ではありません。**

---

## 6. QuantumZero は量子論とどこまで関係があるか — 総括

### 6.1 関係がある部分（比喩・動機づけレベル）

**【比喩・設計意図】**

- ブラックホール・ビッグバン・自己エネルギー **という物語** は、物理学のキーワードを借りた **ナラティブ（語り）**
- 「止まらないプログラム」「情報が残る」は、情報パラドックス議論への **連想**
- v2 の監査ログは、「測定・記録してから処理する」という **科学的誠実さのメタファ**（本物の実験手順ではない）

### 6.2 関係がない部分（厳密な意味）

**【調査者の整理】**

- 量子状態・ユニタリ性・繰り込み・ページ曲線の **いずれもコード内で再現していない**
- 数式の極限・発散・正則化の **計算機構はない**
- `QuantumState` / `AuditState` は **量子論のデータ型ではない**

### 6.3 最終回答: 比喩として使えるか、全く別物か

| 質問 | 答え |
|------|------|
| **Zenn・勉強会用の比喩として使えるか？** | **はい** — 「0 除算をどう設計するか」「監査可能なエラー状態」を、物理の話と **並べて** 紹介するのは有効。ただし **「物理学がこう言っているわけではない」** と毎回明記すべき。 |
| **量子論の一部・モデルか？** | **いいえ** — **全く別物**（プログラミング上の状態オブジェクト）。 |
| **v2 は QFT の正則化の簡易版か？** | **いいえ** — **運用上の類似**（記録してから扱う）止まり。数学的手続きではない。 |
| **v1 の情報復元は BH 情報問題の解か？** | **いいえ** — **意図的な比喩**。`* 0` は数学的にも物理的にも正当化されない。 |

---

## 7. 参考文献・公式資料・論文リンク

### 数学（ゼロ除算・極限）

| 資料 | URL |
|------|-----|
| Wikipedia: Division by zero | https://en.wikipedia.org/wiki/Division_by_zero |
| Wolfram MathWorld: Division by Zero | https://mathworld.wolfram.com/DivisionbyZero.html |
| OpenStax Calculus Vol.1 §4.8（L'Hôpital、不定形） | https://openstax.org/books/calculus-volume-1/pages/4-8-lhopitals-rule |
| Python 言語仕様（算術エラー） | https://docs.python.org/3/reference/expressions.html |

### 量子力学・量子状態（入門）

| 資料 | URL |
|------|-----|
| Stanford Encyclopedia of Philosophy: Quantum Mechanics | https://plato.stanford.edu/entries/qm/ |

### 量子場理論（発散・繰り込み）

| 資料 | URL |
|------|-----|
| CERN: An introduction to quantum field theory (1996-004) | https://doi.org/10.5170/cern-1996-004.1 |
| arXiv: Introductory Lectures on QFT | https://arxiv.org/pdf/hep-th/0510040 |
| Encyclopedia of Mathematics: Renormalization | https://encyclopediaofmath.org/wiki/Renormalization |
| CERN Courier: Renormalization group の歴史 | https://cern-courier.web.cern.ch/a/fifty-years-of-the-renormalization-group/ |

### ブラックホール・情報問題

| 資料 | URL |
|------|-----|
| Hawking 1975（粒子生成） | https://doi.org/10.1007/BF02345020 |
| Hawking 1976（予測可能性） | https://journals.aps.org/prd/abstract/10.1103/PhysRevD.14.2460 |
| blackhole.org: 年表・一次文献整理 | https://blackhole.org/reference/history/black-hole-thermodynamics-information/ |
| Hawking: Information Loss in Black Holes (2005 講演録) | https://arxiv.org/pdf/hep-th/0507171 |
| Page 曲線・ユニタリ性（近年） | https://arxiv.org/html/2601.11363 |
| 島・解釈論争の一例 | https://arxiv.org/html/2602.06543 |
| Nature Reviews Physics レビュー | https://www.nature.com/articles/s42254-026-00942-9 |

### QuantumZero コード（一次資料）

| 資料 | パス |
|------|------|
| v1 実装 | `../quantum_zero.py` |
| v2 実装 | `../quantum_zero_v2.py` |
| v1 仕様ロックテスト | `../tests/test_*.py` |
| v2 テスト | `../tests/test_quantum_zero_v2.py` |

---

## 8. 今後の調査メモ（未着手）

- v1 の `safe_divide` と **IEEE 754** 浮動小数点の除算の関係（別ファイル化推奨）
- ホーキング放射の **厳密定義** とコードデモの対応表
- 教科書レベル（例: Peskin & Schroeder）との章立て対照 — **書籍は購入本を参照すること**

---

*初版は上記 URL の公開情報とリポジトリ内コードに基づく。物理学の最終答えは専門論文の更新に依存する。*