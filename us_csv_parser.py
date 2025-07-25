import pandas as pd
from typing import Dict, List


class USCSVParser:
    """米国株式CSVを解析するクラス"""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        
    def parse_csv(self) -> Dict[str, pd.DataFrame]:
        """CSVファイルを解析し、セクション別にDataFrameを返す"""
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            sections = self._split_sections(lines)
            
            parsed_sections = {}
            for section_name, section_lines in sections.items():
                df = self._parse_section(section_lines)
                if df is not None and not df.empty:
                    parsed_sections[section_name] = df
                    
            return parsed_sections
            
        except Exception as e:
            print(f"米国株CSV解析エラー: {e}")
            return {}
    
    def _split_sections(self, lines: List[str]) -> Dict[str, List[str]]:
        """CSVをセクション別に分割"""
        sections = {}
        current_section = None
        current_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # セクション名を検出（米国株式関連の行）
            if '米国株式（' in line and line.endswith('）'):
                if current_section and current_lines:
                    sections[current_section] = current_lines
                current_section = line
                current_lines = []
                continue
            
            # データ行として追加
            if current_section:
                current_lines.append(line)
        
        # 最後のセクションを追加
        if current_section and current_lines:
            sections[current_section] = current_lines
            
        return sections
    
    def _parse_section(self, lines: List[str]) -> pd.DataFrame:
        """セクションの行をDataFrameに変換"""
        if not lines:
            return None
            
        # ヘッダー行（最初の行）
        header_line = lines[0]
        data_lines = lines[1:]
        
        if not data_lines:
            return None
        
        try:
            # ヘッダーを解析
            headers = [col.strip() for col in header_line.split(',')]
            
            # データ行を解析
            parsed_data = []
            for line in data_lines:
                fields = [field.strip() for field in line.split(',')]
                if len(fields) == len(headers):
                    parsed_data.append(fields)
            
            if not parsed_data:
                return None
                
            # DataFrameを作成
            df = pd.DataFrame(parsed_data, columns=headers)
            
            # 数値列を適切な型に変換
            df = self._convert_numeric_columns(df)
            
            return df
            
        except Exception as e:
            print(f"米国株セクション解析エラー: {e}")
            return None
    
    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """数値列を適切な型に変換"""
        numeric_columns = ['数量', '取得単価（ドル）']
        
        for col in df.columns:
            if any(keyword in col for keyword in numeric_columns):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_us_stock_holdings(self) -> pd.DataFrame:
        """米国株保有情報のみを統合して返す"""
        all_sections = self.parse_csv()
        stock_data = []
        
        for section_name, df in all_sections.items():
            if '米国株式' in section_name:
                # セクション名を追加
                df_copy = df.copy()
                df_copy['セクション'] = section_name
                stock_data.append(df_copy)
        
        if stock_data:
            return pd.concat(stock_data, ignore_index=True)
        else:
            return pd.DataFrame()


def main():
    """テスト用のメイン関数"""
    parser = USCSVParser('input/us_data.csv')
    
    # 全セクションを解析
    sections = parser.parse_csv()
    print(f"検出されたセクション数: {len(sections)}")
    
    for section_name, df in sections.items():
        print(f"\n=== {section_name} ===")
        print(f"行数: {len(df)}")
        print(f"列: {list(df.columns)}")
        print(df)
    
    # 米国株保有情報統合
    us_stock_df = parser.get_us_stock_holdings()
    print(f"\n=== 米国株保有情報統合 ===")
    print(f"行数: {len(us_stock_df)}")
    if not us_stock_df.empty:
        print(us_stock_df)


if __name__ == "__main__":
    main()