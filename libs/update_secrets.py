#!/usr/bin/env python3
"""
CSV Secrets Updater for GitHub Actions
Encodes CSV files to Base64 and updates GitHub repository secrets.
"""

import os
import base64
import subprocess
import sys
from pathlib import Path

def encode_csv_to_base64(csv_path):
    """CSVファイルをBase64エンコードする"""
    try:
        with open(csv_path, 'rb') as f:
            csv_content = f.read()
        return base64.b64encode(csv_content).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: File not found: {csv_path}")
        return None
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return None

def update_github_secret(secret_name, secret_value, repo_name=None):
    """GitHub CLIを使用してシークレットを更新する"""
    try:
        # リポジトリ名が指定されていない場合は現在のリポジトリを使用
        cmd = ['gh', 'secret', 'set', secret_name]
        if repo_name:
            cmd.extend(['--repo', repo_name])
        
        # シークレット値を標準入力として渡す
        result = subprocess.run(
            cmd,
            input=secret_value,
            text=True,
            capture_output=True,
            check=True
        )
        
        print(f"✅ Successfully updated secret: {secret_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update secret {secret_name}: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not found. Please install it first:")
        print("   https://cli.github.com/")
        return False

def check_gh_cli():
    """GitHub CLIがインストールされているか確認"""
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, check=True)
        print(f"✅ GitHub CLI found: {result.stdout.decode().strip().split()[0]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GitHub CLI not found. Please install it first:")
        print("   https://cli.github.com/")
        return False

def check_gh_auth():
    """GitHub CLIの認証状態を確認"""
    try:
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, check=True)
        print("✅ GitHub CLI authenticated")
        return True
    except subprocess.CalledProcessError:
        print("❌ GitHub CLI not authenticated. Please run:")
        print("   gh auth login")
        return False

def main():
    print("🔐 CSV Secrets Updater for GitHub Actions")
    print("=" * 50)
    
    # GitHub CLIの確認
    if not check_gh_cli():
        sys.exit(1)
    
    if not check_gh_auth():
        sys.exit(1)
    
    # 入力ディレクトリの確認
    input_dir = Path("input")
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        sys.exit(1)
    
    # CSVファイルの処理
    csv_files = {
        "jp_data.csv": "JP_DATA_CSV_BASE64",
        "us_data.csv": "US_DATA_CSV_BASE64"
    }
    
    success_count = 0
    
    for csv_file, secret_name in csv_files.items():
        csv_path = input_dir / csv_file
        
        print(f"\n📁 Processing {csv_file}...")
        
        if not csv_path.exists():
            print(f"⚠️  File not found: {csv_path} (skipping)")
            continue
        
        # Base64エンコード
        base64_content = encode_csv_to_base64(csv_path)
        if base64_content is None:
            continue
        
        print(f"📏 Encoded size: {len(base64_content)} characters")
        
        # GitHub Secretを更新
        if update_github_secret(secret_name, base64_content):
            success_count += 1
    
    print(f"\n✨ Completed! Successfully updated {success_count} secrets.")
    
    if success_count > 0:
        print("\n📝 Next steps:")
        print("1. The GitHub Actions workflow will now use the updated CSV data")
        print("2. Test the workflow to ensure it works correctly")

if __name__ == "__main__":
    main()