# ==========================================================
# ARBITRAGE DETECTOR - IBAPI + ALPACA REST API
# ==========================================================

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
import os


class IBController(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, self)
        self.connected = False
        self.nextOrderId = None
        self.market_data = {}
        self.symbol_to_reqid = {}
        self.current_req_id = 1
    
    def get_next_req_id(self):
        req_id = self.current_req_id
        self.current_req_id += 1
        return req_id
    
    def connect_to_ib(self, host="127.0.0.1", port=7497, client_id=0):
        if not self.connected:
            print(f"[IB] Connecting to {host}:{port}...")
            self.connect(host, port, client_id)
            thread = threading.Thread(target=self.run, daemon=True)
            thread.start()
            time.sleep(2)
            self.connected = True
            print("[IB] Connected!")
    
    def disconnect_from_ib(self):
        if self.connected:
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
        
        self.reqMarketDataType(3)
        self.reqMktData(req_id, contract, "", False, False, [])
        time.sleep(0.5)
        return req_id
    
    def get_quote(self, symbol):
        req_id = self.symbol_to_reqid.get(symbol)
        if req_id and req_id in self.market_data:
            data = self.market_data[req_id]
            return {
                'bid': data.get('bid'),
                'ask': data.get('ask'),
                'last': data.get('last'),
                'timestamp': data.get('timestamp')
            }
        return None
    
    def unsubscribe_market_data(self, symbol):
        if symbol in self.symbol_to_reqid:
            req_id = self.symbol_to_reqid[symbol]
            self.cancelMktData(req_id)
    
    def nextValidId(self, orderId: int):
        self.nextOrderId = orderId
    
    def error(self, reqId, errorTime, errorCode, errorString, advancedOrderRejectJson=""):
        if errorCode not in [2104, 2106, 2158, 2119]:
            print(f"[IB Error] {errorCode}: {errorString}")
    
    def tickPrice(self, reqId, tickType, price, attrib):            # delayed tick prices
        tick_types = {66: 'bid', 67: 'ask', 68: 'last'}
        if tickType in tick_types and reqId in self.market_data:
            self.market_data[reqId][tick_types[tickType]] = price
            self.market_data[reqId]['timestamp'] = datetime.now()
    
    def tickSize(self, reqId, tickType, size):
        tick_types ={                       #delayed tick sizes
            69: 'bid_size',
            70: 'ask_size',
            71: 'last_size',
            74: 'volume'
        }
        if tickType in tick_types and reqId in self.market_data:
            self.market_data[reqId][tick_types[tickType]] = size


class AlpacaClient:
    def __init__(self, api_key, api_secret, base_url="https://paper-api.alpaca.markets"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": api_secret
        }
        print("[Alpaca] Client initialized")
    
    def test_connection(self):
        try:
            response = requests.get(f"{self.base_url}/v2/account", headers=self.headers, timeout=5)
            if response.status_code == 200:
                print("[Alpaca] Connection successful!")
                return True
            else:
                print(f"[Alpaca] Connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[Alpaca] Connection error: {e}")
            return False
    
    def get_quote(self, symbol):
        try:
            url = f"{self.base_url}/v2/stocks/{symbol}/quotes/latest"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                quote = data.get('quote', {})
                return {
                    'bid': quote.get('bp'),
                    'ask': quote.get('ap'),
                    'last': None,
                    'timestamp': datetime.now()
                }
            return None
        except Exception as e:
            print(f"[Alpaca] Error fetching {symbol}: {e}")
            return None
    
    def get_latest_trade(self, symbol):
        try:
            url = f"{self.base_url}/v2/stocks/{symbol}/trades/latest"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                trade = data.get('trade', {})
                return {
                    'price': trade.get('p'),
                    'timestamp': trade.get('t')
                }
            return None
        except Exception as e:
            print(f"[Alpaca] Error fetching trade for {symbol}: {e}")
            return None


class ArbitrageDetector:
    def __init__(self, ib_controller, alpaca_client, min_profit_pct=0.1, 
                 trade_size=100, ib_fee_per_share=0.005, alpaca_fee_per_share=0.0):
        self.ib = ib_controller
        self.alpaca = alpaca_client
        self.min_profit_pct = min_profit_pct
        self.trade_size = trade_size
        self.ib_fee_per_share = ib_fee_per_share
        self.alpaca_fee_per_share = alpaca_fee_per_share
        self.opportunities = []
        self.symbols_tracking = set()
        
        print(f"[ArbitrageDetector] Initialized (min profit: {min_profit_pct}%)")
    
    def add_symbol(self, symbol):
        self.ib.subscribe_market_data(symbol)
        self.symbols_tracking.add(symbol)
        time.sleep(0.5)
    
    def remove_symbol(self, symbol):
        self.ib.unsubscribe_market_data(symbol)
        self.symbols_tracking.discard(symbol)
    
    def calculate_profit(self, buy_price, sell_price, buy_platform, sell_platform):
        gross_profit_per_share = sell_price - buy_price
        
        buy_fee = self.ib_fee_per_share if buy_platform == 'IB' else self.alpaca_fee_per_share
        sell_fee = self.ib_fee_per_share if sell_platform == 'IB' else self.alpaca_fee_per_share
        
        total_fees_per_share = buy_fee + sell_fee
        net_profit_per_share = gross_profit_per_share - total_fees_per_share
        total_net_profit = net_profit_per_share * self.trade_size
        profit_pct = (net_profit_per_share / buy_price) * 100
        
        return {
            'gross_profit': gross_profit_per_share * self.trade_size,
            'fees': total_fees_per_share * self.trade_size,
            'net_profit': total_net_profit,
            'profit_pct': profit_pct
        }
    
    def scan_symbol(self, symbol):
        ib_quote = self.ib.get_quote(symbol)
        alpaca_quote = self.alpaca.get_quote(symbol)
        
        if not ib_quote or not alpaca_quote:
            return None
        
        ib_bid = ib_quote.get('bid')
        ib_ask = ib_quote.get('ask')
        alpaca_bid = alpaca_quote.get('bid')
        alpaca_ask = alpaca_quote.get('ask')
        
        if not all([ib_bid, ib_ask, alpaca_bid, alpaca_ask]):
            return None
        
        # Check arbitrage: Buy on IB, Sell on Alpaca
        profit1 = self.calculate_profit(ib_ask, alpaca_bid, 'IB', 'Alpaca')
        
        # Check arbitrage: Buy on Alpaca, Sell on IB
        profit2 = self.calculate_profit(alpaca_ask, ib_bid, 'Alpaca', 'IB')
        
        best_profit = max(profit1['profit_pct'], profit2['profit_pct'])
        
        if best_profit >= self.min_profit_pct:
            if profit1['profit_pct'] > profit2['profit_pct']:
                opportunity = {
                    'symbol': symbol,
                    'buy_platform': 'IB',
                    'sell_platform': 'Alpaca',
                    'buy_price': ib_ask,
                    'sell_price': alpaca_bid,
                    'profit': profit1,
                    'timestamp': datetime.now()
                }
            else:
                opportunity = {
                    'symbol': symbol,
                    'buy_platform': 'Alpaca',
                    'sell_platform': 'IB',
                    'buy_price': alpaca_ask,
                    'sell_price': ib_bid,
                    'profit': profit2,
                    'timestamp': datetime.now()
                }
            
            self.opportunities.append(opportunity)
            return opportunity
        
        return None
    
    def scan_all_symbols(self):
        opportunities = []
        for symbol in self.symbols_tracking:
            opp = self.scan_symbol(symbol)
            if opp:
                opportunities.append(opp)
        return opportunities
    
    def display_opportunity(self, opp):
        print("\n" + "!"*80)
        print("🚨 ARBITRAGE OPPORTUNITY DETECTED! 🚨")
        print("!"*80)
        print(f"Symbol:        {opp['symbol']}")
        print(f"Buy on:        {opp['buy_platform']} @ ${opp['buy_price']:.2f}")
        print(f"Sell on:       {opp['sell_platform']} @ ${opp['sell_price']:.2f}")
        print(f"Gross Profit:  ${opp['profit']['gross_profit']:.2f}")
        print(f"Fees:          ${opp['profit']['fees']:.2f}")
        print(f"Net Profit:    ${opp['profit']['net_profit']:.2f}")
        print(f"Profit %:      {opp['profit']['profit_pct']:.3f}%")
        print(f"Trade Size:    {self.trade_size} shares")
        print(f"Timestamp:     {opp['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("!"*80 + "\n")
    
    def log_opportunity(self, opp, filename="arbitrage_log.txt"):
        with open(filename, 'a') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Arbitrage Opportunity - {opp['timestamp']}\n")
            f.write(f"Symbol: {opp['symbol']}\n")
            f.write(f"Buy: {opp['buy_platform']} @ ${opp['buy_price']:.2f}\n")
            f.write(f"Sell: {opp['sell_platform']} @ ${opp['sell_price']:.2f}\n")
            f.write(f"Net Profit: ${opp['profit']['net_profit']:.2f} ({opp['profit']['profit_pct']:.3f}%)\n")
    
    def get_statistics(self):
        if not self.opportunities:
            return {'total_opportunities': 0, 'average_profit_pct': 0, 'best_opportunity': None}
        
        avg_profit = sum(o['profit']['profit_pct'] for o in self.opportunities) / len(self.opportunities)
        best_opp = max(self.opportunities, key=lambda x: x['profit']['profit_pct'])
        
        return {
            'total_opportunities': len(self.opportunities),
            'average_profit_pct': avg_profit,
            'best_opportunity': best_opp
        }


def main():
    print("\n" + "="*80)
    print("SOLUTION: ARBITRAGE DETECTOR")
    print("="*80)
    
    # IMPORTANT: Replace with your Alpaca credentials
    load_dotenv()
    ALPACA_API_KEY = os.getenv("API_KEY")
    ALPACA_API_SECRET = os.getenv("API_SECRET")
    
    # Create IB Controller
    ib = IBController()
    ib.connect_to_ib(host="127.0.0.1", port=7497, client_id=0)
    
    # Create Alpaca Client
    alpaca = AlpacaClient(ALPACA_API_KEY, ALPACA_API_SECRET)
    
    if not alpaca.test_connection():
        print("[Main] Failed to connect to Alpaca. Check credentials.")
        ib.disconnect_from_ib()
        return
    
    # Create Arbitrage Detector
    detector = ArbitrageDetector(ib, alpaca, min_profit_pct=0.1, trade_size=100)
    
    # Add symbols
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    print(f"\n[Main] Adding symbols: {symbols}")
    for symbol in symbols:
        detector.add_symbol(symbol)
    
    print("\n[Main] Scanning for arbitrage opportunities...")
    time.sleep(3)  # Wait for data
    
    # Scan for 60 seconds
    for i in range(12):
        print(f"\n[Main] Scan {i+1}/12...")
        opportunities = detector.scan_all_symbols()
        
        if opportunities:
            for opp in opportunities:
                detector.display_opportunity(opp)
                detector.log_opportunity(opp)
        else:
            print("[Main] No arbitrage opportunities found in this scan.")
        
        time.sleep(5)
    
    # Display statistics
    stats = detector.get_statistics()
    print("\n" + "="*80)
    print("ARBITRAGE STATISTICS")
    print("="*80)
    print(f"Total Opportunities:  {stats['total_opportunities']}")
    print(f"Average Profit %:     {stats['average_profit_pct']:.3f}%")
    if stats['best_opportunity']:
        best = stats['best_opportunity']
        print(f"Best Opportunity:     {best['symbol']} - {best['profit']['profit_pct']:.3f}%")
    print("="*80 + "\n")
    
    # Cleanup
    for symbol in symbols:
        detector.remove_symbol(symbol)
    ib.disconnect_from_ib()
    
    print("[Main] Arbitrage scanning completed!")


if __name__ == "__main__":
    main()

