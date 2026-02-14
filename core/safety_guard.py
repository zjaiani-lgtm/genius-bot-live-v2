
import logging
log = logging.getLogger("GENIUS")
def is_system_healthy(row):
    return str(row.get("GLOBAL_STATUS","")).upper()=="RUN"
def is_risk_unlocked(row):
    return str(row.get("KILL_SWITCH","")).upper()=="OK"
