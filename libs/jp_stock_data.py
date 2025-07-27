import re
from typing import Dict, List, Tuple
from libs.jp_csv_parser import JPCSVParser


class JPStockData:
    """株式データを管理するクラス"""
    
    def __init__(self, csv_path: str):
        self.parser = JPCSVParser(csv_path)
        self.stock_df = None
        self.fund_df = None
        self._load_data()
    
    def _load_data(self):
        """データを読み込み"""
        self.stock_df = self.parser.get_stock_holdings()
        self.fund_df = self.parser.get_fund_holdings()
    
    def get_stock_codes(self) -> List[str]:
        """保有株式の銘柄コードを取得"""
        if self.stock_df.empty:
            return []
        
        codes = []
        for _, row in self.stock_df.iterrows():
            # 銘柄（コード）から数字部分を抽出
            stock_name = row['銘柄（コード）']
            match = re.search(r'(\d{4})', stock_name)
            if match:
                codes.append(match.group(1))
        
        return codes
    
    def get_stock_names(self) -> Dict[str, str]:
        """銘柄コードと名前のマッピングを取得"""
        if self.stock_df.empty:
            return {}
        
        mapping = {}
        for _, row in self.stock_df.iterrows():
            stock_name = row['銘柄（コード）']
            match = re.search(r'(\d{4})\s+(.+)', stock_name)
            if match:
                code = match.group(1)
                name = match.group(2)
                mapping[code] = name
        
        return mapping
    
    def get_holdings_summary(self) -> Dict:
        """保有状況の要約を取得"""
        summary = {
            'stock_count': len(self.stock_df) if not self.stock_df.empty else 0,
            'fund_count': len(self.fund_df) if not self.fund_df.empty else 0,
            'total_evaluation': 0,
            'total_profit_loss': 0
        }
        
        if not self.stock_df.empty:
            # 評価額と損益の合計を計算
            summary['total_evaluation'] += self.stock_df['評価額'].sum()
            summary['total_profit_loss'] += self.stock_df['損益'].sum()
        
        if not self.fund_df.empty:
            summary['total_evaluation'] += self.fund_df['評価額'].sum()
            summary['total_profit_loss'] += self.fund_df['損益'].sum()
        
        return summary
    
    def get_stock_details(self, code: str) -> Dict:
        """特定銘柄の詳細情報を取得"""
        if self.stock_df.empty:
            return {}
        
        for _, row in self.stock_df.iterrows():
            stock_name = row['銘柄（コード）']
            if code in stock_name:
                return {
                    'code': code,
                    'name': stock_name.replace(f'{code} ', ''),
                    'quantity': row['数量'],
                    'acquisition_price': row.get('取得単価', row.get('参考単価', 0)),
                    'current_price': row['現在値'],
                    'evaluation': row['評価額'],
                    'profit_loss': row['損益'],
                    'profit_loss_pct': row['損益（％）'],
                    'previous_day_change': row['前日比'],
                    'previous_day_change_pct': row['前日比（％）'],
                    'section': row['セクション']
                }
        
        return {}


def main():
    """テスト用のメイン関数"""
    stock_data = JPStockData('input/jp_data.csv')
    
    print("=== 保有銘柄コード ===")
    codes = stock_data.get_stock_codes()
    print(codes)
    
    print("\n=== 銘柄コードと名前のマッピング ===")
    mapping = stock_data.get_stock_names()
    for code, name in mapping.items():
        print(f"{code}: {name}")
    
    print("\n=== 保有状況サマリー ===")
    summary = stock_data.get_holdings_summary()
    print(f"株式銘柄数: {summary['stock_count']}")
    print(f"投資信託数: {summary['fund_count']}")
    print(f"総評価額: {summary['total_evaluation']:,}円")
    print(f"総損益: {summary['total_profit_loss']:+,}円")
    
    print("\n=== 個別銘柄詳細 ===")
    for code in codes:
        details = stock_data.get_stock_details(code)
        if details:
            print(f"{details['code']} {details['name']}")
            print(f"  数量: {details['quantity']}株")
            print(f"  取得単価: {details['acquisition_price']}円")
            print(f"  現在値: {details['current_price']}円")
            print(f"  評価額: {details['evaluation']:,}円")
            print(f"  損益: {details['profit_loss']:+,}円 ({details['profit_loss_pct']:+.2f}%)")
            print(f"  前日比: {details['previous_day_change']:+}円 ({details['previous_day_change_pct']:+.2f}%)")
            print()


if __name__ == "__main__":
    main()