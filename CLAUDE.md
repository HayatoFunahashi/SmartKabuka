# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SmartKabuka is a Python-based AI-powered portfolio notification system that analyzes holdings from SBI Securities and provides morning portfolio reports via LINE messaging. The system runs automatically on GitHub Actions and securely manages CSV data through GitHub Secrets.

## Development Environment

- **Language**: Python 3
- **Required Libraries**: pandas, yfinance, python-dotenv, line-bot-sdk, requests
- **Environment Setup**: API keys stored in `.env` file (local) or GitHub Secrets (production)
- **Input Data**: SBI Securities CSV files (`input/jp_data.csv`, `input/us_data.csv`) - SJIS encoded
- **Deployment**: GitHub Actions for automated daily execution

## Current Architecture

### Core Components
1. **Morning Notifier** (`morning_notifier.py`): Main execution file, orchestrates portfolio report generation
2. **Stock Data Managers**: 
   - `libs/jp_stock_data.py`: Japanese stock portfolio analysis
   - `libs/us_stock_data.py`: US stock portfolio analysis
3. **CSV Parsers**:
   - `libs/jp_csv_parser.py`: Handles SBI Securities Japanese stock CSV format
   - `libs/us_csv_parser.py`: Handles SBI Securities US stock CSV format
4. **Price Fetcher** (`stock_price_fetcher.py`): Yahoo Finance API integration for real-time prices
5. **LINE Notifier** (`line_notifier.py`): LINE Messaging API integration
6. **Secrets Manager** (`libs/update_secrets.py`): GitHub Secrets management for CSV data

### Data Flow
1. CSV data (Base64 encoded) → GitHub Secrets
2. GitHub Actions → Decode CSV → Load portfolio data
3. Yahoo Finance API → Fetch current prices
4. Generate portfolio report → Send via LINE
5. Schedule: Daily at 6:00 AM Japan time

## File Structure

```
SmartKabuka/
├── morning_notifier.py           # Main application entry point
├── line_notifier.py             # LINE messaging integration
├── stock_price_fetcher.py       # Yahoo Finance API client
├── libs/
│   ├── jp_stock_data.py         # Japanese stock data management
│   ├── jp_csv_parser.py         # Japanese stock CSV parser
│   ├── us_stock_data.py         # US stock data management
│   ├── us_csv_parser.py         # US stock CSV parser
│   └── update_secrets.py        # GitHub Secrets management
├── .github/workflows/
│   └── morning-notification.yml # GitHub Actions workflow
├── input/                       # Local CSV files (not committed)
│   ├── jp_data.csv             # Japanese stocks (SJIS)
│   └── us_data.csv             # US stocks (SJIS)
└── requirements.txt            # Python dependencies
```

## Common Commands

```bash
# Run morning portfolio report
python3 morning_notifier.py

# Test Japanese stock data parsing
python3 libs/jp_stock_data.py

# Test US stock data parsing  
python3 libs/us_stock_data.py

# Update GitHub Secrets with new CSV data
python3 libs/update_secrets.py

# Install dependencies
pip install -r requirements.txt
```

## CSV Data Format

### Japanese Stocks (`jp_data.csv`)
- **Encoding**: SJIS (Shift_JIS)
- **Structure**: Multi-section format with headers like "株式（現物/NISA預り（成長投資枠））"
- **Key Fields**: "銘柄（コード）" contains "4-digit-code Company Name" format
- **Parsing**: Handles irregular sections, summary rows, and comma-separated numbers

### US Stocks (`us_data.csv`)
- **Encoding**: SJIS (Shift_JIS)  
- **Structure**: Similar multi-section format for US holdings
- **Key Fields**: Stock symbols and USD prices
- **Currency**: USD/JPY conversion for display

## API Integration

### LINE Messaging API
- **Token**: `LINE_MESSAGING_API_TOKEN` (GitHub Secret/env var)
- **User ID**: `LINE_USER_ID` (GitHub Variable/env var)
- **Usage**: Send formatted portfolio reports

### Yahoo Finance API
- **Library**: yfinance
- **Markets**: Both Japanese (.T suffix) and US stocks
- **Rate Limiting**: 0.3s delay between requests
- **Fallback**: Error handling for failed API calls

## Security & Deployment

### GitHub Actions Workflow
- **Schedule**: `0 21 * * *` (6:00 AM JST daily)
- **Environment**: ubuntu-latest with Python 3.10
- **Secrets**: CSV data stored as Base64-encoded GitHub Secrets
- **Variables**: Non-sensitive config like LINE_USER_ID

### Secret Management
- `JP_DATA_CSV_BASE64`: Base64-encoded Japanese stock CSV
- `US_DATA_CSV_BASE64`: Base64-encoded US stock CSV
- `LINE_MESSAGING_API_TOKEN`: LINE API authentication
- Use `libs/update_secrets.py` to update CSV secrets via GitHub CLI

## Current Implementation Status

- ✅ CSV parsing for SBI Securities format (JP/US)
- ✅ Stock data extraction and portfolio analysis  
- ✅ Yahoo Finance API integration for real-time prices
- ✅ LINE messaging notifications
- ✅ GitHub Actions automation
- ✅ Secure CSV data management via GitHub Secrets
- ⏳ News collection and AI analysis (planned)
- ⏳ Technical indicators (RSI, moving averages) (planned)
- ⏳ Custom alert conditions (planned)