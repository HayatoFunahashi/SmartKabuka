import pandas as pd
from typing import Dict, List


class JPCSVParser:
    """SBI証券の保有株情報CSVを解析するクラス"""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.sections = {}
        
    def parse_csv(self) -> Dict[str, pd.DataFrame]:
        """CSVファイルを解析し、セクション別にDataFrameを返す"""
        try:
            # SJISエンコーディングでCSVを読み込み
            with open(self.csv_path, 'r', encoding='shift_jis') as f:
                lines = f.readlines()
            
            # セクションを分割
            sections = self._split_sections(lines)
            
            # 各セクションをDataFrameに変換
            parsed_sections = {}
            for section_name, section_lines in sections.items():
                df = self._parse_section(section_lines)
                if df is not None and not df.empty:
                    parsed_sections[section_name] = df
                    
            return parsed_sections
            
        except Exception as e:
            print(f"CSV解析エラー: {e}")
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
            
            # セクション名を検出（株式・投資信託関連の行）
            if (('株式（' in line or '投資信託（' in line) and 
                line.startswith('"') and line.count(',') <= 1):
                
                # セクション名を抽出（最初のフィールド）
                section_name = line.split('","')[0].strip('"')
                
                if current_section and current_lines:
                    sections[current_section] = current_lines
                current_section = section_name
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
            
        # ヘッダー行を探す
        header_line = None
        data_lines = []
        
        for line in lines:
            # CSVの行として解析を試みる
            if line.startswith('"') and '","' in line:
                # 最初の行をヘッダーとして使用
                if header_line is None:
                    header_line = line
                else:
                    # 合計行や説明行をスキップ
                    if not self._is_summary_or_description_line(line):
                        data_lines.append(line)
        
        if not header_line or not data_lines:
            return None
            
        try:
            # ヘッダーを解析
            headers = self._parse_csv_line(header_line)
            
            # データ行を解析
            parsed_data = []
            for line in data_lines:
                parsed_line = self._parse_csv_line(line)
                if len(parsed_line) == len(headers):
                    parsed_data.append(parsed_line)
            
            if not parsed_data:
                return None
                
            # DataFrameを作成
            df = pd.DataFrame(parsed_data, columns=headers)
            
            # 数値列を適切な型に変換
            df = self._convert_numeric_columns(df)
            
            return df
            
        except Exception as e:
            print(f"セクション解析エラー: {e}")
            return None
    
    def _parse_csv_line(self, line: str) -> List[str]:
        """CSV行を解析してリストに変換"""
        # 簡単なCSV解析（ダブルクォート対応）
        result = []
        current_field = ""
        in_quotes = False
        
        i = 0
        while i < len(line):
            char = line[i]
            
            if char == '"':
                if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                    # エスケープされたダブルクォート
                    current_field += '"'
                    i += 1
                else:
                    in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                result.append(current_field.strip())
                current_field = ""
            else:
                current_field += char
            
            i += 1
        
        # 最後のフィールドを追加
        result.append(current_field.strip())
        
        return result
    
    def _is_summary_or_description_line(self, line: str) -> bool:
        """合計行や説明行かどうかを判定"""
        summary_keywords = ['合計', '総計', 'total', '小計', '評価額', '※']
        
        for keyword in summary_keywords:
            if keyword in line:
                return True
        
        # 空のデータ行（"--"や空白が多い）もスキップ
        if line.count('--') > 3 or line.count('""') > 3:
            return True
        
        # カンマが少ない行（ヘッダー以外のメタデータ行）もスキップ
        if line.count(',') < 3:
            return True
            
        return False
    
    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """数値列を適切な型に変換"""
        numeric_keywords = ['数量', '単価', '現在値', '前日比', '損益', '評価額', '取得単価']
        
        for col in df.columns:
            # 数値列と思われる列を変換
            if any(keyword in col for keyword in numeric_keywords):
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.replace('+', ''), errors='coerce')
        
        return df
    
    def get_stock_holdings(self) -> pd.DataFrame:
        """株式保有情報のみを統合して返す"""
        all_sections = self.parse_csv()
        stock_data = []
        
        for section_name, df in all_sections.items():
            if '株式' in section_name:
                # セクション名を追加
                df_copy = df.copy()
                df_copy['セクション'] = section_name
                stock_data.append(df_copy)
        
        if stock_data:
            return pd.concat(stock_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def get_fund_holdings(self) -> pd.DataFrame:
        """投資信託保有情報のみを統合して返す"""
        all_sections = self.parse_csv()
        fund_data = []
        
        for section_name, df in all_sections.items():
            if '投資信託' in section_name:
                # セクション名を追加
                df_copy = df.copy()
                df_copy['セクション'] = section_name
                fund_data.append(df_copy)
        
        if fund_data:
            return pd.concat(fund_data, ignore_index=True)
        else:
            return pd.DataFrame()


def main():
    """テスト用のメイン関数"""
    parser = JPCSVParser('input/data.csv')
    
    # 全セクションを解析
    sections = parser.parse_csv()
    print(f"検出されたセクション数: {len(sections)}")
    
    for section_name, df in sections.items():
        print(f"\n=== {section_name} ===")
        print(f"行数: {len(df)}")
        print(f"列: {list(df.columns)}")
        print(df.head())
    
    # 株式保有情報
    stock_df = parser.get_stock_holdings()
    print(f"\n=== 株式保有情報統合 ===")
    print(f"行数: {len(stock_df)}")
    if not stock_df.empty:
        print(stock_df)
    
    # 投資信託保有情報
    fund_df = parser.get_fund_holdings()
    print(f"\n=== 投資信託保有情報統合 ===")
    print(f"行数: {len(fund_df)}")
    if not fund_df.empty:
        print(fund_df)


if __name__ == "__main__":
    main()