import os
import requests
from typing import Optional
from dotenv import load_dotenv


class LineNotifier:
    """LINE Notify APIを使用した通知機能"""
    
    def __init__(self):
        # 環境変数を読み込み
        load_dotenv()
        self.token = os.getenv('LINE_NOTIFY_TOKEN')
        self.api_url = 'https://notify-api.line.me/api/notify'
        
        if not self.token or self.token == 'your_line_notify_token_here':
            print("警告: LINE_NOTIFY_TOKENが設定されていません。.envファイルを確認してください。")
    
    def send_message(self, message: str) -> bool:
        """LINE Notifyでメッセージを送信"""
        if not self.token or self.token == 'your_line_notify_token_here':
            print(f"[LINE通知（テスト）] {message}")
            return False
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'message': message
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, data=data)
            
            if response.status_code == 200:
                print("LINE通知送信成功")
                return True
            else:
                print(f"LINE通知送信失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"LINE通知エラー: {e}")
            return False
    
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
        """LINE Notify接続テスト"""
        test_message = "🔔 SmartKabuka接続テスト"
        return self.send_message(test_message)


def main():
    """テスト用のメイン関数"""
    notifier = LineNotifier()
    
    print("=== LINE Notify接続テスト ===")
    success = notifier.test_connection()
    
    if success:
        print("✅ LINE通知が正常に送信されました")
    else:
        print("❌ LINE通知の送信に失敗しました")
        print("💡 .envファイルのLINE_NOTIFY_TOKENを確認してください")
        print("💡 LINE Notifyトークンの取得方法:")
        print("   1. https://notify-bot.line.me/ にアクセス")
        print("   2. 「ログイン」→「マイページ」→「トークンを発行する」")
        print("   3. 通知を送りたいトークルームを選択してトークン発行")


if __name__ == "__main__":
    main()