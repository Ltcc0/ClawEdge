import requests
from config import settings

class TelegramBot:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

    def send_message(self, chat_id: int, text: str):
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        requests.post(url, json=payload)

    def send_approval_request(self, chat_id: int, plan: list[str]):
        """
        Sends the plan with Inline Keyboard Buttons for HITL.
        """
        plan_text = "📋 **Agent Plan Proposed:**\n\n" + "\n".join(f"{i+1}. {task}" for i, task in enumerate(plan))
        plan_text += "\n\nDo you approve this execution?"

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve", "callback_data": "approve"},
                    {"text": "❌ Reject", "callback_data": "reject"}
                ]
            ]
        }

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": plan_text, 
            "reply_markup": keyboard,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload)

telegram_bot = TelegramBot()