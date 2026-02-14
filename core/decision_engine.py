import logging
import math

log = logging.getLogger("GENIUS")

VALID_ACTIONS = {"BUY", "SELL", "HOLD"}

# Macro Gate accepted values (make it tolerant)
ALLOW_VALUES = {"ALLOW", "OK", "OPEN", "YES", "TRUE", "1", "GO", "RUN", "PASS"}
BLOCK_VALUES = {"BLOCK", "NO", "CLOSE", "FALSE", "0", "STOP", "HALT", "DENY"}


def _is_nan(x) -> bool:
    try:
        return isinstance(x, float) and math.isnan(x)
    except Exception:
        return False


def normalize_action(raw) -> str:
    """
    Normalize action from Excel cell.
    - None / NaN / empty -> HOLD
    - Unknown string -> HOLD (and warn)
    """
    if raw is None or _is_nan(raw):
        return "HOLD"

    s = str(raw).strip().upper()

    if s in ("", "NAN", "NONE", "NULL"):
        return "HOLD"

    if s not in VALID_ACTIONS:
        log.warning(f"ACTION_NORMALIZE_WARN | raw={raw}")
        return "HOLD"

    return s


def normalize_gate(raw) -> str:
    """
    Normalize Macro Gate from Excel cell.
    - If gate is in BLOCK_VALUES => "BLOCK"
    - If gate is in ALLOW_VALUES => "ALLOW"
    - Otherwise => "UNKNOWN"
    """
    if raw is None or _is_nan(raw):
        return "UNKNOWN"

    s = str(raw).strip().upper()

    if s in ("", "NAN", "NONE", "NULL"):
        return "UNKNOWN"

    if s in BLOCK_VALUES:
        return "BLOCK"

    if s in ALLOW_VALUES:
        return "ALLOW"

    return "UNKNOWN"


def build_trade_decision(master_row: dict) -> dict:
    """
    Maps YOUR Excel columns to bot decision.

    Expected columns in sheet AI_MASTER_LIVE_DECISION:
      - "Final Trade Decision"  -> BUY/SELL/HOLD (can be empty)
      - "AI Score"              -> number (float/int)
      - "Macro Gate"            -> BLOCK/ALLOW (or OK/YES/OPEN etc.)
      - optional: "SYMBOL"      -> e.g. BTC/USDT (if exists)

    Rules:
      1) Action defaults to HOLD when empty/NaN/unknown.
      2) If Macro Gate is BLOCK => force HOLD.
      3) If Macro Gate is UNKNOWN => safe HOLD (can relax later).
    """

    raw_action = master_row.get("Final Trade Decision")
    action = normalize_action(raw_action)

    raw_gate = master_row.get("Macro Gate")
    gate = normalize_gate(raw_gate)

    # Safety gating
    if gate == "BLOCK":
        action = "HOLD"
    elif gate == "UNKNOWN":
        # Institutional-safe default
        action = "HOLD"

    ai_score = master_row.get("AI Score")
    if _is_nan(ai_score):
        ai_score = None

    symbol = master_row.get("SYMBOL")  # optional

    return {
        "action": action,
        "SYMBOL": symbol,
        "AI_SCORE": ai_score,
        "MACRO_GATE": gate,
        "RAW_ACTION": raw_action,
        "RAW_GATE": raw_gate,
    }
