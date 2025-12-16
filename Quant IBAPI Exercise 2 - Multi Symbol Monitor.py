# ==========================================================
# MULTI-SYMBOL REAL-TIME MONITOR WITH IBAPI
# ==========================================================

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
from datetime import datetime


class Controller(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, self)
        self.connected = False
        self.nextOrderId = None
        self.market_data = {}
        self.symbol_to_reqid = {}
        self.reqid_to_symbol = {}
        self.current_req_id = 1
    
    def get_next_req_id(self):
        req_id = self.current_req_id
        self.current_req_id += 1
        return req_id
    
    def connect_to_ib(self, host="127.0.0.1", port=7497, client_id=1):
        if not self.connected:
            print(f"[Controller] Connecting to {host}:{port}...")
            self.connect(host, port, client_id)
            thread = threading.Thread(target=self.run, daemon=True)
            thread.start()
            time.sleep(2)
            self.connected = True
            print("[Controller] Connected!")
    
    def disconnect_from_ib(self):
        if self.connected:
            print("[Controller] Disconnecting...")
            self.disconnect()
            self.connected = False
    
    def subscribe_market_data(self, symbol, exchange="SMART", sec_type="STK", currency="USD"):
        if not self.connected:
            return None
        
        contract = Contract()
        contract.symbol = symbol
        contract.secType = sec_type
        contract.exchange = exchange
        contract.currency = currency
        
        req_id = self.get_next_req_id()
        self.market_data[req_id] = {'timestamp': datetime.now()}
        self.symbol_to_reqid[symbol] = req_id
        self.reqid_to_symbol[req_id] = symbol
        
        print(f"[Controller] Subscribing to {symbol} (reqId: {req_id})")
        self.reqMarketDataType(3)
        self.reqMktData(req_id, contract, "", False, False, [])
        time.sleep(1)
        return req_id
    
    def unsubscribe_market_data(self, symbol):
        if symbol in self.symbol_to_reqid:
            req_id = self.symbol_to_reqid[symbol]
            self.cancelMktData(req_id)
            del self.symbol_to_reqid[symbol]
            del self.reqid_to_symbol[req_id]
            del self.market_data[req_id]
    
    def get_market_data(self, symbol):
        req_id = self.symbol_to_reqid.get(symbol)
        return self.market_data.get(req_id, {}) if req_id else {}
    
    def nextValidId(self, orderId: int):
        print(f"[IB] Connected! Order ID: {orderId}")
        self.nextOrderId = orderId
    
    def error(self, reqId, errorTime, errorCode, errorString, advancedOrderRejectJson=""):
        if errorCode not in [2104, 2106, 2158]:
            print(f"[IB Error] {errorCode}: {errorString}")
    
    def tickPrice(self, reqId, tickType, price, attrib):
        tick_types = {66: 'bid', 67: 'ask', 68: 'last', 72: 'high', 73: 'low', 75: 'close'} # this is delayed tick prices
        if tickType in tick_types and reqId in self.market_data:
            self.market_data[reqId][tick_types[tickType]] = price
            self.market_data[reqId]['timestamp'] = datetime.now()
    
    def tickSize(self, reqId, tickType, size):
        tick_types = {69: 'bid_size', 70: 'ask_size', 71: 'last_size', 74: 'volume'} # delayed tick sizes
        if tickType in tick_types and reqId in self.market_data:
            self.market_data[reqId][tick_types[tickType]] = size


class SymbolTracker:
    def __init__(self, symbol, controller, alert_threshold_pct=2.0):
        self.symbol = symbol
        self.controller = controller
        self.alert_threshold_pct = alert_threshold_pct
        self.req_id = None
        self.initial_price = None
        self.last_price = None
        self.high_price = None
        self.low_price = None
        self.price_change = 0
        self.price_change_pct = 0
        self.alerts_triggered = []
    
    def start_tracking(self):
        self.req_id = self.controller.subscribe_market_data(self.symbol)
        time.sleep(1)
        self.update()
        if self.last_price:
            self.initial_price = self.last_price
            self.high_price = self.last_price
            self.low_price = self.last_price
    
    def update(self):
        data = self.controller.get_market_data(self.symbol)
        if data.get('last'):
            self.last_price = data['last']
            
            if self.initial_price:
                self.price_change = self.last_price - self.initial_price
                self.price_change_pct = (self.price_change / self.initial_price) * 100
                
                if self.high_price is None or self.last_price > self.high_price:
                    self.high_price = self.last_price
                if self.low_price is None or self.last_price < self.low_price:
                    self.low_price = self.last_price
                
                self.check_alerts()
    
    def check_alerts(self):
        if abs(self.price_change_pct) >= self.alert_threshold_pct:
            alert_msg = f"🚨 {self.symbol}: {self.price_change_pct:+.2f}% move!"
            if alert_msg not in self.alerts_triggered:
                self.alerts_triggered.append(alert_msg)
                return True
        return False
    
    def get_status(self):
        if not self.last_price:
            return f"{self.symbol:8s}: Waiting for data..."
        
        change_str = f"{self.price_change:+.2f}" if self.price_change else "0.00"
        pct_str = f"({self.price_change_pct:+.2f}%)" if self.price_change_pct else "(0.00%)"
        alert_str = " ⚠️ ALERT" if self.alerts_triggered else ""
        
        return f"{self.symbol:8s}: ${self.last_price:7.2f} {change_str:>7s} {pct_str:>9s} | H:${self.high_price:7.2f} L:${self.low_price:7.2f}{alert_str}"
    
    def stop_tracking(self):
        self.controller.unsubscribe_market_data(self.symbol)


class WatchlistMonitor:
    def __init__(self, controller, alert_threshold_pct=2.0):
        self.controller = controller
        self.alert_threshold_pct = alert_threshold_pct
        self.trackers = {}
    
    def add_symbol(self, symbol):
        print(f"[WatchlistMonitor] Adding {symbol}...")
        tracker = SymbolTracker(symbol, self.controller, self.alert_threshold_pct)
        tracker.start_tracking()
        self.trackers[symbol] = tracker
    
    def remove_symbol(self, symbol):
        if symbol in self.trackers:
            self.trackers[symbol].stop_tracking()
            del self.trackers[symbol]
    
    def update_all(self):
        for tracker in self.trackers.values():
            tracker.update()
    
    def display_watchlist(self):
        print("\n" + "="*80)
        print(f"WATCHLIST - {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)
        for tracker in self.trackers.values():
            print(tracker.get_status())
        print("="*80)
    
    def get_alerts(self):
        alerts = []
        for tracker in self.trackers.values():
            alerts.extend(tracker.alerts_triggered)
        return alerts
    
    def stop_all(self):
        for symbol in list(self.trackers.keys()):
            self.remove_symbol(symbol)


def main():
    print("\n" + "="*80)
    print("SOLUTION: MULTI-SYMBOL MONITOR")
    print("="*80)
    
    controller = Controller()
    controller.connect_to_ib(host="127.0.0.1", port=7497, client_id=2)
    
    monitor = WatchlistMonitor(controller, alert_threshold_pct=1.5)
    
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    for symbol in symbols:
        monitor.add_symbol(symbol)
    
    print("\n[Main] Monitoring for 30 seconds...")
    for i in range(15):
        time.sleep(2)
        monitor.update_all()
        monitor.display_watchlist()
        
        alerts = monitor.get_alerts()
        if alerts:
            print("\n🚨 ALERTS:")
            for alert in alerts:
                print(f"  {alert}")
    
    monitor.stop_all()
    controller.disconnect_from_ib()
    print("\n[Main] Completed!")


if __name__ == "__main__":
    main()

