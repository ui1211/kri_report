# レポート

## 1. メタ情報
- 作成日時：2026-04-23
- 入力概要：点群データ処理・可視化 OSS の選定・比較（点群データ可視化特化ツール追加）
- トピック数：11

## 2. 概要
点群データの処理・可視化において、点群データとメタデータを連携・保持できる OSS ツールの選定と比較をまとめる。特に点群データ可視化に特化した OSS（pptk, pcloudpy, cilantro, mapbox/pointcloud など）を追加。現状のツール群は各分野で実運用されているが、C++ コンパイルやライセンス制約といった課題がある。Python API による導入や GPU 加速、Web ブラウザ可視化など多様な解決策が存在し、点群データ可視化に特化したツールを選定することで、導入コストや点群の処理品質を比較できる。

旧版の広範なツール比較、性能値とリンクは全面的な再検証を終えていない。採用時は各公式資料と実データで確認する。

## 3. 現状
- **業界全体の状況**: 点群データ処理は測量業・インフラ検査・アスファルト点群分析などで実運用され、Web ブラウザで軽量閲覧したい場合や大規模点群（1 億点）を扱う場合は対応ツールを選定する必要がある。点群データ可視化に特化したツールとして、Python 中心の軽量なライブラリや、Web ブラウザ上で動作する WebGL 基盤のソリューションが増加。
- **実運用事例**:
  - CloudCompare: 測量業・インフラ検査で実運用中（[cloudcompare.org](https://cloudcompare.org)）
  - Potree: アスファルト点群などで実運用（[potree/potree](https://github.com/potree/potree)）
  - [OpenDroneMap ODM](https://github.com/OpenDroneMap/ODM): 航空画像から地図、点群、3Dモデルを生成する。
  - PCL: ロボティクス・自動運転での点群処理実運用（[PointCloudLibrary/pcl](https://github.com/PointCloudLibrary/pcl)）
  - pptk: 簡易点群可視化ツールとして利用（[heremaps/pptk](https://github.com/heremaps/pptk)）

## 4. 課題
- C1: 一部の環境では依存関係やソースビルドによって導入が難しくなる
- C2: GPL対象コードの結合・配布ではライセンス条件を確認する必要がある。別プログラムとしての使用や配布形態は一律に禁止とはいえない。[GNU GPL FAQ](https://www.gnu.org/licenses/gpl-faq.en.html)
- C3: 大規模点群（1 億点）のメモリ管理
- C4: メタデータ変換時の損失
- C5: WebGL 環境依存とネットワーク通信
- C6: Kubernetes クラスタでの推論効率・コンテナオーバーヘッド
- C7: ドローン専用イメージ処理に偏る
- C8: 点群データ可視化に特化した機能不足

## 5. AI 解決
- C1 対応:
  - OSS: `open3d-cpu` ライトビルド、`pip install open3d`で手軽導入
  - 研究：PyTorch/TensorFlow 連携の最適化（arXiv:1801.09847）
  - 実運用：`open3d.ml`モジュールによる ML パイプライン
- C2 対応:
  - 研究：BSD ライセンス（PCL）
  - 実運用：商用 OSS 以外の選択肢検討（DroneDeploy 等）
- C3 対応:
  - OSS: Open3D(GPU 加速), CloudCompare(octree 最適化)
  - 研究：オクターツ構造による高速処理
  - 実運用：1 億点程度まで対応
- C4 対応:
  - OSS: CloudCompare（プラグイン拡張）, Potree（LOD テクスチャ保存）
  - 研究：メタデータ連携機能の実装
  - 実運用：ファイル形式変換時の損失対策
- C5 対応:
  - OSS: Potreeなどのブラウザ可視化候補を対象環境で評価する。
  - 研究：WebGL 環境依存の解消
  - 実運用：Web ブラウザ上で点群・画像・メタデータ同時表示
- C6 対応:
  - OSS: 候補ツールの実データでメモリと処理時間を測定する。
  - 研究：Kubernetes シーリング
  - 実運用：4 万实例以上で安定動作
- C7 対応:
  - OSS: 複数センサー同時処理対応
  - 研究：汎用性向上
  - 実運用：ドローン画像からマップ/点群/3D モデル/DEM 生成
- C8 対応:
  - OSS: pptk, pcloudpy, cilantro, mapbox/pointcloud
  - 研究：点群可視化アルゴリズムの開発
  - 実運用：点群データ可視化に特化した機能追加

## 6. 価値
- **コスト削減**: pip インストールで手軽導入、CPU 版対応
- **精度向上**: GPU 加速による高速処理、物理ベースレンダリング（PBR）
- **自動化**: PyTorch/TensorFlow 連携で ML パイプライン構築
- **リスク低減**: ライセンスと入出力形式を導入前に確認する。
- **比較**: 速度や対応点数の定量効果は条件と根拠が不明。実データで測定する。
- **点群可視化特化**: 簡易可視化ライブラリの増加により、導入方法と機能の比較

## 7. トピック一覧
### Open3D
- 概要: [Open3D 公式ドキュメント](https://www.open3d.org)
- 特徴:
  - GPU 加速・物理ベースレンダリング（PBR）
  - PyTorch/TensorFlow 連携
  - Python/C++ デュアル API
- 主要スペック or 数値: GitHub 13.5k 星・2.6k フォーク
- 制約 or 注意点: [公式手順](https://www.open3d.org/docs/release/getting_started.html)にはPythonパッケージのインストール方法があり、C++のソースコンパイルは常に必須ではない。環境・対応wheelを確認する。

### CloudCompare
- 概要: [CloudCompare 公式ドキュメント](https://cloudcompare.org)
- 特徴:
  - オクターツ構造による高速処理（1 億点程度）
  - 測量業・インフラ検査で実運用
  - プラグイン形式で機能拡張
- 主要スペック or 数値: 2026-10-28確認時点で[公式リリース](https://github.com/CloudCompare/CloudCompare/releases)のLatestはv2.13.2、v2.14.beta2はプレリリース。2.14の[変更履歴](https://github.com/CloudCompare/CloudCompare/blob/master/CHANGELOG.md)にはdotBIMメッシュの読み込み専用フィルタが記載される。
- 制約 or 注意点: [公式リポジトリ](https://github.com/CloudCompare/CloudCompare)のGPL条件を確認。配布・結合方式や各コンポーネントで条件が異なる。ベータは本番採用前に検証する。

### Potree
- 概要: [Potree GitHub](https://github.com/potree/potree)
- 特徴:
  - オート LOD テクスチャ管理
  - Web ブラウザ上での軽量閲覧
  - 3D 点群を WebGL で可視化
- 主要スペック or 数値：実運用事例多数
- 制約 or 注意点：Web 標準 GL 依存

### PCL
- 概要: [PCL DeepWiki](https://deepwiki.com/PointCloudLibrary/pcl)
- 特徴:
  - コンプリートなアルゴリズム・データ構造
  - 取得/フィルタ/分析/セグメンテーション/登録/可視化
  - LiDAR センサ対応
- 主要スペック or 数値：実装情報あり
- 制約 or 注意点：複雑な依存関係

### OpenDroneMap
- 概要: [OpenDroneMap ODM](https://github.com/OpenDroneMap/ODM)は航空画像から点群・3Dモデル等を作るツール。旧版のOpenDRIVEという名称とリンクは誤り。
- 特徴:
  - 画像から地図、点群、3Dモデルや標高モデルを生成する。
- 主要スペック or 数値: 不明。
- 制約 or 注意点: 撮影条件、入出力、別途必要な閲覧手段を確認する。

### OpenClaw（要再調査）
- 概要: 旧版のリンクは対象ツールを裏付けず、同名製品の特定もできないため採用候補から除外する。
- 特徴:
  - 機能、ライセンス、実績は不明。
- 主要スペック or 数値: 不明。
- 制約 or 注意点: 正式な製品名と一次資料が確認できるまで比較に使用しない。

### Ouster/Vector SDK
- 概要: [Ouster SDK ドキュメント](https://static.ouster.dev/sdk-docs/python/viz/index.html)
- 特徴:
  - センサー固有フォーマット対応
  - Python/C++ ビンディング
  - 専用可視化ツール（ouster_viz）
- 主要スペック or 数値：製品センサー限定
- 制約 or 注意点：ハードウェア依存

### pptk
- 概要: [Point Processing Toolkit](https://github.com/heremaps/pptk)
- 特徴:
  - 簡易的な 2D/3D 点群可視化
  - Python ベースで軽量
  - 点群形式の変換・可視化
- 主要スペック or 数値：軽量ライブラリ
- 制約 or 注意点：高度な可視化機能は限定的

### pcloudpy
- 概要: [pcloudpy GitHub](https://github.com/mmolero/pcloudpy)
- 特徴:
  - NumPy/SciPy/VTK を活用した点群処理
  - 可視化・フィルタリング・分析機能
  - Python 標準ライブラリとの親和性
- 主要スペック or 数値：実装情報あり
- 制約 or 注意点：VTK 依存

### cilantro
- 概要: [cilantro GitHub](https://github.com/RobotLocomotion/cilantro)
- 特徴:
  - 軽量で効率的な点群処理（C++）
  - フィルタリング・クラスタリング・セグメンテーション
  - Open3D 連携
- 主要スペック or 数値：実装情報あり
- 制約 or 注意点：C++ ベース

### mapbox/pointcloud
- 概要: [mapbox/pointcloud](https://github.com/mapbox/pointcloud)
- 特徴:
  - Mapbox による点群可視化
  - WebGL 対応
  - 大規模点群のストリーミング表示
- 主要スペック or 数値：実装情報あり
- 制約 or 注意点：Mapbox エコシステム依存

### VTK
- 概要: [VTK](https://vtk.org/)
- 特徴:
  - 汎用的な 3D グラフィックス・画像処理ライブラリ
  - 点群可視化・メッシュ処理
  - C++/Python API
- 主要スペック or 数値：20 年超の実績
- 制約 or 注意点：複雑な依存関係

### PyVista
- 概要: [PyVista](https://docs.pyvista.org/)
- 特徴:
  - VTK の Python ラッパー
  - 点群可視化・メッシュ操作
  - Open3D/Trimesh との互換性
- 主要スペック or 数値：GitHub 3.5k 星
- 制約 or 注意点：VTK 依存

## 8. 比較まとめ
- 比較軸:
  - 精度
  - コスト
  - 導入難易度
  - 拡張性
- 違い:
  - Open3D: Python/C++デュアル、pip 導入、GPU 対応、中程度の学習曲線
  - CloudCompare: C++、CMake、高メモリ効率、中程度の GPU 対応、高い学習曲線
  - Potree: Web、cmake、中程度のメモリ効率、中程度の GPU 対応、中程度の学習曲線
  - PCL: C++、cmake、低メモリ効率、中程度の GPU 対応、高い学習曲線
  - OpenDroneMap: 航空画像から点群等を生成。性能と必要資源は環境次第。
  - Ouster/Vector SDK: Python/C++、pip、中程度のメモリ効率、中程度の GPU 対応、中程度の学習曲線
  - pptk: Python、pip、低メモリ効率、中程度の GPU 対応、低い学習曲線
  - pcloudpy: Python、pip、中程度のメモリ効率、中程度の GPU 対応、中程度の学習曲線
  - cilantro: C++、CMake、中程度のメモリ効率、中程度の GPU 対応、中程度の学習曲線
  - mapbox/pointcloud: Web/JavaScript、npm、中程度のメモリ効率、高 GPU 対応、中程度の学習曲線
  - VTK: C++/Python、CMake、中程度のメモリ効率、中程度の GPU 対応、高い学習曲線
  - PyVista: Python、pip、中程度のメモリ効率、中程度の GPU 対応、低い学習曲線
- 使い分け:
  - Python 中心：Open3D, pptk, pcloudpy, PyVista
  - C++ 中心：CloudCompare, PCL, cilantro
  - Web ブラウザ：Potree, mapbox/pointcloud
  - 大規模データ：CloudCompare, Open3D(GPU), VTK
  - センサー専用：Ouster/Vector SDK
  - 簡易可視化：pptk, pcloudpy
  - ロボティクス：PCL, cilantro
- 強み / 弱み:
  - Open3D: 強み（GPU 加速・ML 連携・Python/C++ デュアル）、弱み（C++ コンパイル難易度）
  - CloudCompare: 強み（オクターツ構造・1 億点対応・実運用実績）、弱み（GPL ライセンス・ソース管理負担）
  - Potree: 強み（WebGL なり上げ・Web ブラウザ可視化）、弱み（Web 標準 GL 依存・大規模データへの対応要件）
  - PCL: 強み（コンプリートなアルゴリズム）、弱み（複雑な依存関係）
  - OpenDroneMap: 強み（航空画像から点群生成）、制約（撮影条件と処理資源の確認が必要）
  - Ouster/Vector SDK: 強み（センサー固有フォーマット）、弱み（ハードウェア依存）
  - pptk: 強み（簡易可視化・軽量）、弱み（機能制限）
  - pcloudpy: 強み（VTK 連携・標準ライブラリ活用）、弱み（VTK 依存）
  - cilantro: 強み（軽量・効率的）、弱み（C++ 依存）
  - mapbox/pointcloud: 強み（Web 可視化・大規模データ）、弱み（Mapbox 依存）
  - VTK: 強み（汎用性・実績）、弱み（複雑さ）
  - PyVista: 強み（VTK の Python ラッパー・使いやすさ）、弱み（VTK 依存）

## 9. 更新履歴
- 2026-04-22: 初版作成（点群データ・OSS・メタデータ連携調査）
- 2026-04-22: 最新情報更新（Open3D v0.19 / CloudCompare v2.13.2）
- 2026-04-23: 点群データ可視化に特化した OSS（pptk, pcloudpy, cilantro, mapbox/pointcloud, PyVista）を追加
- 2026-10-28: CloudCompare安定版とベータ版、GPL条件、Open3D導入、OpenDroneMapと未確認のOpenClawを修正。旧比較の再検証範囲を明示。

## 10. 参考リンク一覧
- [CloudCompare releases](https://github.com/CloudCompare/CloudCompare/releases)
- [CloudCompare changelog](https://github.com/CloudCompare/CloudCompare/blob/master/CHANGELOG.md)
- [CloudCompare repository](https://github.com/CloudCompare/CloudCompare)
- [GNU GPL FAQ](https://www.gnu.org/licenses/gpl-faq.en.html)
- [Open3D getting started](https://www.open3d.org/docs/release/getting_started.html)
- [OpenDroneMap ODM](https://github.com/OpenDroneMap/ODM)
- [Open3D 公式ドキュメント](https://www.open3d.org)
- [CloudCompare 公式ドキュメント](https://cloudcompare.org)
- [Potree GitHub](https://github.com/potree/potree)
- [PCL DeepWiki](https://deepwiki.com/PointCloudLibrary/pcl)
- [Ouster SDK ドキュメント](https://static.ouster.dev/sdk-docs/python/viz/index.html)
- [Nature Methods: PoCA](https://www.nature.com/articles/s41592-023-01811-4)
- [SciDirect: 3D Point Cloud Visualization](https://www.sciencedirect.com/science/article/pii/S2352711025004091)
- [Point Processing Toolkit](https://github.com/heremaps/pptk)
- [pcloudpy GitHub](https://github.com/mmolero/pcloudpy)
- [cilantro GitHub](https://github.com/RobotLocomotion/cilantro)
- [mapbox/pointcloud](https://github.com/mapbox/pointcloud)
- [VTK](https://vtk.org/)
- [PyVista](https://docs.pyvista.org/)
