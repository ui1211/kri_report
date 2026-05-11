# レポート

## 1. メタ情報
- 作成日時: 2026-05-07
- 入力要約: IoT センサーデータを BigQuery に集約し、Looker で可視化する用途について、BigQuery と Looker の料金体系、費用発生点、概算方法、コスト抑制設計を深掘りする。
- トピック数: 10

## 2. 概要
- BigQuery の料金は [クエリ処理、ストレージ、取り込み、抽出、BI Engine など](https://cloud.google.com/bigquery/pricing?hl=en_US)に分かれる。オンデマンドクエリは月 1 TiB まで無料、その後 $6.25/TiB、容量課金は Standard $0.04/slot-hour、Enterprise $0.06/slot-hour、Enterprise Plus $0.10/slot-hour が基本になる。
- IoT センサーデータの取り込みでは、バッチロードは共有 slot pool 利用なら無料、`tabledata.insertAll` は $0.01/200 MiB、Storage Write API は月 2 TiB まで無料で超過分 $0.025/GiB、Pub/Sub BigQuery subscription は Pub/Sub 側で $50/TiB が目安になる。
- Looker の料金は [プラットフォーム料金とユーザー料金](https://cloud.google.com/looker/pricing)の 2 要素で、Standard / Enterprise / Embed とも公開ページ上は `Call sales` で個別見積もりである。一方、BigQuery に対して Looker が発行する SQL は BigQuery 側のクエリ費用、PDT/集計テーブルの保存費、BI Engine 費用に波及する。
- Looker + BigQuery 構成では、Looker 本体費用よりも、ダッシュボードの自動更新、Explore の自由度、時刻フィルタの有無、PDT / aggregate awareness / BI Engine の設計が BigQuery 側の継続費用を左右する。

## 3. 現状
- BigQuery はサーバーレス分析基盤で、クエリは選択列の読み取り量に基づいて課金される。公式料金では、オンデマンドは最初の 1 TiB/月が無料で、その後 $6.25/TiB である。
- 容量課金は slot-hour ベースで、BigQuery editions の Standard / Enterprise / Enterprise Plus を使う。公式料金では、各 edition の従量 slot 単価は Standard $0.04、Enterprise $0.06、Enterprise Plus $0.10 / slot-hour で、秒単位課金かつ 1 分最小とされている。
- IoT センサーデータは継続的に増加し、Looker では最新値、時系列推移、設備別・拠点別・センサー種別の傾向を繰り返し見るため、取り込み費用、保存費用、ダッシュボード更新時のクエリ費用が同時に発生する。
- Looker は [BigQuery Standard SQL に接続](https://cloud.google.com/looker/docs/db-config-google-bigquery)でき、サービスアカウントまたは OAuth などで BigQuery に認証する。PDT を使う場合は BigQuery 側に一時データセットを作成する必要がある。
- Looker の公開料金ページでは、Looker (Google Cloud core) はプラットフォーム料金とユーザー料金で構成され、Standard / Enterprise / Embed はいずれも年間契約の `Call sales` とされる。Standard は 50 ユーザー未満の小規模組織向けで、10 Standard Users、2 Developer Users、月 1,000 query-based API calls と月 1,000 administrative API calls が含まれる。
- Looker の Enterprise は内部 BI 向けで、10 Standard Users、2 Developer Users、月 100,000 query-based API calls と月 10,000 administrative API calls が含まれる。Embed は外部分析や組み込み用途向けで、月 500,000 query-based API calls と月 100,000 administrative API calls が含まれる。

## 4. 課題
- C1: IoT データの取り込み方式によって、BigQuery 取り込み料金、Pub/Sub 料金、Dataflow 料金、遅延、重複制御、実装難度が大きく変わる。
- C2: Looker のダッシュボードや Explore が生データを広くスキャンし、PDT・集計テーブル・長期保存パーティションも無計画に増えると、BigQuery のクエリ費用、保存費用、応答時間が増えやすい。
- C3: Looker 本体は個別見積もりのため、ユーザー種別、API 利用、Embed 利用、Conversational Analytics の将来課金まで含めないと総額を見積もりにくい。

## 5. AI解決
- C1対応
  - OSS: Apache Beam / Dataflow SDK を使うと、Pub/Sub から BigQuery への変換、バリデーション、重複排除、異常値補正を実装しやすい。ただし Dataflow 実行料金は別途発生する。
  - 研究: ストリーム処理では exactly-once / at-least-once の選択が重要で、BigQuery Storage Write API は [stream offset による exactly-once](https://cloud.google.com/bigquery/docs/write-api)をサポートする。
  - 実運用: 変換不要なら [Pub/Sub BigQuery subscription](https://cloud.google.com/pubsub/docs/bigquery)で直接 BigQuery に書き込み、複雑な変換や補正が必要なら Dataflow 経由にする。
- C2対応
  - OSS: dbt や Dataform で raw、clean、mart、aggregate の階層を管理し、Looker は raw ではなく mart / aggregate を主要 Explore にする。
  - 研究: Looker の [aggregate awareness](https://cloud.google.com/looker/docs/aggregate_awareness)は、クエリを満たせる最小の集計テーブルを選び、巨大テーブルへのクエリを減らせる。公式ドキュメントは、戦略的に実装すると平均クエリを桁違いに高速化できると説明している。
  - 実運用: Looker Explores では時刻フィルタを必須化し、必要列のみ参照し、日次・時次集計、PDT、BigQuery マテリアライズドビュー、BI Engine、パーティション・クラスタリングを組み合わせる。センサー raw は時刻パーティション、保持期間は partition expiration で制御し、Looker 用には必要粒度に集計したテーブルを長期保持する。
- C3対応
  - OSS: 該当なし。Looker ライセンスは商用サービスの契約条件に依存する。
  - 研究: Looker 料金ページでは、Developer / Standard / Viewer の 3 種類のユーザーライセンスが定義され、権限範囲が異なる。Conversational Analytics は 2026-09-30 までフェアユース範囲で無制限、2026-10-01 以降は月次割当超過分が Input $3.00/1M tokens、Output $20.00/1M tokens とされている。
  - 実運用: 見積もり時は Standard / Enterprise / Embed の edition、Developer / Standard / Viewer の人数、API 呼び出し上限、Embed の外部ユーザー規模、Conversational Analytics の利用有無を分けて整理する。

## 6. 価値
- C1由来: Storage Write API は月 2 TiB まで無料で、超過分は $0.025/GiB。旧 `tabledata.insertAll` の $0.01/200 MiB と比べ、継続ストリーミングでは BigQuery 取り込み単価を抑えやすい。
- C2由来: オンデマンドクエリは $6.25/TiB のため、Looker の 1 回のダッシュボード表示で 1 TiB を読む設計より、時刻パーティションと集計テーブルで 10 GiB だけ読む設計の方が、単純計算で処理量を約 99% 減らせる。さらに、90 日以上未変更のテーブルまたはパーティションは長期ストレージに自動移行するため、過去データを更新しない設計は保存費抑制にも効く。
- C3由来: Looker Standard / Enterprise / Embed は公開定価ではなく `Call sales` だが、各 platform には 10 Standard Users と 2 Developer Users が含まれる。追加ユーザー、API 上限超過、Conversational Analytics 超過課金を分けることで、見積もり漏れを減らせる。

## 7. トピック一覧

### BigQuery オンデマンドクエリ料金
- 概要: BigQuery の [オンデマンド料金](https://cloud.google.com/bigquery/pricing?hl=en_US)は、クエリが処理したデータ量に応じて課金される。
- 特徴:
  - 最初の 1 TiB/月は無料で、その後 $6.25/TiB。
  - 選択した列のデータ量に基づくため、`SELECT *` は費用増加要因になる。
  - `LIMIT` を付けても、読み取る列の処理データ量は減らない。
- 主なスペック or 数値:
  - 無料枠: 1 TiB/月/account
  - 超過単価: $6.25/TiB
  - 最小課金: クエリあたり 10 MB、参照テーブルあたり 10 MB
- 制約 or 注意点:
  - Looker のタイル数、更新頻度、Explore の自由検索が BigQuery クエリ回数と処理量を増やす。

### BigQuery 容量課金・Editions
- 概要: BigQuery は [slot-hour ベースの容量課金](https://cloud.google.com/bigquery/pricing?hl=en_US)も提供する。
- 特徴:
  - Standard / Enterprise / Enterprise Plus の 3 edition がある。
  - BigQuery ML、DML、DDL などのクエリ処理に適用される。
  - ストレージ、BI Engine、ストリーミング挿入、BigQuery Storage API には適用されない。
- 主なスペック or 数値:
  - Standard: $0.04/slot-hour
  - Enterprise: $0.06/slot-hour
  - Enterprise Plus: $0.10/slot-hour
  - 秒単位課金、1 分最小
- 制約 or 注意点:
  - Looker のクエリが多く、オンデマンド費用が読みにくい場合は、予約や autoscaler による予算安定化を検討する。

### BigQuery ストレージ料金
- 概要: BigQuery の [ストレージ料金](https://cloud.google.com/bigquery/pricing?hl=en_US)は、論理ストレージまたは物理ストレージ、アクティブまたは長期ストレージで考える。
- 特徴:
  - BigQuery にロードされたデータはストレージ課金対象になる。
  - 90 日変更されないテーブルまたはパーティションは長期ストレージ料金に自動移行する。
  - Cloud Storage からロードする場合、BigQuery 側とは別に Cloud Storage 側の保存費が発生する。
- 主なスペック or 数値:
  - 最初の 10 GiB は無料枠の対象。
  - 既存レポート作成時点の公式例では、アクティブ論理ストレージ 1 TiB/月は $23.552。
- 制約 or 注意点:
  - PDT、aggregate table、マテリアライズドビューは BigQuery 上に実体またはキャッシュ相当のデータを持つため、クエリ削減と保存費のバランスを見る。

### BigQuery データ取り込み料金
- 概要: BigQuery は [バッチロードとストリーミング書き込み](https://cloud.google.com/bigquery/pricing?hl=en_US)で料金が異なる。
- 特徴:
  - バッチロードは default-pipeline の共有 slot pool 利用なら無料。
  - `tabledata.insertAll` は成功挿入行が課金対象。
  - Storage Write API は高性能な推奨 API として扱いやすい。
- 主なスペック or 数値:
  - Batch Loading: 共有 slot pool 利用なら無料
  - `tabledata.insertAll`: $0.01/200 MiB、1 行 1 KB 最小サイズ
  - Storage Write API: 月 2 TiB まで無料、その後 $0.025/GiB
- 制約 or 注意点:
  - ロード後の BigQuery ストレージ費、Cloud Storage 保存費、クロスリージョン転送料は別に見る。

### Pub/Sub BigQuery Subscription
- 概要: [Pub/Sub BigQuery subscription](https://cloud.google.com/pubsub/docs/bigquery)は、個別 subscriber を実装せず Pub/Sub メッセージを BigQuery テーブルへ直接書き込む方式。
- 特徴:
  - BigQuery Storage Write API を使って書き込む。
  - 変換不要なメッセージであれば Dataflow ジョブなしで BigQuery に格納できる。
  - 書き込み失敗時は dead-letter topic を設定できる。
- 主なスペック or 数値:
  - [Pub/Sub pricing](https://cloud.google.com/pubsub/pricing)では BigQuery subscription throughput は $50/TiB。
  - この方式では追加の BigQuery data ingestion charges はないと説明されている。
- 制約 or 注意点:
  - スキーマ変換、欠損補完、複雑な重複排除が必要な場合は Dataflow 経由が向く。

### BI Engine 料金
- 概要: [BI Engine](https://cloud.google.com/bigquery/pricing?hl=en_US)は BigQuery データをメモリにキャッシュして SQL クエリを高速化する。
- 特徴:
  - オンデマンド料金では、BI Engine が加速したステージは 0 scanned bytes として扱われる。
  - editions 料金では、最初のステージは BigQuery reservation slot を消費しない。
  - BigQuery editions commitments 利用時は、購入 slot 数に応じた追加 BI Engine 容量が無償枠として提供される。
- 主なスペック or 数値:
  - BI Engine memory capacity: $0.0416/GiB-hour
  - editions commitment bundle: 100 slots で 5 GiB、500 slots で 25 GiB、1,000 slots で 50 GiB、2,000 slots で最大 100 GiB
- 制約 or 注意点:
  - Looker ダッシュボードの高速化には有効だが、予約メモリ容量そのものの費用が発生する。

### Looker プラットフォーム料金
- 概要: Looker (Google Cloud core) の [料金](https://cloud.google.com/looker/pricing)はプラットフォーム料金とユーザー料金で構成される。
- 特徴:
  - Standard / Enterprise / Embed の 3 edition がある。
  - いずれも公開ページ上の費用は Annual commitment / Call sales。
  - 各 platform には 10 Standard Users と 2 Developer Users が含まれる。
- 主なスペック or 数値:
  - Standard: 50 ユーザー未満の小規模組織向け、月 1,000 query-based API calls、月 1,000 administrative API calls
  - Enterprise: 月 100,000 query-based API calls、月 10,000 administrative API calls
  - Embed: 月 500,000 query-based API calls、月 100,000 administrative API calls
- 制約 or 注意点:
  - 公開定価では総額を算出できないため、ユーザー数、edition、契約年数、API 利用、Embed 利用を前提条件として見積もる。

### Looker ユーザー・Conversational Analytics 料金
- 概要: Looker の [ユーザーライセンス](https://cloud.google.com/looker/pricing)は Developer User、Standard User、Viewer User の 3 種類で、権限範囲が異なる。
- 特徴:
  - Developer は開発モード、LookML、管理、SQL Runner、API、Support など広い権限を持つ。
  - Standard は Explore、SQL Runner、Scheduling、Dashboard / Look 作成が可能だが、開発モードや管理権限は含まれない。
  - Viewer はフォルダ、ボード、ダッシュボード、Looks の閲覧中心で、Explore や SQL Runner は含まれない。
- 主なスペック or 数値:
  - Conversational Analytics 月次割当: Viewer input 1M / output 20K、Standard input 2M / output 40K、Developer input 4M / output 80K data tokens
  - 2026-09-30 までフェアユース範囲で無制限
  - 2026-10-01 以降の超過単価: Input $3.00/1M tokens、Output $20.00/1M tokens
- 制約 or 注意点:
  - 生成 AI 機能を使う場合、2026-10-01 以降の超過課金を見積もりに入れる必要がある。

### Looker キャッシュ・PDT・Aggregate Awareness
- 概要: Looker は [クエリキャッシュ](https://cloud.google.com/looker/docs/caching-and-datagroups)、PDT、aggregate awareness により BigQuery へのクエリを減らせる。
- 特徴:
  - Looker は同一 SQL クエリの結果がキャッシュにあり、キャッシュポリシー上有効ならキャッシュ結果を使う。
  - デフォルトのキャッシュ保持は 1 時間。
  - aggregate awareness は、クエリを満たせる最小の集計テーブルを動的に選ぶ。
- 主なスペック or 数値:
  - キャッシュは customer data を最大 30 日、またはキャッシュ保存上限に達するまで保持する。
  - キャッシュを最小化しても、結果は最大 10 分保存される場合がある。
- 制約 or 注意点:
  - BigQuery OAuth の per-user connection override では、同じユーザーが同じクエリを実行した場合に限りキャッシュが使われるため、キャッシュ効果が下がる可能性がある。

### 概算モデルと設計判断
- 概要: IoT + BigQuery + Looker の費用は、[BigQuery 料金](https://cloud.google.com/bigquery/pricing?hl=en_US)と Looker 契約料金を分けて概算する。
- 特徴:
  - 月額概算は、取り込み量、保存量、Looker からのクエリ処理量、BI Engine 予約容量、Looker edition / ユーザー数に分解する。
  - BigQuery 側は公開単価で概算しやすいが、Looker 本体は `Call sales` のため見積もり前提を明文化する。
  - 低頻度・遅延許容ならバッチロード、リアルタイムなら Storage Write API または Pub/Sub BigQuery subscription、変換が多いなら Dataflow を選ぶ。
- 主なスペック or 数値:
  - 仮に 1,000 台のデバイスが 1 分ごとに 500 B のレコードを送る場合、月間 raw 量は約 21.6 GB、行数は約 4,320 万行になる。
  - 同条件では Storage Write API の 2 TiB/月無料枠内に収まりやすい一方、`insertAll` は 1 行 1 KB 最小計算の影響を受ける。
- 制約 or 注意点:
  - 上記は単純な仮定に基づく概算であり、実費はレコードサイズ、属性数、圧縮、重複、更新頻度、ダッシュボード更新間隔、リージョン、契約条件で変わる。

## 8. 比較まとめ
- 比較表:

| 対象 | 概要 | 精度 | コスト | 導入難易度 | 拡張性 | 主な数値 | 根拠 |
|---|---|---|---|---|---|---|---|
| BigQuery オンデマンド | 読み取り量に応じたクエリ課金 | 高 | 利用量変動 | 低 | 高 | 1 TiB/月無料、超過 $6.25/TiB | [BigQuery pricing](https://cloud.google.com/bigquery/pricing?hl=en_US) |
| BigQuery 容量課金 | slot-hour による予約・従量課金 | 高 | 予算安定化しやすい | 中 | 高 | Standard $0.04、Enterprise $0.06、Enterprise Plus $0.10/slot-hour | [BigQuery pricing](https://cloud.google.com/bigquery/pricing?hl=en_US) |
| バッチロード | Cloud Storage 等からまとめて BigQuery にロード | 高 | 取り込み無料、保存費別 | 低 | 中 | default-pipeline 共有 slot pool は無料 | [BigQuery pricing](https://cloud.google.com/bigquery/pricing?hl=en_US) |
| `tabledata.insertAll` | 旧ストリーミング API | at-least-once 相当、重複対策要 | 中 | 中 | 中 | $0.01/200 MiB、1 行 1 KB 最小計算 | [BigQuery pricing](https://cloud.google.com/bigquery/pricing?hl=en_US) |
| Storage Write API | 推奨度の高いリアルタイム書き込み API | offset 管理で exactly-once 可 | 低〜中 | 中〜高 | 高 | 2 TiB/月無料、超過 $0.025/GiB | [Storage Write API](https://cloud.google.com/bigquery/docs/write-api) |
| Pub/Sub BigQuery subscription | Pub/Sub から BigQuery へ直接書き込み | Pub/Sub / BigQuery subscription 依存 | 中 | 低〜中 | 中 | BigQuery subscription throughput $50/TiB、追加 BigQuery ingestion charge なし | [Pub/Sub pricing](https://cloud.google.com/pubsub/pricing) |
| BI Engine | Looker / BigQuery ダッシュボード高速化 | 高 | 予約容量課金 | 中 | 中 | $0.0416/GiB-hour | [BigQuery pricing](https://cloud.google.com/bigquery/pricing?hl=en_US) |
| Looker Standard | 小規模組織向け Looker platform | 高 | 個別見積もり | 中 | 中 | 50 ユーザー未満、10 Standard + 2 Developer、API 1,000/月 | [Looker pricing](https://cloud.google.com/looker/pricing) |
| Looker Enterprise | 内部 BI 向け Looker platform | 高 | 個別見積もり | 中 | 高 | query-based API 100,000/月、admin API 10,000/月 | [Looker pricing](https://cloud.google.com/looker/pricing) |
| Looker Embed | 外部分析・組み込み向け Looker platform | 高 | 個別見積もり | 高 | 高 | query-based API 500,000/月、admin API 100,000/月 | [Looker pricing](https://cloud.google.com/looker/pricing) |
| Looker aggregate awareness | 最小の集計テーブルを選んで BigQuery クエリを削減 | 高 | 保存費と引き換えにクエリ費削減 | 中 | 高 | 戦略的実装で平均クエリを桁違いに高速化可能 | [Aggregate awareness](https://cloud.google.com/looker/docs/aggregate_awareness) |

- 違い:
  - BigQuery は公開単価で概算しやすいが、Looker 本体は個別見積もりである。
  - 取り込みは、遅延許容ならバッチロード、リアルタイムなら Storage Write API、Pub/Sub 連携を簡略化したいなら BigQuery subscription が候補になる。
  - Looker 利用時の BigQuery 費用は、利用者数そのものよりも、ダッシュボード更新頻度、タイル数、Explore の自由度、キャッシュ設計、集計テーブル設計に強く依存する。
- 使いどころ:
  - 数分〜数十分遅延でよい集計: Cloud Storage -> BigQuery load job。
  - ほぼリアルタイムの監視: Pub/Sub -> BigQuery subscription、または Storage Write API。
  - 異常値補正・重複排除・スキーマ変換あり: Pub/Sub -> Dataflow -> BigQuery。
  - 経営・現場ダッシュボード: BigQuery mart / aggregate -> Looker、必要に応じて BI Engine。
- 強み / 弱み:
  - BigQuery + Looker は大量時系列データの分析と可視化に強い。一方、Looker 本体は個別見積もりで、BigQuery 側は無制限の生データスキャンや高頻度自動更新を許すと費用が膨らむ。

## 9. 更新履歴
- 2026-05-07: 初版
- 2026-05-11: BigQuery と Looker の料金体系、Looker edition、ユーザーライセンス、BI Engine、キャッシュ・PDT・aggregate awareness、概算モデルを追加。

## 10. 参考リンク一覧
- [BigQuery pricing](https://cloud.google.com/bigquery/pricing?hl=en_US)
- [Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [Pub/Sub BigQuery subscription](https://cloud.google.com/pubsub/docs/bigquery)
- [Pub/Sub pricing](https://cloud.google.com/pubsub/pricing)
- [Looker pricing](https://cloud.google.com/looker/pricing)
- [Looker BigQuery connection](https://cloud.google.com/looker/docs/db-config-google-bigquery)
- [Aggregate awareness](https://cloud.google.com/looker/docs/aggregate_awareness)
- [Looker caching and datagroups](https://cloud.google.com/looker/docs/caching-and-datagroups)
