import os
import requests
from typing import Optional
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage

"""
see : Line bot api documentation
https://github.com/line/line-bot-sdk-python/blob/master/linebot/v3/messaging/docs/MessagingApi.md
"""

class LineNotifier:
    """LINE APIを使用した通知機能"""
    
    def __init__(self):
        # 環境変数を読み込み
        load_dotenv()
        self.token = os.getenv('LINE_MESSAGING_API_TOKEN')
        self.user_id = os.getenv('LINE_USER_ID')
        self.line_bot_api = LineBotApi(self.token)
    
    def send_message(self, message: str) -> bool:
        """LINE Messaging APIでメッセージを送信"""               
        self.line_bot_api.push_message(
            to=self.user_id,
            messages=TextSendMessage(text=message))
    
    def send_portfolio_summary(self, jp_data: dict, us_data: dict = None, exchange_rate: float = None) -> bool:
        """ポートフォリオサマリーをLINEで送信"""
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
        from datetime import datetime
        now = datetime.now().strftime("%Y/%m/%d %H:%M")
        message_lines.append(f"⏰ {now} 更新")
        
        message = "\n".join(message_lines)
        return self.send_message(message)
    
    def test_connection(self) -> bool:
        """LINE Messaging API接続テスト"""
        test_message = "🔔 SmartKabuka接続テスト"
        return self.send_message(test_message)


def main():
    """テスト用のメイン関数"""
    notifier = LineNotifier()
    
    print("=== LINE Messaging API接続テスト ===")
    success = notifier.test_connection()
    
    if success:
        print("✅ LINE通知が正常に送信されました")
    else:
        print("❌ LINE通知の送信に失敗しました")
        print("💡 .envファイルのLINE_MESSAGING_API_TOKENを確認してください")
        print("💡 LINE Messaging APIトークンの取得方法:")
        print("   1. https://developers.line.biz/ja/ にアクセス")
        print("   2. 「ログイン」→「コンソール」にアクセスする")
        print("   3. 通知を送りたい「チャネル」→「MessagingAPI設定」→「トークンを発行」")


if __name__ == "__main__":
    main()