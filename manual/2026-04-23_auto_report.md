# auto_report

# 構成図

<img src="_img/auto.drawio.png" width="1200">

# セットアップ手順

## 1. Node.js / npx のインストール

`cline` の MCP で `mcp-searxng` を起動するため、`node` と `npx` が使える状態にしておく。

1. Node.js の LTS 版をインストールする
2. PowerShell を再起動する
3. 以下でインストール確認を行う

例:

```powershell
winget install OpenJS.NodeJS.LTS
```

```powershell
node -v
npx -v
```

`node` と `npx` の両方でバージョンが表示されればよい。

## 2. SearXNG を Docker で起動

このリポジトリでは `docker/searxng/settings.yml` を利用する。

1. PowerShell で `docker/searxng` に移動する
2. 既存の `searxng` コンテナがあれば停止・削除する
3. `8080` 番ポートで起動する

```powershell
cd docker/searxng
$pwd = (Get-Location).Path
docker rm -f searxng 2>$null
docker run -d -p 8080:8080 -v "${pwd}/settings.yml:/etc/searxng/settings.yml" --name searxng --restart unless-stopped searxng/searxng
```

起動確認:

```powershell
docker ps
curl "http://localhost:8080/search?q=test&format=json"
```

`docker ps` に `searxng` が表示され、`curl` で JSON が返れば利用可能。

## 3. cline で MCP を設定

`cline` の MCP 設定では、`npx -y mcp-searxng` を使って SearXNG を stdio 接続する。

1. `cline` の MCP 設定画面を開く
2. `mcpServers` に `searxng` を追加する
3. `SEARXNG_URL` を `http://localhost:8080` に設定する
4. 設定保存後、`cline` を再読み込みする

設定例:

```json
{
  "mcpServers": {
    "searxng": {
      "autoApprove": [
        "searxng_web_search"
      ],
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "mcp-searxng"
      ],
      "env": {
        "SEARXNG_URL": "http://localhost:8080"
      }
    }
  }
}
```

設定内容は [cline_mcp_settings.json](</c:/Users/yutou/Desktop/work/kri/kri_report/manual/cline_mcp_settings.json>) をベースにしている。

## 4. 動作確認

1. `cline` から `searxng_web_search` を呼び出す
2. エラーが出ないことを確認する
3. 必要なら `http://localhost:8080` をブラウザで開き、SearXNG 自体が応答していることを確認する

# 使用例(調査レポートの作成)

> 調査における手順や具体指示はワークフローとスキルによって制御
> WorkFlows > research-report-kri
> Skills > report-format-kri, report-fact-check

1. レポート作成指示
2. レポート作成方針

<img src="_img/2026-04-23-10-27-44.png" width="1200">

3. SearXNGから情報収集

<img src="_img/2026-04-23-10-28-17.png" width="1200">

4. 情報のファクトチェック
5. レポートのフォーマット整形

<img src="_img/2026-04-23-10-28-40.png" width="1200">

6. レポート作成

<img src="_img/2026-04-23-10-29-03.png" width="1200">

