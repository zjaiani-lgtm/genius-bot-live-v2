import logging

log = logging.getLogger("GENIUS")

VALID_ACTIONS = {"BUY", "SELL", "HOLD"}


def normalize_action(raw) -> str:
    if raw is None:
        return "HOLD"
    a = str(raw).upper().strip()
    if a not in VALID_ACTIONS:
        log.warning(f"ACTION_NORMALIZE_WARN | raw={raw}")
        return "HOLD"
    return a


def build_trade_decision(master_row: dict) -> dict:
    """
    Maps YOUR Excel columns to bot decision.

    Expected columns in sheet AI_MASTER_LIVE_DECISION:
      - "Final Trade Decision"  -> BUY/SELL/HOLD
      - "AI Score"              -> number (can be float)
      - "Macro Gate"            -> BLOCK/ALLOW (BLOCK forces HOLD)
      - optional: "SYMBOL"      -> e.g. BTC/USDT (if exists)

    If "Macro Gate" is BLOCK => action becomes HOLD (safety).
    """

    raw_action = master_row.get("Final Trade Decision")
    action = normalize_action(raw_action)

    macro_gate = str(master_row.get("Macro Gate", "")).upper().strip()
    if macro_gate == "BLOCK":
        action = "HOLD"

    ai_score = master_row.get("AI Score")
    symbol = master_row.get("SYMBOL")  # optional

    return {
        "action": action,
        "SYMBOL": symbol,
        "AI_SCORE": ai_score,
        "MACRO_GATE": macro_gate,
        "RAW_ACTION": raw_action,
    }
