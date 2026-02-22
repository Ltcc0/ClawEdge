from typing import Dict, List

class StateManager:
    """
    Manages the context of user interactions.
    Key: user_id (or chat_id)
    Value: Dict containing the current plan and status.
    """
    def __init__(self):
        self._store: Dict[str, Dict] = {}

    def set_pending_plan(self, user_id: str, plan: List[str], original_query: str):
        self._store[user_id] = {
            "status": "PENDING_APPROVAL",
            "plan": plan,
            "query": original_query
        }

    def get_state(self, user_id: str):
        return self._store.get(user_id)

    def clear_state(self, user_id: str):
        if user_id in self._store:
            del self._store[user_id]

# Singleton instance
state_manager = StateManager()