from typing import Dict, List
from us_csv_parser import USCSVParser


class USStockData:
    """米国株式データを管理するクラス"""
    
    def __init__(self, csv_path: str):
        self.parser = USCSVParser(csv_path)
        self.stock_df = None
        self._load_data()
    
    def _load_data(self):
        """データを読み込み"""
        self.stock_df = self.parser.get_us_stock_holdings()
    
    def get_stock_symbols(self) -> List[str]:
        """保有米国株のシンボルを取得"""
        if self.stock_df.empty:
            return []
        
        return self.stock_df['銘柄シンボル'].tolist()
    
    def get_holdings_summary(self) -> Dict:
        """保有状況の要約を取得"""
        summary = {
            'stock_count': len(self.stock_df) if not self.stock_df.empty else 0,
            'total_acquisition_cost_usd': 0
        }
        
        if not self.stock_df.empty:
            # 取得原価の合計（USD）
            self.stock_df['取得原価'] = self.stock_df['数量'] * self.stock_df['取得単価（ドル）']
            summary['total_acquisition_cost_usd'] = self.stock_df['取得原価'].sum()
        
        return summary
    
    def get_stock_details(self, symbol: str) -> Dict:
        """特定銘柄の詳細情報を取得"""
        if self.stock_df.empty:
            return {}
        
        for _, row in self.stock_df.iterrows():
            if row['銘柄シンボル'] == symbol:
                return {
                    'symbol': symbol,
                    'quantity': row['数量'],
                    'acquisition_price_usd': row['取得単価（ドル）'],
                    'acquisition_cost_usd': row['数量'] * row['取得単価（ドル）'],
                    'section': row['セクション']
                }
        
        return {}


def main():
    """テスト用のメイン関数"""
    us_stock_data = USStockData('input/us_data.csv')
    
    print("=== 保有米国株シンボル ===")
    symbols = us_stock_data.get_stock_symbols()
    print(symbols)
    
    print("\n=== 保有状況サマリー ===")
    summary = us_stock_data.get_holdings_summary()
    print(f"米国株銘柄数: {summary['stock_count']}")
    print(f"総取得原価: ${summary['total_acquisition_cost_usd']:,.2f}")
    
    print("\n=== 個別銘柄詳細 ===")
    for symbol in symbols:
        details = us_stock_data.get_stock_details(symbol)
        if details:
            print(f"{details['symbol']}")
            print(f"  数量: {details['quantity']}株")
            print(f"  取得単価: ${details['acquisition_price_usd']:.2f}")
            print(f"  取得原価: ${details['acquisition_cost_usd']:,.2f}")
            print(f"  セクション: {details['section']}")
            print()


if __name__ == "__main__":
    main()