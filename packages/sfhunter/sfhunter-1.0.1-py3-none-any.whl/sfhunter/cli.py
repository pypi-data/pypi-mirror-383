#!/usr/bin/env python3
"""
SFHunter CLI module
"""

import sys
import os
import subprocess
import requests
from .core import SFHunter

# ASCII Banner
BANNER = r"""
 ______     ______   __  __     __  __     __   __     ______   ______     ______    
/\  ___\   /\  ___\ /\ \_\ \   /\ \/\ \   /\ "-.\ \   /\__  _\ /\  ___\   /\  == \   
\ \___  \  \ \  __\ \ \  __ \  \ \ \_\ \  \ \ \-.  \  \/_/\ \/ \ \  __\   \ \  __<   
 \/\_____\  \ \_\    \ \_\ \_\  \ \_____\  \ \_\"\_\    \ \_\  \ \_____\  \ \_\ \_\ 
  \/_____/   \/_/     \/_/\/_/   \/_____/   \/_/ \/_/     \/_/   \/_____/   \/_/ /_/ 

High-performance Salesforce URL scanner with advanced detection capabilities
"""

def update_sfhunter():
    """Update SFHunter to the latest version from PyPI"""
    print("🔄 Checking for SFHunter updates...")
    
    try:
        # Check current version
        current_version = "1.0.1"
        print(f"Current version: {current_version}")
        
        # Check latest version from PyPI
        response = requests.get("https://pypi.org/pypi/sfhunter/json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            latest_version = data["info"]["version"]
            print(f"Latest version: {latest_version}")
            
            if latest_version == current_version:
                print("✅ SFHunter is already up to date!")
                return
            
            print(f"🔄 Updating from {current_version} to {latest_version}...")
            
            # Update using pip
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "--upgrade", "sfhunter"
                ], check=True, capture_output=True, text=True)
                
                print("✅ SFHunter updated successfully!")
                print("🔄 Please restart your terminal or run 'hash -r' to use the updated version.")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Update failed: {e}")
                print(f"Error output: {e.stderr}")
                
        else:
            print("❌ Could not check for updates. Please check your internet connection.")
            
    except requests.RequestException as e:
        print(f"❌ Network error while checking for updates: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main CLI entry point"""
    print(BANNER)
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="High-performance Salesforce URL scanner with advanced detection capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-u", "--url", help="Single URL to scan")
    parser.add_argument("-f", "--file", help="Path to a file of URLs (one per line)")
    parser.add_argument("-o", "--output", help="Output file to save results")
    parser.add_argument("--ignore-ssl", action="store_true", help="Ignore SSL certificate errors")
    parser.add_argument("--discord-webhook", help="Discord webhook URL to send verified findings")
    parser.add_argument("--telegram-bot-token", help="Telegram bot token for notifications")
    parser.add_argument("--telegram-chat-id", help="Telegram chat ID for notifications")
    parser.add_argument("--high-performance", action="store_true", help="Enable high-performance parallel processing")
    parser.add_argument("--max-workers", type=int, default=50, help="Maximum number of worker threads (default: 50)")
    parser.add_argument("--concurrent-downloads", type=int, default=200, help="Maximum concurrent downloads (default: 200)")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for processing (default: 100)")
    parser.add_argument("--connection-limit", type=int, default=100, help="HTTP connection limit (default: 100)")
    parser.add_argument("-up", "--update", action="store_true", help="Update SFHunter to the latest version from PyPI")
    parser.add_argument("-v", "--version", action="version", version="SFHunter v1.0.1")
    
    args = parser.parse_args()
    
    # Handle update command
    if args.update:
        update_sfhunter()
        return
    
    if not args.url and not args.file:
        print("[!] Use -u <url> or -f <file>")
        parser.print_help()
        return
    
    # Initialize SFHunter
    detector = SFHunter(
        high_performance=args.high_performance,
        max_workers=args.max_workers,
        concurrent_downloads=args.concurrent_downloads,
        batch_size=args.batch_size,
        connection_limit=args.connection_limit
    )
    
    # Override Discord webhook if provided
    if args.discord_webhook:
        detector.config["discord_webhook_url"] = args.discord_webhook
    
    # Override Telegram settings if provided
    if args.telegram_bot_token:
        detector.config["telegram_bot_token"] = args.telegram_bot_token
    if args.telegram_chat_id:
        detector.config["telegram_chat_id"] = args.telegram_chat_id
    
    # Collect URLs
    urls = []
    if args.url:
        urls = [args.url]
    elif args.file:
        if not os.path.exists(args.file):
            print(f"[!] File not found: {args.file}")
            return
        with open(args.file, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
    
    # Remove duplicates
    urls = list(set(urls))
    
    print(f"[+] Loaded {len(urls)} URL(s). Starting scan...")
    
    # Scan URLs
    results = detector.scan_urls(urls)
    
    # Print scan summary
    detector.print_scan_summary()
    
    # Always save results (even if empty)
    output_file = args.output or "salesforce_results.txt"
    filepath = detector.save_results(results, output_file)
    print(f"[+] Results saved → {filepath}")
    
    if results:
        # Send results summary to Discord and Telegram
        detector.send_discord_file(filepath, results)
        
        # Send summary to Telegram
        summary_message = f"""
🔍 <b>SFHunter Scan Complete</b>

📊 <b>Scan Summary:</b>
• Total URLs: {len(urls)}
• Successful scans: {len(results)}
• Salesforce instances found: {len(results)}

📁 <b>Results saved to:</b> <code>{filepath}</code>

<i>SFHunter Detection Complete</i>
"""
        detector.send_telegram_message(summary_message, filepath)
    else:
        print("[!] No Salesforce sites detected.")

if __name__ == "__main__":
    main()
