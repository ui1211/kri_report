# Python + VSCode

## 目的
このマニュアルのみで以下を実現する

- Python環境構築
- VSCode設定
- git設定

---

# 1. Python インストール

1. 「python 3.12」と検索

<img src="_img/2026-04-20-08-45-15.png" width="1200">

2. サイト下部の「windows installer (64bit)」をクリック

<img src="_img/2026-04-20-08-45-29.png" width="1200">

## 設定

1. インストーラーを起動(ダウンロードしたexeファイルをクリック)

<img src="_img/2026-04-20-08-53-50.png" width="200">

2. 「Add Python to PATH」にチェックを入れてインストール

<img src="_img/2026-04-20-08-47-55.png" width="1200">

## 確認

1. 検索バーに「cmd」を入力し「コマンドプロンプト」を起動

<img src="_img/2026-04-20-08-59-02.png" width="1200">

2. 「python」を入力し「エンターキー」を押下すると、「pythonの対話モード」に入る
```bash
python
```
3. 「python 3.12.0」と表示され、「>>>」の入力まち状態になれば確認完了

<img src="_img/2026-04-20-08-57-47.png" width="1200">

4. 「print("hello")」を入力してエンターキーを押下すると、「hello」が表示される

```bash
print("hello")
```

<img src="_img/2026-04-20-09-04-33.png" width="1200">

5. 「exit()」を入力してエンターキーを押下すると「pythonの対話モード」を終了する

<img src="_img/2026-04-20-09-12-03.png" width="1200">

1. 「pip install uv」を入力してエンターキーを押下してパッケージ管理ライブラリ「uv」をインストールする
```bash
pip install uv
```
<img src="_img/2026-04-20-14-00-15.png" width="1200">

---

# 6. VSCode設定

1. webサイトからインストーラをダウンロードしてPCにインストール

https://code.visualstudio.com/

<img src="_img/2026-04-20-13-26-07.png" width="1200">


## 拡張機能のインストール

1. サイドバーの「拡張機能」を選択

<img src="_img/2026-04-20-13-39-38.png" width="1200">

2. 検索ウィンドウから各種拡張機能を選択してインストール

<img src="_img/2026-04-20-13-41-37.png" width="1200">

|-|-|
|---|---|
|便利系|<img src="_img/2026-04-20-13-50-34.png" width="300"><img src="_img/2026-04-20-13-45-28.png" width="300"><img src="_img/2026-04-20-13-50-50.png" width="300"><img src="_img/2026-04-20-13-52-03.png" width="300"><img src="_img/2026-04-20-13-54-20.png" width="300"><img src="_img/2026-04-20-14-03-30.png" width="300">|
|python|<img src="_img/2026-04-20-13-44-42.png" width="300">|
|markdown|<img src="_img/2026-04-20-13-48-23.png" width="300">|
|画像|<img src="_img/2026-04-20-13-46-11.png" width="300"><img src="_img/2026-04-20-13-46-28.png" width="300">|

## 作業ディレクトリの作成

2. デスクトップに「work」フォルダを作成

<img src="_img/2026-04-20-13-28-34.png" width="1200">

3. VSCodeを起動しサイドバーの「エクスプローラ」を開き、「フォルダーを開く」を選択

<img src="_img/2026-04-20-13-32-26.png" width="1200">

4. 作業ディレクトリとしてデスクトップに作成した「work」を選択する

<img src="_img/2026-04-20-13-36-01.png" width="1200">

---

# git設定

1. 公式サイトからインストーラをダウンロードしてインストール

https://git-scm.com/install/windows

<img src="_img/2026-04-20-14-05-49.png" width="1200">

2. コマンドプロンプトに「git -v」を入力してエンターキー押下でバージョン表示が出れば終了

<img src="_img/2026-04-20-14-07-16.png" width="1200">

---

