
# 4. 仮想環境作成

```powershell
uv venv
```

```powershell
.venv\Scripts\activate
```

成功すると `( .venv )` が表示される


::contentReference[oaicite:1]{index=1}


---

# 5. ライブラリインストール

```powershell
uv pip install pandas matplotlib jupyter
```



---

# 8. 仮想環境を選択

1. フォルダを開く（titanic_project）
2. `Ctrl + Shift + P`
3. `Python: Select Interpreter`
4. `.venv` を選択


::contentReference[oaicite:3]{index=3}


---

# 9. Titanicデータ準備

以下をダウンロード

https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv

保存場所

```
titanic_project/
 ├── titanic.csv
```

---

# 10. Notebook 作成

VSCodeで新規作成

```
analysis.ipynb
```


::contentReference[oaicite:4]{index=4}


---

# 11. CSV読み込み

```python
import pandas as pd

df = pd.read_csv("titanic.csv")
df.head()
```

実行するとデータが表で表示される


::contentReference[oaicite:5]{index=5}


---

# 12. グラフ表示

## 生存者数

```python
import matplotlib.pyplot as plt

df["Survived"].value_counts().plot(kind="bar")
plt.title("Survived Count")
plt.show()
```


::contentReference[oaicite:6]{index=6}


---

## 年齢分布

```python
df["Age"].plot(kind="hist", bins=20)
plt.title("Age Distribution")
plt.show()
```


::contentReference[oaicite:7]{index=7}


---

## 性別ごとの生存率

```python
df.groupby("Sex")["Survived"].mean().plot(kind="bar")
plt.title("Survival Rate by Sex")
plt.show()
```


::contentReference[oaicite:8]{index=8}


---

# 13. よくあるエラー

## グラフが出ない
```python
plt.show()
```

---

## CSVが読めない
- ファイル名確認
- 同じフォルダに置く

---

## 仮想環境が効いていない

```powershell
.venv\Scripts\activate
```

---

# 14. 完了状態

- データが表示される
- グラフが表示される

---

# まとめ

このマニュアルでできること

- CSV読み込み
- データ確認
- 可視化

→ データ分析の入口
