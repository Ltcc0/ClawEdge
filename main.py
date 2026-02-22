from fastapi import FastAPI, Request, BackgroundTasks
from schemas import TelegramUpdate, FeishuWebhook
from platforms.telegram import telegram_bot
from platforms.feishu import feishu_bot
from core.agent import agent_brain
from core.state import state_manager
from config import settings
import uvicorn

app = FastAPI()

async def process_user_intent(user_id: str, message: str, platform: str):
    """
    1. Analyze intent via LLM.
    2. Generate subtasks.
    3. Save state.
    4. Ask user for approval.
    """
    # Analyze
    plan = agent_brain.analyze_and_plan(message)
    
    # Save State
    state_manager.set_pending_plan(user_id, plan, message)
    
    # Notify User
    if platform == "telegram":
        telegram_bot.send_approval_request(int(user_id), plan)
    elif platform == "feishu":
        feishu_bot.send_approval_card(user_id, plan)

async def execute_approved_plan(user_id: str, platform: str):
    """
    1. Retrieve plan.
    2. Execute.
    3. Send results.
    """
    state = state_manager.get_state(user_id)
    if not state:
        msg = "Session expired or no plan found."
        if platform == "telegram": telegram_bot.send_message(user_id, msg)
        else: feishu_bot.send_message(user_id, msg)
        return

    # Notify processing
    loading_msg = "🚀 Executing approved plan..."
    if platform == "telegram": telegram_bot.send_message(user_id, loading_msg)
    else: feishu_bot.send_message(user_id, loading_msg)

    # Execute
    result = agent_brain.execute_plan(state["plan"])
    
    # Send Result
    if platform == "telegram": telegram_bot.send_message(user_id, f"✅ **Result:**\n{result}")
    else: feishu_bot.send_message(user_id, f"✅ Result:\n{result}")
    
    # Clear state
    state_manager.clear_state(user_id)

# --- Routes ---

@app.get("/")
def health_check():
    return {"status": "running", "system": "Agent Sentinel"}

# --- Telegram Webhook ---

@app.post("/webhook/telegram")
async def telegram_webhook(update: TelegramUpdate, background_tasks: BackgroundTasks):
    # Case 1: Callback Query (User clicked a button)
    if update.callback_query:
        cb = update.callback_query
        user_id = str(cb['from']['id'])
        data = cb.get('data')
        
        if data == "approve":
            background_tasks.add_task(execute_approved_plan, user_id, "telegram")
        elif data == "reject":
            telegram_bot.send_message(user_id, "🚫 Operation cancelled.")
            state_manager.clear_state(user_id)
            
        # Acknowledge callback (optional but recommended in real Telegram bots)
        return {"status": "ok"}

    # Case 2: Standard Message
    if update.message and 'text' in update.message:
        user_id = str(update.message['chat']['id'])
        text = update.message['text']
        
        # Async processing so we don't block the webhook
        background_tasks.add_task(process_user_intent, user_id, text, "telegram")

    return {"status": "ok"}

# --- Feishu Webhook ---

@app.post("/webhook/feishu")
async def feishu_webhook(request: Request, background_tasks: BackgroundTasks):
    # Feishu sends raw JSON that might not perfectly match strict schemas immediately due to encryption (ignored here)
    body = await request.json()
    
    # 1. URL Verification Challenge
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}
        
    # 2. Event Handling
    if "header" in body and body["header"]["event_type"] == "im.message.receive_v1":
        event = body["event"]
        message = event["message"]
        
        # Ignore bot's own messages to prevent loops
        # (Feishu usually filters this, but good practice)
        
        if message["message_type"] == "text":
            user_id = event["sender"]["sender_id"]["open_id"]
            content = json.loads(message["content"])
            text = content["text"]
            
            background_tasks.add_task(process_user_intent, user_id, text, "feishu")
            
    # 3. Card Action (Button Click)
    if "action" in body:
        # Feishu card actions have a different structure
        user_id = body["open_id"]
        action_value = body["action"].get("value", {})
        
        if action_value.get("action") == "approve":
             background_tasks.add_task(execute_approved_plan, user_id, "feishu")
        elif action_value.get("action") == "reject":
             feishu_bot.send_message(user_id, "🚫 Operation cancelled.")
             state_manager.clear_state(user_id)

    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)