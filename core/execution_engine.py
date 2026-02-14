
import logging
log = logging.getLogger("GENIUS")
def execute_order_safe(exchange, symbol, side, amount):
    try:
        order = exchange.create_market_order(symbol=symbol, side=side.lower(), amount=amount)
        log.info(f"ORDER_OK | {symbol} {side} {amount}")
        return True, order
    except Exception as e:
        log.error(f"ORDER_FAIL | {e}")
        return False, str(e)
