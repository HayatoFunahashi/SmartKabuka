import os
from datetime import datetime
from libs.jp_stock_data import JPStockData
from libs.us_stock_data import USStockData
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
        jp_csv_path = 'input/jp_data.csv'
        us_csv_path = 'input/us_data.csv'
        
        # 日本株データ
        if os.path.exists(jp_csv_path):
            try:
                self.jp_stock_data = JPStockData(jp_csv_path)
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
    
    def create_portfolio_message(self, jp_data: dict, us_data: dict = None, exchange_rate: float = None) -> str:
        """ポートフォリオレポートメッセージを作成"""
        message_lines = ["📊 朝のポートフォリオレポート"]
        message_lines.append("=" * 30)
        
        # 日本株情報
        if jp_data:
            message_lines.append("🇯🇵 日本株")
            message_lines.append(f"銘柄数: {jp_data.get('count', 0)}銘柄")
            
            for stock in jp_data.get('stocks', []):
                code = stock.get('code', '')
                name = stock.get('name', '')
                current_price = stock.get('current_price', 0)
                change = stock.get('price_change', 0)
                change_pct = stock.get('price_change_pct', 0)
                
                # 変動の矢印表示
                arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                
                message_lines.append(f"{arrow} {code} {name}")
                message_lines.append(f"   {current_price:.0f}円 ({change:+.0f}円 {change_pct:+.2f}%)")
            
            message_lines.append("")
        
        # 米国株情報
        if us_data:
            message_lines.append("🇺🇸 米国株")
            message_lines.append(f"銘柄数: {us_data.get('count', 0)}銘柄")
            
            if exchange_rate:
                message_lines.append(f"USD/JPY: {exchange_rate:.2f}")
            
            for stock in us_data.get('stocks', []):
                symbol = stock.get('symbol', '')
                current_price = stock.get('current_price', 0)
                change = stock.get('price_change', 0)
                change_pct = stock.get('price_change_pct', 0)
                
                # 変動の矢印表示
                arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                
                message_lines.append(f"{arrow} {symbol}")
                message_lines.append(f"   ${current_price:.2f} (${change:+.2f} {change_pct:+.2f}%)")
                
                # 円換算表示（為替レートがある場合）
                if exchange_rate:
                    jpy_price = current_price * exchange_rate
                    message_lines.append(f"   ≈{jpy_price:.0f}円")
            
            message_lines.append("")
        
        # 送信時刻
        now = datetime.now().strftime("%Y/%m/%d %H:%M")
        message_lines.append(f"⏰ {now} 更新")
        
        return "\n".join(message_lines)
    
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
        
        # メッセージ作成
        message = self.create_portfolio_message(
            jp_data=jp_data if jp_data else None,
            us_data=us_data if us_data else None,
            exchange_rate=exchange_rate
        )
        
        # LINE通知送信
        print("📱 LINE通知を送信中...")
        success = self.line_notifier.send_message(message)
        
        if success:
            print("✅ 朝のレポートを送信しました")
        else:
            print("❌ レポート送信に失敗しました")
        
        return success
    
    def schedule_check(self) -> bool:
        """実行時刻チェック（GitHub Actionsの場合は常にTrue）"""
        # GitHub Actionsで実行される場合は時間チェックをスキップ
        if os.getenv('GITHUB_ACTIONS'):
            print("🤖 GitHub Actions環境で実行中 - 時間チェックをスキップ")
            return True
        
        now = datetime.now()
        current_hour = now.hour
        
        # 朝6時から9時の間のみ実行
        if 6 <= current_hour < 9:
            return True
        else:
            print(f"⏰ 現在時刻 {now.strftime('%H:%M')} - 朝の通知時間外です (6:00-9:00)")
            return False


def main():
    """メイン実行関数"""
    notifier = MorningNotifier()
    
    print("=" * 50)
    print("🔔 SmartKabuka 朝のポートフォリオ通知システム")
    print("=" * 50)
    
    # 時刻チェック
    if not notifier.schedule_check():
        return
    
    # レポート送信
    success = notifier.send_morning_report()
    
    if success:
        print("\n🎉 朝のレポート送信完了！")
    else:
        print("\n💥 レポート送信に問題が発生しました")
        print("📋 チェック項目:")
        print("  - .envファイルのLINE_MESSAGING_API_TOKEN設定")
        print("  - .envファイルのLINE_USER_ID設定")
        print("  - input/jp_data.csv（日本株）の存在")
        print("  - input/us_data.csv（米国株）の存在")
        print("  - インターネット接続")


if __name__ == "__main__":
    main()