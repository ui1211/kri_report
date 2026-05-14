# ThingSpeak取得設計A4要約

## 要約
ThingSpeak REST APIは、センサーの最新値、履歴、最終更新経過秒数をHTTP GETで取得できる。BigQuery upsert前提では `channel_id + entry_id` をキーにし、過去分は期間分割、現在以降は `results<=100` または最新値APIで差分取得する設計が妥当である。

## 現状
公式仕様では、全フィールド取得、単一フィールド取得、最新エントリ取得、最終更新からの秒数取得が用意されている。feed取得の `results` は最大8000件で、private channelにはRead API Keyが必要である。JSON/XMLで100件を超えるfeedは5分キャッシュされる。

## 課題
一括取得では8000件上限により高頻度センサーの期間窓で取りこぼしが起き得る。定期取得ではキャッシュ、ネットワーク失敗、429 Too Many Requests、一時停止後の欠測補完を考慮する必要がある。商用利用や無料枠制限も別途確認が必要である。

## 解決
Pythonラッパーを `src/thingspeak_client.py` に実装し、HTTPS固定、APIキーのログマスク、429/5xxリトライ、`last_data_age` による生存確認、時間窓分割の過去取得、`entry_id` 差分による定期取得を提供した。進捗表示には`tqdm`、ログには`loguru`を使う。

## 価値
最大8000件制限と100件超キャッシュを前提に取得経路を分けることで、過去データ補完と現在データ監視を同じupsertパイプラインに接続しやすくなる。BigQuery側では `channel_id + entry_id` の冪等投入により、再取得による重複を吸収できる。
