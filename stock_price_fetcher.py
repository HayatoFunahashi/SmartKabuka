import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import time


class StockPriceFetcher:
    """Yahoo Finance APIを使って株価情報を取得するクラス"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5分間キャッシュ
    
    def _get_yahoo_symbol(self, code: str, market: str = "JP") -> str:
        """株式コードをYahoo Finance形式に変換"""
        if market == "JP":
            return f"{code}.T"  # 日本株
        elif market == "US":
            return code  # 米国株はそのまま（例：AAPL, GOOGL）
        else:
            return code
    
    def get_current_price(self, code: str, market: str = "JP") -> Optional[Dict]:
        """単一銘柄の現在価格を取得"""
        yahoo_symbol = self._get_yahoo_symbol(code, market)
        
        # キャッシュチェック
        cache_key = f"current_{market}_{code}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        try:
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            
            if 'currentPrice' not in info and 'regularMarketPrice' not in info:
                print(f"価格情報が取得できませんでした: {code}")
                return None
            
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            previous_close = info.get('previousClose', info.get('regularMarketPreviousClose', 0))
            
            # 前日比を計算
            price_change = current_price - previous_close if previous_close else 0
            price_change_pct = (price_change / previous_close * 100) if previous_close else 0
            
            result = {
                'code': code,
                'symbol': yahoo_symbol,
                'market': market,
                'current_price': current_price,
                'previous_close': previous_close,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'market_cap': info.get('marketCap'),
                'volume': info.get('volume', info.get('regularMarketVolume')),
                'currency': info.get('currency', 'JPY' if market == 'JP' else 'USD'),
                'last_update': datetime.now().isoformat()
            }
            
            # キャッシュに保存
            self.cache[cache_key] = (result, time.time())
            
            return result
            
        except Exception as e:
            print(f"株価取得エラー ({code}): {e}")
            return None
    
    def get_multiple_prices(self, codes: List[str], market: str = "JP", delay: float = 0.5) -> Dict[str, Dict]:
        """複数銘柄の現在価格を取得（レート制限対応）"""
        results = {}
        
        for i, code in enumerate(codes):
            print(f"株価取得中... ({i+1}/{len(codes)}) {code} ({market})")
            price_data = self.get_current_price(code, market)
            
            if price_data:
                results[code] = price_data
            
            # API制限回避のための待機
            if i < len(codes) - 1:
                time.sleep(delay)
        
        return results
    
    def get_historical_data(self, code: str, market: str = "JP", period: str = "1mo") -> Optional[pd.DataFrame]:
        """過去の株価データを取得"""
        yahoo_symbol = self._get_yahoo_symbol(code, market)
        
        try:
            ticker = yf.Ticker(yahoo_symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                print(f"履歴データが取得できませんでした: {code}")
                return None
            
            # 日本語カラム名に変更
            hist = hist.rename(columns={
                'Open': '始値',
                'High': '高値', 
                'Low': '安値',
                'Close': '終値',
                'Volume': '出来高'
            })
            
            hist['銘柄コード'] = code
            
            return hist
            
        except Exception as e:
            print(f"履歴データ取得エラー ({code}): {e}")
            return None
    
    def get_company_info(self, code: str, market: str = "JP") -> Optional[Dict]:
        """企業情報を取得"""
        yahoo_symbol = self._get_yahoo_symbol(code, market)
        
        # キャッシュチェック
        cache_key = f"info_{market}_{code}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 3600:  # 1時間キャッシュ
                return cached_data
        
        try:
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            
            result = {
                'code': code,
                'name': info.get('longName', info.get('shortName', '')),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap'),
                'employees': info.get('fullTimeEmployees'),
                'website': info.get('website', ''),
                'business_summary': info.get('businessSummary', ''),
                'pe_ratio': info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'last_update': datetime.now().isoformat()
            }
            
            # キャッシュに保存
            self.cache[cache_key] = (result, time.time())
            
            return result
            
        except Exception as e:
            print(f"企業情報取得エラー ({code}): {e}")
            return None
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self.cache.clear()


def main():
    """テスト用のメイン関数"""
    from libs.jp_stock_data import JPStockData
    from libs.us_stock_data import USStockData
    
    # 保有銘柄を取得
    stock_data = JPStockData('input/data.csv')
    codes = stock_data.get_stock_codes()
    
    print(f"=== 保有銘柄の株価取得テスト ===")
    print(f"対象銘柄: {codes}")
    
    fetcher = StockPriceFetcher()
    
    # 複数銘柄の現在価格を取得
    print("\n=== 現在価格取得 ===")
    prices = fetcher.get_multiple_prices(codes)
    
    for code, data in prices.items():
        if data:
            print(f"{code}: {data['current_price']:.2f}円 "
                  f"(前日比: {data['price_change']:+.2f}円 / {data['price_change_pct']:+.2f}%)")
    
    # 企業情報取得のテスト（最初の銘柄のみ）
    if codes:
        test_code = codes[0]
        print(f"\n=== 企業情報取得テスト ({test_code}) ===")
        company_info = fetcher.get_company_info(test_code)
        if company_info:
            print(f"企業名: {company_info['name']}")
            print(f"セクター: {company_info['sector']}")
            print(f"業界: {company_info['industry']}")
            print(f"時価総額: {company_info['market_cap']:,}円" if company_info['market_cap'] else "時価総額: N/A")
            print(f"PER: {company_info['pe_ratio']}" if company_info['pe_ratio'] else "PER: N/A")
    
    # 履歴データ取得のテスト（最初の銘柄のみ）
    if codes:
        test_code = codes[0]
        print(f"\n=== 履歴データ取得テスト ({test_code}) ===")
        hist_data = fetcher.get_historical_data(test_code, period="5d")
        if hist_data is not None:
            print(f"過去5日間のデータ:")
            print(hist_data[['始値', '高値', '安値', '終値', '出来高']].tail())


if __name__ == "__main__":
    main()