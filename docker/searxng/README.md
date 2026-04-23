# Local Deep Research + SearXNG + Ollama（最小構成）

## 概要
- `SearXNG`: 検索エンジン
- `Local Deep Research`: 検索結果を使うリサーチ UI
- `Ollama`: ローカル LLM

このディレクトリでは、`Local Deep Research` から `SearXNG` を参照する最小構成を扱います。

## 前提条件
- Docker が利用可能であること
- Ollama がホスト OS 上で起動していること
- 実行ディレクトリが `docker/searxng` であること
- `settings.yml` がこのディレクトリに存在すること

## OS ごとの前提

### macOS
- Docker Desktop がインストール済みであること
- `host.docker.internal` を利用する前提です
- 以下の macOS 手順は Docker Desktop 環境向けです

### Linux
- native Linux を前提にしています
- `host.docker.internal` は前提にしません
- 必要に応じて `--add-host=host.docker.internal:host-gateway` を使うか、ホスト IP を明示してください

### Windows
- Docker Desktop の利用を前提にしています
- `host.docker.internal` を利用します

---

## 起動手順

### macOS（Docker Desktop 前提）

```bash
#!/bin/bash

# SearXNG 起動
docker rm -f searxng 2>/dev/null || true
docker run -d -p 8080:8080 -v "$(pwd)/settings.yml:/etc/searxng/settings.yml" --name searxng --restart unless-stopped searxng/searxng

# Local Deep Research 起動
docker rm -f local-deep-research 2>/dev/null || true
docker run -d -p 5001:5000 -e SEARXNG_URL=http://host.docker.internal:8080 --name local-deep-research localdeepresearch/local-deep-research
```

### Linux（native Linux）

`host.docker.internal` を使わず、SearXNG コンテナ名をそのまま参照する例です。

```bash
#!/bin/bash

docker network create ldr-net 2>/dev/null || true

# SearXNG 起動
docker rm -f searxng 2>/dev/null || true
docker run -d -p 8080:8080 --network ldr-net -v "$(pwd)/settings.yml:/etc/searxng/settings.yml" --name searxng --restart unless-stopped searxng/searxng

# Local Deep Research 起動
docker rm -f local-deep-research 2>/dev/null || true
docker run -d -p 5001:5000 --network ldr-net -e SEARXNG_URL=http://searxng:8080 --name local-deep-research localdeepresearch/local-deep-research
```

### Windows（PowerShell, Docker Desktop 前提）

```powershell
$pwd = (Get-Location).Path

# SearXNG 起動
docker rm -f searxng 2>$null
docker run -d -p 8080:8080 -v "${pwd}/settings.yml:/etc/searxng/settings.yml" --name searxng --restart unless-stopped searxng/searxng

# Local Deep Research 起動
docker rm -f local-deep-research 2>$null
docker run -d -p 5001:5000 -e SEARXNG_URL=http://host.docker.internal:8080 --name local-deep-research localdeepresearch/local-deep-research
```

---

## 接続先設定（LDR UI）

### Ollama
- macOS: `http://host.docker.internal:11434`
- Linux: ホスト上の Ollama URL を明示
  - 例: `http://127.0.0.1:11434`
  - 例: `http://192.168.x.x:11434`
- Windows: `http://host.docker.internal:11434`

### Search（SearXNG）
- macOS: `http://host.docker.internal:8080`
- Linux:
  - ブラウザから確認する場合: `http://localhost:8080`
  - LDR コンテナ内から参照する場合: `http://searxng:8080`
- Windows: `http://host.docker.internal:8080`

---

## 動作確認

### SearXNG API 確認

```bash
curl "http://localhost:8080/search?q=test&format=json"
```

### コンテナ確認

```bash
docker ps
```

---

## 注意点

### macOS
- Docker Desktop 前提です
- `host.docker.internal` を利用します
- `localhost` はコンテナ内からそのまま参照できません

### Linux
- native Linux では `host.docker.internal` を前提にしないでください
- コンテナ間接続は同一 Docker network 上で名前解決する構成を推奨します
- ホスト上の Ollama をコンテナから参照する場合は、ホスト IP または `host-gateway` の利用を検討してください

### Windows
- Docker Desktop 前提です
- `host.docker.internal` を利用します
- `localhost` はコンテナ内からそのまま参照できません

---

## 構成

```text
[ LDR コンテナ ] (port 5001)
        |
        | macOS / Windows: http://host.docker.internal:8080
        | Linux: http://searxng:8080
        v
[ SearXNG コンテナ ] (port 8080)
        |
        v
外部検索エンジン（brave, bing, wikipedia など）
```

---

## まとめ

- macOS は Docker Desktop 前提で運用する
- Linux は macOS と分けて扱い、`host.docker.internal` 前提にしない
- Windows は Docker Desktop 前提で `host.docker.internal` を使う
