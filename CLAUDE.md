# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based AI-powered stock alert notification application that analyzes portfolio holdings from SBI Securities and provides intelligent alerts based on stock prices, news analysis, and technical indicators.

## Development Environment

- **Language**: Python 3
- **Required Libraries**: pandas, requests, beautifulsoup4, yfinance, python-dotenv
- **Environment Setup**: API keys and authentication info stored in `.env` file
- **Input Data**: SBI Securities CSV files in `input/jp_data.csv` (SJIS encoded)

## Core Architecture

### Data Processing Pipeline
1. **CSV Parser** (`csv_parser.py`): Handles complex SBI Securities CSV format with multiple sections (stocks, mutual funds) and SJIS encoding
2. **Stock Data Manager** (`stock_data.py`): Provides high-level interface for portfolio data access and analysis
3. **Stock Price API**: Yahoo Finance API integration (楽天証券API as alternative)
4. **News Collection**: Web scraping from 株探, 日経電子版, NewsPicks
5. **AI Analysis**: Claude API integration for news summarization and relevance analysis
6. **Technical Indicators**: Moving average deviation, RSI calculations
7. **Notifications**: LINE Notify or email alerts

### Key Components

- `SBICSVParser`: Parses multi-section CSV with irregular structure, handles合計行 and explanation rows
- `StockData`: Extracts stock codes (4-digit), maps to company names, calculates portfolio summaries
- Input CSV contains multiple sections like "株式（現物/NISA預り（成長投資枠））" with varying column structures

## Common Commands

```bash
# Test CSV parsing functionality
python3 csv_parser.py

# Test stock data management
python3 stock_data.py

# Run main application (when implemented)
python3 main.py
```

## Data Format Notes

The SBI Securities CSV input has these characteristics:
- SJIS encoding (Shift_JIS)
- Multiple sections with repeated headers
- Mixed data types with comma separators in numbers
- Summary rows and metadata that need filtering
- Stock codes are 4-digit numbers embedded in "銘柄（コード）" field format: "XXXX 会社名"

## API Integration Requirements

- Claude API key for news analysis and portfolio correlation
- Yahoo Finance API for real-time stock prices
- Optional: 楽天証券API as alternative data source
- LINE Notify token or SMTP credentials for notifications (user selectable)

## Current Implementation Status

- ✅ CSV parsing for SBI Securities format
- ✅ Stock data extraction and portfolio analysis
- 🔄 Yahoo Finance API integration (in progress)
- ⏳ News collection and web scraping
- ⏳ Claude API integration for AI analysis
- ⏳ Technical indicator calculations
- ⏳ Notification system