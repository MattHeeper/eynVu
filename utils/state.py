"""
Simple in-memory state management for user conversations
"""

# Store user states
user_states = {}

# State constants
STATE_NONE = "none"
STATE_WAITING_MESSAGE = "waiting_message"
STATE_WAITING_CONFIRMATION = "waiting_confirmation"
STATE_WAITING_REPLY = "waiting_reply"


def set_state(user_id: int, state: str, data: dict = None):
    """Set user state with optional data"""
    user_states[user_id] = {
        "state": state,
        "data": data or {}
    }


def get_state(user_id: int) -> dict:
    """Get user state"""
    return user_states.get(user_id, {"state": STATE_NONE, "data": {}})


def clear_state(user_id: int):
    """Clear user state"""
    if user_id in user_states:
        del user_states[user_id]


def is_in_state(user_id: int, state: str) -> bool:
    """Check if user is in specific state"""
    current = get_state(user_id)
    return current["state"] == state


def get_state_data(user_id: int) -> dict:
    """Get state data"""
    current = get_state(user_id)
    return current.get("data", {})
