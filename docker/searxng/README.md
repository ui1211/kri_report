# Local Deep Research + SearXNG + Ollama（最小構成）

## 概要
- SearXNG：検索エンジン
- Local Deep Research：検索エージェント
- Ollama：LLM

---

## 起動コマンド（PowerShell）

```
docker rm -f searxng; docker run -d -p 8080:8080 -v ${PWD}/settings.yml:/etc/searxng/settings.yml --name searxng --restart unless-stopped searxng/searxng
```

```
docker rm -f local-deep-research; docker run -d -p 5001:5000 -e SEARXNG_URL=http://host.docker.internal:8080 --name local-deep-research localdeepresearch/local-deep-research
```

---

## 必須設定（LDR UI）

### Ollama
http://host.docker.internal:11434
<img src="_img/2026-04-01-16-49-42.png" width="1200">


### Search（SearXNG）
http://host.docker.internal:8080
<img src="_img/2026-04-01-16-50-15.png" width="1200">

---

## 動作確認

### SearXNG
curl "http://localhost:8080/search?q=test&format=json"

### コンテナ確認
docker ps

---

## 注意点
- localhost はコンテナ内では使えない
- 必ず host.docker.internal を使う
- Windowsでは --network host は使わない

---

## 構成
[ LDRコンテナ ]
        ↓
http://host.docker.internal:8080
        ↓
[ SearXNG ]
        ↓
外部検索

---

## まとめ
- Docker構成はこれでOK
- URL設定だけ間違えなければ動く