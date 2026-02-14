
class VirtualWallet:
    def create_market_order(self, symbol, side, amount):
        return {"symbol":symbol,"side":side,"amount":amount,"mode":"paper"}
