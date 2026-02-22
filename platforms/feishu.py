import requests
import json
from config import settings

class FeishuBot:
    def __init__(self):
        self.app_id = settings.FEISHU_APP_ID
        self.app_secret = settings.FEISHU_APP_SECRET
        self._tenant_access_token = None

    def _get_token(self):
        # In production, cache this token until expiry
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        resp = requests.post(url, json=payload).json()
        return resp.get("tenant_access_token")

    def send_message(self, receive_id: str, text: str, receive_id_type="open_id"):
        token = self._get_token()
        url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
        headers = {"Authorization": f"Bearer {token}"}
        content = json.dumps({"text": text})
        payload = {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": content
        }
        requests.post(url, headers=headers, json=payload)

    def send_approval_card(self, receive_id: str, plan: list[str], receive_id_type="open_id"):
        """
        Sends a Feishu Interactive Card.
        """
        token = self._get_token()
        url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Build Plan Text
        plan_str = "\n".join(f"{i+1}. {task}" for i, task in enumerate(plan))
        
        card_content = {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "🤖 Agent Plan Review"}, "template": "blue"},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**Proposed Subtasks:**\n{plan_str}"}},
                {"tag": "action", "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "Approve"},
                        "type": "primary",
                        "value": {"action": "approve"}
                    },
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "Reject"},
                        "type": "danger",
                        "value": {"action": "reject"}
                    }
                ]}
            ]
        }
        
        payload = {
            "receive_id": receive_id,
            "msg_type": "interactive",
            "content": json.dumps(card_content)
        }
        requests.post(url, headers=headers, json=payload)

feishu_bot = FeishuBot()