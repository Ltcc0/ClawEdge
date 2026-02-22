from pydantic import BaseModel
from typing import Optional, List, Any, Dict

# Telegram Webhook Schema (Simplified)
class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None

# Feishu Webhook Schema
class FeishuHeader(BaseModel):
    event_id: str
    event_type: str
    token: str

class FeishuEvent(BaseModel):
    message: Optional[Dict[str, Any]] = None
    sender: Optional[Dict[str, Any]] = None

class FeishuWebhook(BaseModel):
    schema_v: Optional[str] = None  # Field name is actually 'schema' but protected in pydantic
    header: Optional[FeishuHeader] = None
    event: Optional[FeishuEvent] = None
    type: Optional[str] = None      # For url_verification
    challenge: Optional[str] = None # For url_verification
    token: Optional[str] = None     # For url_verification