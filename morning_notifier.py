import os
from datetime import datetime
from stock_data import StockData
from us_stock_data import USStockData
from stock_price_fetcher import StockPriceFetcher
from line_notifier import LineNotifier
import yfinance as yf


class MorningNotifier:
    """朝のポートフォリオ通知システム"""
    
    def __init__(self):
        self.jp_stock_data = None
        self.us_stock_data = None
        self.price_fetcher = StockPriceFetcher()
        self.line_notifier = LineNotifier()
        
        # データファイルの存在確認と読み込み
        self._load_portfolio_data()
    
    def _load_portfolio_data(self):
        """ポートフォリオデータを読み込み"""
        jp_csv_path = 'input/data.csv'
        us_csv_path = 'input/us_data.csv'
        
        # 日本株データ
        if os.path.exists(jp_csv_path):
            try:
                self.jp_stock_data = StockData(jp_csv_path)
                print(f"✅ 日本株データを読み込みました: {len(self.jp_stock_data.get_stock_codes())}銘柄")
            except Exception as e:
                print(f"❌ 日本株データの読み込みエラー: {e}")
        
        # 米国株データ
        if os.path.exists(us_csv_path):
            try:
                self.us_stock_data = USStockData(us_csv_path)
                print(f"✅ 米国株データを読み込みました: {len(self.us_stock_data.get_stock_symbols())}銘柄")
            except Exception as e:
                print(f"❌ 米国株データの読み込みエラー: {e}")
    
    def get_exchange_rate(self) -> float:
        """USD/JPYの為替レートを取得"""
        try:
            ticker = yf.Ticker("USDJPY=X")
            data = ticker.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
        except Exception as e:
            print(f"為替レート取得エラー: {e}")
        
        # デフォルト値（手動更新が必要）
        return 150.0
    
    def collect_jp_stock_data(self) -> dict:
        """日本株の現在価格を取得"""
        if not self.jp_stock_data:
            return {}
        
        codes = self.jp_stock_data.get_stock_codes()
        if not codes:
            return {}
        
        print("📈 日本株価格を取得中...")
        current_prices = self.price_fetcher.get_multiple_prices(codes, market="JP", delay=0.3)
        
        stocks = []
        for code in codes:
            price_data = current_prices.get(code)
            stock_details = self.jp_stock_data.get_stock_details(code)
            
            if price_data and stock_details:
                stocks.append({
                    'code': code,
                    'name': stock_details['name'],
                    'current_price': price_data['current_price'],
                    'price_change': price_data['price_change'],
                    'price_change_pct': price_data['price_change_pct'],
                    'quantity': stock_details['quantity'],
                    'acquisition_price': stock_details['acquisition_price']
                })
        
        return {
            'count': len(stocks),
            'stocks': stocks
        }
    
    def collect_us_stock_data(self) -> dict:
        """米国株の現在価格を取得"""
        if not self.us_stock_data:
            return {}
        
        symbols = self.us_stock_data.get_stock_symbols()
        if not symbols:
            return {}
        
        print("📈 米国株価格を取得中...")
        current_prices = self.price_fetcher.get_multiple_prices(symbols, market="US", delay=0.3)
        
        stocks = []
        for symbol in symbols:
            price_data = current_prices.get(symbol)
            stock_details = self.us_stock_data.get_stock_details(symbol)
            
            if price_data and stock_details:
                stocks.append({
                    'symbol': symbol,
                    'current_price': price_data['current_price'],
                    'price_change': price_data['price_change'],
                    'price_change_pct': price_data['price_change_pct'],
                    'quantity': stock_details['quantity'],
                    'acquisition_price_usd': stock_details['acquisition_price_usd']
                })
        
        return {
            'count': len(stocks),
            'stocks': stocks
        }
    
    def send_morning_report(self) -> bool:
        """朝のレポートを送信"""
        print("🌅 朝のポートフォリオレポートを作成中...")
        
        # データ収集
        jp_data = self.collect_jp_stock_data()
        us_data = self.collect_us_stock_data()
        exchange_rate = self.get_exchange_rate() if us_data else None
        
        # 通知がない場合
        if not jp_data and not us_data:
            print("❌ 送信するポートフォリオデータがありません")
            return False
        
        # LINE通知送信
        print("📱 LINE通知を送信中...")
        success = self.line_notifier.send_portfolio_summary(
            jp_data=jp_data if jp_data else None,
            us_data=us_data if us_data else None,
            exchange_rate=exchange_rate
        )
        
        if success:
            print("✅ 朝のレポートを送信しました")
        else:
            print("❌ レポート送信に失敗しました")
        
        return success
    
    def schedule_check(self) -> bool:
        """実行時刻チェック（朝8-9時の間のみ実行）"""
        now = datetime.now()
        current_hour = now.hour
        
        # 朝8時から9時の間のみ実行
        if 8 <= current_hour < 9:
            return True
        else:
            print(f"⏰ 現在時刻 {now.strftime('%H:%M')} - 朝の通知時間外です (8:00-9:00)")
            return False


def main():
    """メイン実行関数"""
    notifier = MorningNotifier()
    
    print("=" * 50)
    print("🔔 SmartKabuka 朝のポートフォリオ通知システム")
    print("=" * 50)
    
    # 時刻チェック（テスト時はコメントアウト）
    # if not notifier.schedule_check():
    #     return
    
    # レポート送信
    success = notifier.send_morning_report()
    
    if success:
        print("\n🎉 朝のレポート送信完了！")
    else:
        print("\n💥 レポート送信に問題が発生しました")
        print("📋 チェック項目:")
        print("  - .envファイルのLINE_NOTIFY_TOKEN設定")
        print("  - input/data.csv（日本株）の存在")
        print("  - input/us_data.csv（米国株）の存在")
        print("  - インターネット接続")


if __name__ == "__main__":
    main()