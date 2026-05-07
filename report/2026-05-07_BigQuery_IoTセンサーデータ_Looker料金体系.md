# レポート

## 1. メタ情報
- 作成日時: 2026-05-07
- 入力要約: IoT センサーデータを BigQuery に集約し、Looker で可視化する用途について、基本から発展的な設計、特にインサート・取り込み料金体系を調査する。
- トピック数: 7

## 2. 概要
- BigQuery はサーバーレス分析基盤で、料金は主に「クエリ処理」「ストレージ」「データ取り込み」「BI Engine / Storage API 等の追加機能」に分かれる。公式料金では、オンデマンドクエリは月 1 TiB まで無料、その後 $6.25/TiB、ストレージは最初の 10 GiB が無料で、アクティブ論理ストレージは例として 1 TiB/月 $23.552 とされている。
- IoT センサーデータを継続投入する場合、低頻度・遅延許容なら Cloud Storage 経由のバッチロードが取り込み無料、リアルタイム表示なら BigQuery Storage Write API または Pub/Sub BigQuery subscription が候補になる。
- `tabledata.insertAll` は $0.01/200 MiB で、成功挿入行が課金対象かつ 1 行あたり 1 KB 最小計算。Storage Write API は月 2 TiB まで無料、その後 $0.025/GiB で、公式ドキュメント上も旧 streaming API より低コストとされている。
- Looker ダッシュボード用途では、時刻列パーティション、デバイス ID・拠点・センサー種別でのクラスタリング、集計テーブルまたはマテリアライズドビュー、BI Engine の併用がコストと応答速度の鍵になる。

## 3. 現状
- BigQuery は [サーバーレスのデータ分析プラットフォーム](https://cloud.google.com/bigquery/pricing?hl=en_US)で、個別インスタンス管理なしにクエリ処理・ストレージ・ストリーミング書き込みを利用できる。
- IoT センサーデータは、時系列で継続的に増え、Looker では「最新状態」「時系列推移」「拠点・設備・デバイス別の異常傾向」を頻繁に見るため、書き込み頻度とクエリ頻度の両方がコスト要因になる。
- Looker は BigQuery に接続でき、LookML によるセマンティックモデルで BigQuery 上のデータをダッシュボードや探索に利用できる。[Looker と BigQuery の連携](https://cloud.google.com/bigquery/docs/looker)では、BigQuery データセットを Looker から分析する構成が示されている。
- BigQuery のオンデマンドクエリは、選択した列の読み取り量に応じて課金される。公式料金ページでは、最初の 1 TiB/月が無料、その後 $6.25/TiB とされている。
- パーティションテーブルでは、フィルタ条件に合うパーティションだけを読む partition pruning により、読み取り量とクエリ費用を削減できる。[公式ドキュメント](https://cloud.google.com/bigquery/docs/partitioned-tables)は、パーティション化によりクエリ性能改善とコスト制御が可能と説明している。

## 4. 課題
- C1: IoT センサーデータをリアルタイム投入すると、取り込み方式ごとに料金・遅延・重複制御・実装難度が大きく変わる。
- C2: Looker ダッシュボードが生データを広くスキャンすると、オンデマンドクエリ費用と応答時間が増えやすい。
- C3: 長期保存するセンサーデータは増加し続けるため、保存期間、パーティション失効、長期ストレージ、集計保持を設計しないと継続費用が読みにくい。

## 5. AI解決
- C1対応
  - OSS: Apache Beam / Dataflow テンプレートや SDK を使うと、Pub/Sub から BigQuery への変換・バリデーション・重複排除を実装しやすい。ただし Dataflow 自体の実行料金は別途発生する。
  - 研究: ストリーム処理では exactly-once / at-least-once の選択が重要。BigQuery Storage Write API は [stream offset による exactly-once](https://cloud.google.com/bigquery/docs/write-api)をサポートする。
  - 実運用: 変換不要なら [Pub/Sub BigQuery subscription](https://cloud.google.com/pubsub/docs/bigquery)で直接 BigQuery に書き込み、変換や異常値補正が必要なら Dataflow 経由を使う。
- C2対応
  - OSS: dbt や Dataform で日次・時次・分次の集計テーブルを管理し、Looker は集計済みテーブルを見る構成にする。
  - 研究: BigQuery の [マテリアライズドビュー](https://cloud.google.com/bigquery/docs/materialized-views-intro)はクエリ結果を事前計算し、変更分を増分更新できるため、繰り返し集計の処理量削減に使える。
  - 実運用: Looker Explores は時刻フィルタ必須、必要列のみ参照、日次・時次集計、BI Engine、パーティション・クラスタリングを組み合わせる。
- C3対応
  - OSS: dbt / Dataform で raw、clean、mart の階層を分け、古い raw を Cloud Storage または低頻度参照領域へ退避する。
  - 研究: BigQuery は 90 日変更されていないテーブルまたはパーティションを長期ストレージ料金に自動移行し、価格が約 50% 下がると説明している。
  - 実運用: センサー raw は日次または時次パーティション、保持期間を partition expiration で制御し、Looker 用には集計粒度を落としたテーブルを長期保持する。

## 6. 価値
- C1由来: Storage Write API は月 2 TiB まで無料、その後 $0.025/GiB。旧 `tabledata.insertAll` の $0.01/200 MiB より、継続ストリーミングでは料金面で有利になりやすい。
- C2由来: オンデマンドクエリは $6.25/TiB のため、Looker の 1 回のダッシュボード表示で 1 TiB を読む設計より、時刻パーティションと集計テーブルで 10 GiB だけ読む設計の方が、単純計算で処理量を約 99% 減らせる。
- C3由来: 公式例ではアクティブ論理ストレージ 1 TiB/月は $23.552。90 日以上未変更の長期ストレージは約 50% 低下するため、過去データを追記・更新しないパーティション設計にすると保存費を抑えやすい。

## 7. トピック一覧

### BigQuery 料金体系の基本
- 概要: BigQuery の料金は [Compute pricing、Storage pricing、streaming reads/writes など](https://cloud.google.com/bigquery/pricing?hl=en_US)に分かれる。
- 特徴:
  - オンデマンドクエリ: 月 1 TiB まで無料、その後 $6.25/TiB。
  - 容量課金: slot-hour ベース。Standard / Enterprise / Enterprise Plus の Edition がある。
  - ストレージ: active / long-term、logical / physical のモデルがある。
- 主なスペック or 数値:
  - On-demand query: $6.25/TiB
  - Standard Edition slot: $0.04/slot-hour
  - Enterprise Edition slot: $0.06/slot-hour
  - Enterprise Plus slot: $0.10/slot-hour
- 制約 or 注意点:
  - 容量課金はストレージ費用、BI Engine、ストリーミング挿入、Storage API には適用されない。

### データ取り込み料金
- 概要: BigQuery は [バッチロードとストリーミング](https://cloud.google.com/bigquery/pricing?hl=en_US)の 2 方式を提供する。
- 特徴:
  - バッチロード: 共有 slot pool 利用なら無料。ロード後は BigQuery ストレージ課金。
  - `tabledata.insertAll`: $0.01/200 MiB。
  - Storage Write API: 月 2 TiB まで無料、その後 $0.025/GiB。
- 主なスペック or 数値:
  - `insertAll`: 成功挿入行が課金対象、1 行 1 KB 最小サイズで計算。
  - Storage Write API: first 2 TiB/month free。
- 制約 or 注意点:
  - Cloud Storage からロードする場合、Cloud Storage 側の保存費は別途発生する。
  - クロスリージョンロードはネットワーク転送料が発生しうる。

### SQL INSERT / DML の料金
- 概要: BigQuery の DML は [処理バイト数に基づいて課金](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax)される。
- 特徴:
  - `INSERT` は DML 文自体が処理するバイト数 q または q' が課金対象。
  - `UPDATE`、`DELETE`、更新を含む `MERGE` は対象テーブルまたは対象パーティションのサイズも関係する。
- 主なスペック or 数値:
  - 非パーティション表の `INSERT`: q
  - 非パーティション表の `UPDATE` / `DELETE`: q + t
  - パーティション表の `UPDATE` / `DELETE`: q' + t'
- 制約 or 注意点:
  - IoT の大量逐次投入に SQL `INSERT VALUES` を多用する設計は、運用・スループット・コストの面で Storage Write API やバッチロードより不利になりやすい。

### BigQuery Storage Write API
- 概要: [Storage Write API](https://cloud.google.com/bigquery/docs/write-api) はストリーミング取り込みとバッチ取り込みを統合した高性能 API。
- 特徴:
  - default stream は at-least-once。
  - committed stream と offset 管理で exactly-once を実現可能。
  - gRPC、Protocol Buffers、Apache Arrow に対応。
- 主なスペック or 数値:
  - 月 2 TiB まで無料、その後 $0.025/GiB。
- 制約 or 注意点:
  - exactly-once は offset 管理が必要で、実装複雑度が上がる。
  - 1 行ずつ送るより、公式ドキュメント上も複数行をまとめた append が推奨される。

### Pub/Sub BigQuery Subscription
- 概要: [Pub/Sub BigQuery subscription](https://cloud.google.com/pubsub/docs/bigquery) は、個別 subscriber を実装せず Pub/Sub メッセージを BigQuery テーブルへ直接書き込む方式。
- 特徴:
  - 変換不要なメッセージなら Dataflow ジョブなしで BigQuery へ格納できる。
  - BigQuery Storage Write API を使って書き込む。
  - 書き込み失敗時は dead-letter topic を設定できる。
- 主なスペック or 数値:
  - [Pub/Sub pricing](https://cloud.google.com/pubsub/pricing)では、BigQuery subscription throughput は $50/TiB。
  - この方式では追加の BigQuery data ingestion charges はないと説明されている。
- 制約 or 注意点:
  - 変換、欠損補完、複雑な重複排除が必要な場合は Dataflow が推奨される。

### パーティション・クラスタリング
- 概要: BigQuery の [パーティションテーブル](https://cloud.google.com/bigquery/docs/partitioned-tables)と [クラスタリング](https://cloud.google.com/bigquery/docs/clustered-tables)は、IoT 時系列データのクエリ費用削減に重要。
- 特徴:
  - `event_timestamp` で日次または時次パーティション。
  - `device_id`、`site_id`、`sensor_type` などでクラスタリング。
  - パーティションフィルタにより不要パーティションをスキャン対象から外せる。
- 主なスペック or 数値:
  - TIMESTAMP / DATETIME は hourly、daily、monthly、yearly partitioning が可能。
  - クラスタリングは指定列に基づく block pruning で読み取りブロックを減らす。
- 制約 or 注意点:
  - Looker 側で時刻フィルタなしの全期間集計を許すと、パーティション設計の効果が出にくい。

### Looker 表示・発展設計
- 概要: Looker は [BigQuery Standard SQL に接続](https://cloud.google.com/looker/docs/db-config-google-bigquery)し、LookML で一貫した指標定義を提供できる。
- 特徴:
  - raw テーブルではなく、clean / mart / aggregate テーブルを Looker の主要 Explore にする。
  - 最新値テーブル、時系列集計テーブル、異常検知結果テーブルを分ける。
  - BI Engine やマテリアライズドビューを繰り返し参照されるダッシュボードに使う。
- 主なスペック or 数値:
  - マテリアライズドビューは変更分をバックグラウンドで増分反映し、クエリ処理時間と料金削減に役立つ。
- 制約 or 注意点:
  - Looker の利用者数、ダッシュボード自動更新間隔、Explore の自由度が BigQuery クエリ費用に直結する。

## 8. 比較まとめ
- 比較表:

| 対象 | 概要 | 精度 | コスト | 導入難易度 | 拡張性 | 主な数値 | 根拠 |
|---|---|---|---|---|---|---|---|
| バッチロード | Cloud Storage 等からまとめて BigQuery にロード | 高 | 取り込み無料、保存費別 | 低 | 中 | 共有 slot pool は無料 | [BigQuery pricing](https://cloud.google.com/bigquery/pricing?hl=en_US) |
| `tabledata.insertAll` | 旧ストリーミング API | at-least-once 相当、重複対策要 | $0.01/200 MiB | 中 | 中 | 1 行 1 KB 最小計算 | [BigQuery pricing](https://cloud.google.com/bigquery/pricing?hl=en_US) |
| Storage Write API | 推奨度の高いリアルタイム書き込み API | offset 管理で exactly-once 可 | 月 2 TiB 無料、その後 $0.025/GiB | 中〜高 | 高 | first 2 TiB/month free | [Storage Write API](https://cloud.google.com/bigquery/docs/write-api) |
| Pub/Sub BigQuery subscription | Pub/Sub から BigQuery へ直接書き込み | Pub/Sub / BigQuery subscription 依存 | $50/TiB、追加 BigQuery ingestion charge なし | 低〜中 | 中 | BigQuery subscription throughput $50/TiB | [Pub/Sub pricing](https://cloud.google.com/pubsub/pricing) |
| Dataflow + BigQuery | 変換・重複排除・補正を挟む本格パイプライン | 実装次第で高 | Dataflow 実行費 + BigQuery 費 | 高 | 高 | 該当なし | [Pub/Sub BigQuery subscription](https://cloud.google.com/pubsub/docs/bigquery) |
| SQL DML INSERT | SQL でテーブルに行追加 | 高 | 処理バイト課金 | 低 | 低〜中 | INSERT は q / q' | [DML syntax](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax) |
| Looker + 集計テーブル | Looker が集計済み BigQuery テーブルを参照 | 高 | クエリ量を抑制可能 | 中 | 高 | オンデマンド $6.25/TiB | [Looker and BigQuery](https://cloud.google.com/bigquery/docs/looker) |

- 違い:
  - 遅延許容ならバッチロードが最安になりやすい。
  - リアルタイム性が必要なら Storage Write API または Pub/Sub BigQuery subscription。
  - データ変換や品質チェックが必要なら Dataflow を挟む。
- 使いどころ:
  - 数分〜数十分遅延でよい集計: Cloud Storage → BigQuery load job。
  - ほぼリアルタイムのダッシュボード: Pub/Sub → BigQuery subscription、または Storage Write API。
  - 異常値補正・重複排除・スキーマ変換あり: Pub/Sub → Dataflow → BigQuery。
- 強み / 弱み:
  - BigQuery は大量時系列データの分析と Looker 可視化に強い一方、無制限の生データスキャンや高頻度ダッシュボード更新を許すとクエリ費用が膨らむ。

## 9. 更新履歴
- 2026-05-07: 初版

## 10. 参考リンク一覧
- [BigQuery pricing](https://cloud.google.com/bigquery/pricing?hl=en_US)
- [BigQuery overview](https://docs.cloud.google.com/bigquery/docs/introduction)
- [Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [Stream data using the Storage Write API](https://cloud.google.com/bigquery/docs/write-api-streaming)
- [Pub/Sub BigQuery subscription](https://cloud.google.com/pubsub/docs/bigquery)
- [Pub/Sub pricing](https://cloud.google.com/pubsub/pricing)
- [DML syntax](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax)
- [Partitioned tables](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [Clustered tables](https://cloud.google.com/bigquery/docs/clustered-tables)
- [Materialized views](https://cloud.google.com/bigquery/docs/materialized-views-intro)
- [Looker and BigQuery](https://cloud.google.com/bigquery/docs/looker)
- [Looker BigQuery connection](https://cloud.google.com/looker/docs/db-config-google-bigquery)
