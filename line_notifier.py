import os
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

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
        
        if not self.token or not self.user_id:
            print("警告: LINE_MESSAGING_API_TOKENまたはLINE_USER_IDが設定されていません。")
            self.line_bot_api = None
        else:
            self.line_bot_api = LineBotApi(self.token)
    
    def send_message(self, message: str) -> bool:
        """LINE Messaging APIでメッセージを送信"""
        if not self.line_bot_api:
            print(f"[LINE通知（テスト）] {message}")
            return False
        
        try:
            self.line_bot_api.push_message(
                to=self.user_id,
                messages=TextSendMessage(text=message)
            )
            print("LINE通知送信成功")
            return True
            
        except LineBotApiError as e:
            print(f"LINE API エラー: {e.status_code} - {e.error.message}")
            return False
        except Exception as e:
            print(f"LINE通知送信エラー: {e}")
            return False
    
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