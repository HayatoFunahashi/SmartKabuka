# SmartKabuka - AI-Powered Portfolio Notification System

SBI証券の保有株情報を活用して、株価情報とLINE通知を組み合わせた朝のポートフォリオレポートシステムです。

## 🚀 現在の実装状況

### ✅ 実装済み機能
- **ポートフォリオデータ解析**: SBI証券CSV（日本株・米国株）の自動解析
- **リアルタイム株価取得**: Yahoo Finance APIによる現在価格取得
- **LINE通知**: 朝のポートフォリオレポート自動送信
- **GitHub Actions**: 毎日朝6時（日本時間）の自動実行
- **セキュア運用**: CSVデータをBase64エンコードしてGitHub Secretsで管理

### 🔄 今後の実装予定
- ニュース収集・AI解析機能
- テクニカル指標（移動平均乖離、RSI）による売買判定
- アラート条件のカスタマイズ

## 📋 セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定（.env）
```env
LINE_MESSAGING_API_TOKEN=your_line_messaging_api_token
LINE_USER_ID=your_line_user_id
```

### 3. CSVデータの準備
SBI証券から以下のファイルをダウンロードして`input/`フォルダに配置：
- `jp_data.csv` (日本株データ)
- `us_data.csv` (米国株データ)

### 4. GitHub Actions用セットアップ（本番運用）
```bash
# GitHub CLI認証
gh auth login

# CSVデータをSecretsに登録
python3 update_secrets.py
```

## 🏗️ アーキテクチャ

### コアコンポーネント
- `morning_notifier.py`: メイン実行ファイル・ポートフォリオレポート作成
- `libs/jp_stock_data.py`: 日本株データ管理
- `libs/us_stock_data.py`: 米国株データ管理
- `stock_price_fetcher.py`: Yahoo Finance API連携
- `line_notifier.py`: LINE Messaging API通知
- `update_secrets.py`: GitHub Secrets管理ツール

## 入力csvのデータフォーマット

CSVはSJISでエンコーディングされた，カンマ区切りデータです．
株式・投資信託ごとに複数のセクションに分かれており、各セクションごとにヘッダー行とデータ行が存在します。
合計行や説明行も含まれています。

### 主なセクション例

- 株式（現物/一般預り）
- 株式（現物/NISA預り（成長投資枠））
- 株式（現物/旧NISA預り）
- 投資信託（金額/特定預り）
- 投資信託（金額/NISA預り（つみたて投資枠））

### 各セクションのカラム例

株式セクション

```
"銘柄（コード）","買付日","数量","取得単価","現在値","前日比","前日比（％）","損益","損益（％）","評価額"
```

投資信託セクション

```
"ファンド名","買付日","数量","取得単価","現在値","前日比","前日比（％）","損益","損益（％）","評価額"
```

CAUTION: 

* セクションごとにヘッダー行が繰り返されます。
* 合計行や説明行も含まれるため、データ抽出時は不要行のスキップが必要です。
* 数値はカンマ区切り、小数点あり・なしが混在しています。