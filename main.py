
import os, time, logging
from core.excel_reader import ExcelReader
from core.decision_engine import build_trade_decision
from core.execution_engine import execute_order_safe
from core.safety_guard import is_system_healthy, is_risk_unlocked
from adapters.virtual_wallet import VirtualWallet

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("GENIUS")

EXCEL_PATH = os.getenv("EXCEL_PATH","DYZEN_CAPITAL_OS_AI_LIVE_CORE_READY_HARDENED.xlsx")
AUTO_TRADING = True
BOT_SYMBOLS = ["BTC/USDT"]
BOT_QUOTE_PER_TRADE = 10

def main_loop():
    reader = ExcelReader(EXCEL_PATH)
    exchange = VirtualWallet()

    while True:
        master = reader.read_decision()
        hb = reader.read_heartbeat()
        risk = reader.read_risk_lock()

        if not is_system_healthy(hb) or not is_risk_unlocked(risk):
            action="HOLD"
        else:
            decision = build_trade_decision(master)
            action = decision["action"]

        if action in ("BUY","SELL") and AUTO_TRADING:
            for sym in BOT_SYMBOLS:
                amount = 0.001
                ok,res = execute_order_safe(exchange,sym,action,amount)
                log.info(f"EXEC_RESULT | {ok} {res}")
        else:
            log.info(f"HOLD | action={action}")

        time.sleep(10)

if __name__ == "__main__":
    main_loop()
