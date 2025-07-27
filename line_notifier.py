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

    def send_message(self, message: str, isbroadcast: bool = False) -> bool:
        """LINE Messaging APIでメッセージを送信"""
        if not self.line_bot_api:
            print(f"[LINE通知（テスト）] {message}")
            return False
        
        try:
            if isbroadcast:
                # ブロードキャストメッセージ
                self.line_bot_api.broadcast(TextSendMessage(text=message))
                print("LINEブロードキャスト通知送信成功")
            else:
                # 個別メッセージ
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
    
    def get_usage(self) -> str:
        """LINE Messaging APIのメッセージ利用情報を取得"""
        
        try:
            quota = self.line_bot_api.get_message_quota()
            consumption = self.line_bot_api.get_message_quota_consumption()
            message = f"上限:{quota.value} - 使用済み:{consumption.total_usage}"
            print(message)
            return message
        except LineBotApiError as e:
            print(f"LINE API エラー: {e.status_code} - {e.error.message}")
            return None
        except Exception as e:
            print(f"メッセージ利用情報取得エラー: {e}")
            return None

    def test_connection(self) -> bool:
        """LINE Messaging API接続テスト"""
        unicast_result = self.send_message("unicast test", isbroadcast=False)
        broadcast_result = self.send_message("broadcast test", isbroadcast=True)
        return unicast_result or broadcast_result


def main():
    """テスト用のメイン関数"""
    notifier = LineNotifier()
    
    print("=== LINE Messaging API接続テスト ===")
    notifier.get_usage()
    success = notifier.test_connection()
    
    if success:
        print("✅ LINE通知が正常に送信されました")
    else:
        print("❌ LINE通知の送信に失敗しました")


if __name__ == "__main__":
    main()