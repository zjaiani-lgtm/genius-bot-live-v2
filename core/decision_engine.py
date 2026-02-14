
import logging
log = logging.getLogger("GENIUS")
VALID_ACTIONS = {"BUY","SELL","HOLD"}
def normalize_action(raw):
    if not raw:
        return "HOLD"
    a = str(raw).upper().strip()
    if a not in VALID_ACTIONS:
        log.warning(f"ACTION_NORMALIZE_WARN | {raw}")
        return "HOLD"
    return a
def build_trade_decision(master_row: dict) -> dict:
    action = normalize_action(master_row.get("FINAL_ACTION"))
    return {
        "action": action,
        "SYMBOL": master_row.get("SYMBOL"),
        "AI_SCORE": master_row.get("FINAL_AI_SCORE"),
    }
