import os
from datetime import datetime
from libs.jp_stock_data import JPStockData
from libs.us_stock_data import USStockData
from stock_price_fetcher import StockPriceFetcher
from line_notifier import LineNotifier
import yfinance as yf
import pytz


class StockNotifier:
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
        jst = pytz.timezone('Asia/Tokyo')
        now = datetime.now(jst).strftime("%Y/%m/%d %H:%M")
        message_lines.append(f"⏰ {now} 更新")
        message_lines.append(self.line_notifier.get_usage())
        
        return "\n".join(message_lines)
    
    def _create_jp_stock_section(self, jp_data: dict) -> list:
        """日本株セクションのメッセージを作成"""
        lines = []
        lines.append("🇯🇵 日本株")
        lines.append(f"銘柄数: {jp_data.get('count', 0)}銘柄")
        
        for stock in jp_data.get('stocks', []):
            code = stock.get('code', '')
            name = stock.get('name', '')
            current_price = stock.get('current_price', 0)
            change = stock.get('price_change', 0)
            change_pct = stock.get('price_change_pct', 0)
            
            # 変動の矢印表示
            arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            
            lines.append(f"{arrow} {code} {name}")
            lines.append(f"   {current_price:.0f}円 ({change:+.0f}円 {change_pct:+.2f}%)")
        
        return lines
    
    def _create_us_stock_section(self, us_data: dict, exchange_rate: float = None) -> list:
        """米国株セクションのメッセージを作成"""
        lines = []
        lines.append("🇺🇸 米国株")
        lines.append(f"銘柄数: {us_data.get('count', 0)}銘柄")
        
        if exchange_rate:
            lines.append(f"USD/JPY: {exchange_rate:.2f}")
        
        for stock in us_data.get('stocks', []):
            symbol = stock.get('symbol', '')
            current_price = stock.get('current_price', 0)
            change = stock.get('price_change', 0)
            change_pct = stock.get('price_change_pct', 0)
            
            # 変動の矢印表示
            arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            
            lines.append(f"{arrow} {symbol}")
            lines.append(f"   ${current_price:.2f} (${change:+.2f} {change_pct:+.2f}%)")
            
            # 円換算表示（為替レートがある場合）
            if exchange_rate:
                jpy_price = current_price * exchange_rate
                lines.append(f"   ≈{jpy_price:.0f}円")
        
        return lines
    
    def _add_timestamp_and_usage(self, lines: list) -> list:
        """タイムスタンプと使用状況を追加"""
        jst = pytz.timezone('Asia/Tokyo')
        now = datetime.now(jst).strftime("%Y/%m/%d %H:%M")
        lines.append(f"\n⏰ {now} 更新")
        lines.append(self.line_notifier.get_usage())
        return lines
    
    def _send_report(self, message: str, success_msg: str) -> bool:
        """共通のレポート送信処理"""
        print("📱 LINE通知を送信中...")
        success = self.line_notifier.send_message(message, isbroadcast=False)
        
        if success:
            print(f"✅ {success_msg}")
        else:
            print("❌ レポート送信に失敗しました")
        
        return success
    
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
        success = self.line_notifier.send_message(message, isbroadcast=False)
        
        if success:
            print("✅ 朝のレポートを送信しました")
        else:
            print("❌ レポート送信に失敗しました")
        
        return success
    
    def send_jp_report(self) -> bool:
        """日本株レポートを送信"""
        print("🇯🇵 日本株レポートを作成中...")
        
        # 日本株データ収集
        jp_data = self.collect_jp_stock_data()
        
        # 通知がない場合
        if not jp_data:
            print("❌ 送信する日本株データがありません")
            return False
        
        # メッセージ作成（日本株のみ）
        message_lines = ["📊 日本株レポート (16:00)", "=" * 30]
        message_lines.extend(self._create_jp_stock_section(jp_data))
        self._add_timestamp_and_usage(message_lines)
        
        message = "\n".join(message_lines)
        return self._send_report(message, "日本株レポートを送信しました")
    
    def send_us_report(self) -> bool:
        """米国株レポートを送信"""
        print("🇺🇸 米国株レポートを作成中...")
        
        # 米国株データ収集
        us_data = self.collect_us_stock_data()
        exchange_rate = self.get_exchange_rate() if us_data else None
        
        # 通知がない場合
        if not us_data:
            print("❌ 送信する米国株データがありません")
            return False
        
        # メッセージ作成（米国株のみ）
        message_lines = ["📊 米国株レポート (06:00)", "=" * 30]
        message_lines.extend(self._create_us_stock_section(us_data, exchange_rate))
        self._add_timestamp_and_usage(message_lines)
        
        message = "\n".join(message_lines)
        return self._send_report(message, "米国株レポートを送信しました")
    
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
    import argparse
    
    # コマンドライン引数を解析
    parser = argparse.ArgumentParser(description='Portfolio notification system')
    parser.add_argument('--market', choices=['jp', 'us', 'both'], default='both',
                       help='Market to notify (jp: Japanese stocks, us: US stocks, both: both markets)')
    args = parser.parse_args()
    
    notifier = StockNotifier()
    
    print("=" * 50)
    if args.market == 'jp':
        print("🇯🇵 SmartKabuka 日本株通知システム")
    elif args.market == 'us':
        print("🇺🇸 SmartKabuka 米国株通知システム")
    else:
        print("🔔 SmartKabuka ポートフォリオ通知システム")
    print("=" * 50)
    
    # 時刻チェック（GitHub Actionsでは常にTrue）
    if not notifier.schedule_check():
        return
    
    # 市場指定に応じてレポート送信
    if args.market == 'jp':
        success = notifier.send_jp_report()
    elif args.market == 'us':
        success = notifier.send_us_report()
    else:
        success = notifier.send_morning_report()
    
    if success:
        market_name = {"jp": "日本株", "us": "米国株", "both": "ポートフォリオ"}[args.market]
        print(f"\n🎉 {market_name}レポート送信完了！")
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