# ==========================================================
# PORTFOLIO MONITOR WITH IBAPI
# ==========================================================

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time


class Controller(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, self)
        self.connected = False
        self.nextOrderId = None
        self.account_summary = {}
        self.portfolio_positions = []
        
    def connect_to_ib(self, host="127.0.0.1", port=7497, client_id=0):
        if not self.connected:
            print(f"[Controller] Connecting to IB at {host}:{port}...")
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
    
    def request_account_summary(self):
        if not self.connected:
            print("[Controller] Not connected!")
            return
        
        req_id = 9001
        print("[Controller] Requesting account summary...")
        self.reqAccountSummary(req_id, "All", "NetLiquidation,TotalCashValue,BuyingPower,GrossPositionValue")
        time.sleep(2)
        return self.account_summary
    
    def request_positions(self):
        if not self.connected:
            print("[Controller] Not connected!")
            return
        
        print("[Controller] Requesting positions...")
        self.portfolio_positions = []
        self.reqPositions()
        time.sleep(2)
        return self.portfolio_positions
    
    def cancel_account_summary(self, req_id):
        self.cancelAccountSummary(req_id)
    
    def nextValidId(self, orderId: int):
        print(f"[IB] Connected! Next order ID: {orderId}")
        self.nextOrderId = orderId
    
    def error(self, reqId, errorTime, errorCode, errorString, advancedOrderRejectJson=""):
        print(f"[IB Error] {errorCode}: {errorString}")
    
    def accountSummary(self, reqId, account, tag, value, currency):
        print(f"[IB] {tag}: {value} {currency}")
        self.account_summary[tag] = {'value': float(value), 'currency': currency}
    
    def accountSummaryEnd(self, reqId):
        print("[IB] Account summary complete")
    
    def position(self, account, contract, position, avgCost):
        position_data = {
            'symbol': contract.symbol,
            'secType': contract.secType,
            'position': position,
            'avgCost': avgCost,
            'marketValue': position * avgCost
        }
        print(f"[IB] Position - {contract.symbol}: {position} @ ${avgCost:.2f}")
        self.portfolio_positions.append(position_data)
    
    def positionEnd(self):
        print("[IB] Positions complete")


class PortfolioMonitor:
    def __init__(self, controller):
        self.controller = controller
        self.account_data = {}
        self.positions = []
        print("\n[PortfolioMonitor] Initialized")
    
    def fetch_account_data(self):
        print("\n[PortfolioMonitor] Fetching account data...")
        self.account_data = self.controller.request_account_summary()
        return self.account_data
    
    def fetch_positions(self):
        print("\n[PortfolioMonitor] Fetching positions...")
        self.positions = self.controller.request_positions()
        return self.positions
    
    def display_portfolio_summary(self):
        print("\n" + "="*60)
        print("PORTFOLIO SUMMARY")
        print("="*60)
        
        for tag, data in self.account_data.items():
            print(f"{tag:25s}: ${data['value']:,.2f} {data['currency']}")
        
        print("\n" + "-"*60)
        print("CURRENT POSITIONS")
        print("-"*60)
        print(f"{'Symbol':<10} {'Shares':>10} {'Avg Cost':>12} {'Market Value':>15}")
        print("-"*60)
        
        for pos in self.positions:
            print(f"{pos['symbol']:<10} {pos['position']:>10.0f} ${pos['avgCost']:>11.2f} ${pos['marketValue']:>14,.2f}")
        
        print("="*60 + "\n")
    
    def calculate_total_portfolio_value(self):
        total_value = sum(pos['marketValue'] for pos in self.positions)
        return total_value


def main():
    print("\n" + "="*60)
    print("SOLUTION: PORTFOLIO MONITOR")
    print("="*60)
    
    controller = Controller()
    controller.connect_to_ib(host="127.0.0.1", port=7497, client_id=0)
    
    monitor = PortfolioMonitor(controller)
    monitor.fetch_account_data()
    monitor.fetch_positions()
    monitor.display_portfolio_summary()
    
    total_value = monitor.calculate_total_portfolio_value()
    print(f"[Main] Total Portfolio Value: ${total_value:,.2f}\n")
    
    controller.cancel_account_summary(9001)
    controller.disconnect_from_ib()
    print("[Main] Completed!")


if __name__ == "__main__":
    main()

