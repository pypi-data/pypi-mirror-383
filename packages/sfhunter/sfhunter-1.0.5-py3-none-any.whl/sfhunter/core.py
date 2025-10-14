#!/usr/bin/env python3
"""
SFHunter - High-performance Salesforce URL scanner
Detects Salesforce instances, follows redirects, saves results to files, and sends to Discord
"""

import requests
import json
import time
import re
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Dict, Optional, Tuple
import argparse
import sys
import concurrent.futures
import threading
import urllib3
from concurrent.futures import ThreadPoolExecutor
import math

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ASCII Banner
BANNER = r"""
 ______     ______   __  __     __  __     __   __     ______   ______     ______    
/\  ___\   /\  ___\ /\ \_\ \   /\ \/\ \   /\ "-.\ \   /\__  _\ /\  ___\   /\  == \   
\ \___  \  \ \  __\ \ \  __ \  \ \ \_\ \  \ \ \-.  \  \/_/\ \/ \ \  __\   \ \  __<   
 \/\_____\  \ \_\    \ \_\ \_\  \ \_____\  \ \_\"\_\    \ \_\  \ \_____\  \ \_\ \_\ 
  \/_____/   \/_/     \/_/\/_/   \/_____/   \/_/ \/_/     \/_/   \/_____/   \/_/ /_/ 

High-performance Salesforce URL scanner with advanced detection capabilities
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('sf_detector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SFHunter:
    def __init__(self, config_file: str = "config.json", high_performance: bool = False, max_workers: int = 50, 
                 concurrent_downloads: int = 200, batch_size: int = 100, connection_limit: int = 100):
        """Initialize the SFHunter with configuration"""
        self.config = self.load_config(config_file)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.detected_instances = []
        self.high_performance = high_performance
        self.max_workers = max_workers
        self.concurrent_downloads = concurrent_downloads
        self.batch_size = batch_size
        self.connection_limit = connection_limit
        self.detected_sites_lock = threading.Lock()
        self.detected_count = 0
        self.detected_count_lock = threading.Lock()
        self.sent_to_discord = set()
        self.sent_to_discord_lock = threading.Lock()
        self.scan_stats = {
            'total_urls': 0,
            'successful_scans': 0,
            'failed_scans': 0,
            'verified_findings': 0,
            'unverified_findings': 0,
            'start_time': None,
            'processed_count': 0
        }
        self.stats_lock = threading.Lock()
    
    def normalize_url(self, url: str) -> List[str]:
        """Normalize URL by adding protocol if missing"""
        url = url.strip()
        
        # If URL already has protocol, return as is
        if url.startswith(('http://', 'https://')):
            return [url]
        
        # If it's a domain without protocol, try both http and https
        if '.' in url and not url.startswith('/'):
            return [f"http://{url}", f"https://{url}"]
        
        # If it's a path, assume it needs a protocol (this shouldn't happen in normal usage)
        return [f"https://{url}"]
        
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Config file {} not found. Using default configuration.".format(config_file))
            return {
                "discord_webhook_url": "",
                "max_redirects": 10,
                "timeout": 30,
                "output_dir": "results",
                "salesforce_indicators": [
                    "salesforce.com",
                    "force.com",
                    "my.salesforce.com",
                    "login.salesforce.com",
                    "test.salesforce.com",
                    "developer.salesforce.com"
                ]
            }
    
    def is_salesforce_url(self, url: str) -> bool:
        """Check if URL contains Salesforce indicators"""
        url_lower = url.lower()
        for indicator in self.config.get("salesforce_indicators", []):
            if indicator in url_lower:
                return True
        return False
    
    def check_salesforce_headers(self, response: requests.Response) -> Tuple[bool, List[str]]:
        """Check response headers for Salesforce indicators and return signals"""
        headers_lower = {k.lower(): v.lower() for k, v in response.headers.items()}
        signals = []
        
        # Check for Salesforce-specific headers
        salesforce_headers = [
            ('x-salesforce-sip', 'Salesforce SIP Header'),
            ('x-salesforce-request-id', 'Salesforce Request ID'),
            ('x-salesforce-session-id', 'Salesforce Session ID'),
            ('x-sfdc-request-id', 'SFDC Request ID')
        ]
        
        for header, signal_name in salesforce_headers:
            if header in headers_lower:
                signals.append(signal_name)
        
        # Check for Salesforce in server header
        if 'server' in headers_lower:
            server_value = headers_lower['server']
            if 'salesforce' in server_value:
                signals.append('Salesforce Server Header')
            elif 'sfdcedge' in server_value:
                signals.append('Salesforce Edge Server')
            elif 'sfdc' in server_value:
                signals.append('SFDC Server Header')
        
        # Check for other Salesforce indicators
        if 'x-sfdc-' in str(response.headers).lower():
            signals.append('SFDC Header Pattern')
        
        return len(signals) > 0, signals
    
    def check_salesforce_content(self, content: str) -> Tuple[bool, List[str]]:
        """Check page content for Salesforce indicators and return signals"""
        content_lower = content.lower()
        signals = []
        
        # Aura/Lightning detection (primary method) - be more specific
        if ("aura" in content_lower and ("aura://" in content_lower or "aura." in content_lower or "aura/" in content_lower)) or \
           ("lightning" in content_lower and ("lightning/" in content_lower or "lightning." in content_lower or "lightning:" in content_lower)):
            signals.append("Aura/Lightning")
        
        # Salesforce branding - be more specific to avoid false positives
        if ("salesforce" in content_lower and ("salesforce.com" in content_lower or "salesforce/" in content_lower or "salesforce." in content_lower)) or \
           ("visualforce" in content_lower and ("visualforce/" in content_lower or "visualforce." in content_lower)):
            signals.append("Salesforce Branding")
        
        # Force.com redirect detection
        if "community.force.com" in content_lower or "force.com" in content_lower:
            signals.append("Force.com Redirect")
        
        # Additional Salesforce-specific patterns
        patterns = [
            (r'salesforce\.com', "Salesforce Domain"),
            (r'force\.com', "Force.com Domain"),
            (r'lightning\.salesforce\.com', "Lightning Framework"),
            (r'my\.salesforce\.com', "My Salesforce"),
            (r'login\.salesforce\.com', "Salesforce Login"),
            (r'visual\.force\.com', "Visualforce"),
            (r'apex\.salesforce\.com', "Apex API"),
            (r'api\.salesforce\.com', "Salesforce API"),
            (r'data\.salesforce\.com', "Salesforce Data"),
            (r'secure\.force\.com', "Secure Force"),
            (r'na\d+\.salesforce\.com', "NA Instance"),
            (r'eu\d+\.salesforce\.com', "EU Instance"),
            (r'ap\d+\.salesforce\.com', "AP Instance"),
            (r'cs\d+\.salesforce\.com', "CS Instance"),
            (r'lightning\.force\.com', "Lightning Force"),
            (r'sfdc\.com', "SFDC Domain"),
            (r'sfdc-', "SFDC Header"),
            (r'x-sfdc-', "SFDC Header Pattern"),
            (r'visualforce', "Visualforce Component"),
            (r'apex\.salesforce\.com', "Apex API"),
            (r'apex/', "Apex Code"),
            (r'salesforce-community', "Salesforce Community"),
            (r'community\.force\.com', "Community Force"),
            (r'customer\.force\.com', "Customer Force"),
            (r'partner\.force\.com', "Partner Force"),
            (r'developer\.force\.com', "Developer Force")
        ]
        
        for pattern, signal_name in patterns:
            if re.search(pattern, content_lower):
                if signal_name not in signals:
                    signals.append(signal_name)
        
        return len(signals) > 0, signals
    
    def follow_redirects(self, url: str) -> Tuple[str, List[str]]:
        """Follow redirects and return final URL and redirect chain"""
        redirect_chain = [url]
        current_url = url
        max_redirects = self.config.get("max_redirects", 10)
        
        for _ in range(max_redirects):
            try:
                response = self.session.head(
                    current_url, 
                    timeout=self.config.get("timeout", 30),
                    allow_redirects=False
                )
                
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('location')
                    if location:
                        # Handle relative URLs
                        current_url = urljoin(current_url, location)
                        redirect_chain.append(current_url)
                    else:
                        break
                else:
                    break
                    
            except requests.RequestException as e:
                error_msg = self._get_custom_error_message(e, current_url)
                logger.warning("Error following redirect for {}: {}".format(current_url, error_msg))
                break
                
        return current_url, redirect_chain
    
    def _get_custom_error_message(self, error: Exception, url: str) -> str:
        """Convert technical error messages to user-friendly messages"""
        error_str = str(error)
        
        # DNS Resolution Errors
        if "NameResolutionError" in error_str or "Failed to resolve" in error_str:
            if "No address associated with hostname" in error_str:
                return "DNS resolution failed - hostname not found"
            elif "Name or service not known" in error_str:
                return "DNS resolution failed - unknown hostname"
            else:
                return "DNS resolution failed"
        
        # Connection Errors
        elif "NewConnectionError" in error_str:
            if "Network is unreachable" in error_str:
                return "Network unreachable"
            elif "Connection refused" in error_str:
                return "Connection refused by server"
            else:
                return "Connection failed"
        
        # Timeout Errors
        elif "ConnectTimeoutError" in error_str:
            return "Connection timeout"
        elif "ReadTimeoutError" in error_str:
            return "Read timeout"
        elif "timed out" in error_str:
            return "Request timeout"
        
        # SSL Errors
        elif "SSLError" in error_str or "SSL" in error_str:
            return "SSL/TLS error"
        
        # HTTP Errors
        elif "HTTPError" in error_str:
            return "HTTP error occurred"
        
        # Max retries exceeded
        elif "Max retries exceeded" in error_str:
            return "Max connection retries exceeded"
        
        # Default fallback
        else:
            return "Connection error"
    
    def detect_salesforce(self, url: str) -> Optional[Dict]:
        """Detect if URL is a Salesforce instance"""
        try:
            logger.info("Analyzing URL: {}".format(url))
            
            # Follow redirects first
            final_url, redirect_chain = self.follow_redirects(url)
            logger.info("Final URL after redirects: {}".format(final_url))
            
            # Check if any URL in the chain is Salesforce
            for chain_url in redirect_chain:
                if self.is_salesforce_url(chain_url):
                    logger.info("Salesforce detected in redirect chain: {}".format(chain_url))
                    return self.create_detection_result(url, final_url, redirect_chain, "redirect_chain")
            
            # Make request to final URL
            response = self.session.get(
                final_url, 
                timeout=self.config.get("timeout", 30),
                allow_redirects=True
            )
            
            # Check URL
            if self.is_salesforce_url(response.url):
                logger.info("Salesforce detected in final URL: {}".format(response.url))
                return self.create_detection_result(url, response.url, redirect_chain, "final_url")
            
            # Check headers
            is_salesforce, signals = self.check_salesforce_headers(response)
            if is_salesforce:
                logger.info("Salesforce detected in headers for: {} - Signals: {}".format(response.url, ', '.join(signals)))
                return self.create_detection_result(url, response.url, redirect_chain, "headers", signals)
            
            # Check content
            is_salesforce, signals = self.check_salesforce_content(response.text)
            if is_salesforce:
                logger.info("Salesforce detected in content for: {} - Signals: {}".format(response.url, ', '.join(signals)))
                return self.create_detection_result(url, response.url, redirect_chain, "content", signals)
            
            logger.info("No Salesforce indicators found for: {}".format(url))
            return None
            
        except requests.RequestException as e:
            error_msg = self._get_custom_error_message(e, url)
            logger.error("Error analyzing {}: {}".format(url, error_msg))
            return None
    
    def create_detection_result(self, original_url: str, final_url: str, redirect_chain: List[str], detection_method: str, signals: List[str] = None) -> Dict:
        """Create a detection result dictionary"""
        return {
            "timestamp": datetime.now().isoformat(),
            "original_url": original_url,
            "final_url": final_url,
            "redirect_chain": redirect_chain,
            "detection_method": detection_method,
            "signals": signals or [],
            "status": "detected"
        }
    
    def save_results(self, results: List[Dict], filename: str = None):
        """Save detection results to text file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"salesforce_detections_{timestamp}.txt"
        
        output_dir = self.config.get("output_dir", "results")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        # Save only detected Salesforce URLs as simple list
        detected_results = [r for r in results if r.get('status') == 'detected']
        
        with open(filepath, 'w') as f:
            if detected_results:
                for result in detected_results:
                    f.write(f"{result['final_url']}\n")
            else:
                f.write("No Salesforce instances detected.\n")
        
        logger.info("Results saved to: {}".format(filepath))
        return filepath
    
    def send_discord_message(self, url: str, signals: List[str]):
        """Send simple Discord text message for detected site"""
        webhook_url = self.config.get("discord_webhook_url")
        if not webhook_url or not webhook_url.strip():
            return
        
        # Format signals like jshunter style
        if signals:
            signal_text = ", ".join(signals)
            message = f"[info] {url} [{signal_text}] ✅ Verified"
        else:
            message = f"[info] {url} [Salesforce Detected] ✅ Verified"
        
        try:
            requests.post(webhook_url, json={"content": message})
        except Exception as e:
            logger.error("Discord message error: {}".format(e))

    def send_discord_file(self, filepath: str, results: List[Dict]):
        """Send the actual text file to Discord webhook"""
        webhook_url = self.config.get("discord_webhook_url")
        if not webhook_url or not webhook_url.strip():
            return
        
        try:
            # Send the actual file to Discord
            with open(filepath, "rb") as f:
                files = {"file": f}
                data = {"content": "SFHunter Scan Results"}
                requests.post(webhook_url, files=files, data=data)
                    
        except Exception as e:
            logger.error("Discord file upload error: {}".format(e))

    def send_telegram_message(self, message: str, filepath: str = None):
        """Send message to Telegram bot"""
        bot_token = self.config.get("telegram_bot_token")
        chat_id = self.config.get("telegram_chat_id")
        
        if not bot_token or not chat_id:
            return
            
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            # Send file if provided
            if filepath and os.path.exists(filepath):
                url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
                with open(filepath, "rb") as f:
                    files = {"document": f}
                    data = {"chat_id": chat_id}
                    requests.post(url, files=files, data=data)
                    
        except Exception as e:
            logger.error("Telegram message error: {}".format(e))

    def send_telegram_embed(self, domain: str, url: str, status: str, title: str, signals: List[str]):
        """Send individual Telegram message for detected site"""
        bot_token = self.config.get("telegram_bot_token")
        chat_id = self.config.get("telegram_chat_id")
        
        if not bot_token or not chat_id:
            return
            
        message = f"""
🔍 <b>Salesforce Site Detected</b>

🌐 <b>Domain:</b> <code>{domain}</code>
🔗 <b>URL:</b> <a href="{url}">{url}</a>
📊 <b>Status:</b> {status}
📝 <b>Title:</b> {title}
🎯 <b>Signals:</b> {', '.join(signals) if signals else 'No signals'}

<i>SFHunter Detection</i>
"""
        
        try:
            url_api = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            requests.post(url_api, data=data)
        except Exception as e:
            logger.error("Telegram embed error: {}".format(e))

    def send_to_discord(self, results: List[Dict], filepath: str):
        """Send results to Discord webhook"""
        webhook_url = self.config.get("discord_webhook_url")
        if not webhook_url:
            logger.warning("No Discord webhook URL configured")
            return
        
        try:
            # Send individual messages for each detection
            for result in results:
                if result.get("status") == "detected":
                    domain = urlparse(result['final_url']).netloc
                    signals = result.get('signals', [])
                    
                    with self.sent_to_discord_lock:
                        if domain not in self.sent_to_discord:
                            self.send_discord_message(
                                result['final_url'],
                                signals
                            )
                            self.sent_to_discord.add(domain)
            
            # Send results summary in text format
            self.send_discord_file(filepath, results)
            logger.info("Results sent to Discord successfully")
            
        except Exception as e:
            logger.error("Error sending to Discord: {}".format(e))
    
    def update_progress(self, success: bool = True, verified: bool = False):
        """Update scan progress and statistics"""
        with self.stats_lock:
            self.scan_stats['processed_count'] += 1
            if success:
                self.scan_stats['successful_scans'] += 1
                if verified:
                    self.scan_stats['verified_findings'] += 1
                else:
                    self.scan_stats['unverified_findings'] += 1
            else:
                self.scan_stats['failed_scans'] += 1

    def print_progress(self):
        """Print progress in jshunter style"""
        with self.stats_lock:
            total = self.scan_stats['total_urls']
            processed = self.scan_stats['processed_count']
            success = self.scan_stats['successful_scans']
            failed = self.scan_stats['failed_scans']
            verified = self.scan_stats['verified_findings']
            unverified = self.scan_stats['unverified_findings']
            
            if total > 0:
                percentage = (processed / total) * 100
                rate = processed / max(1, (time.time() - self.scan_stats['start_time']))
                eta_seconds = (total - processed) / max(0.1, rate)
                eta_minutes = eta_seconds / 60
                
                # Only print progress every 10 processed URLs to avoid interfering with logs
                if processed % 10 == 0 or processed == total:
                    print(f"\n[PROGRESS] {processed}/{total} ({percentage:.1f}%) | Rate: {rate:.1f}/s | ETA: {eta_minutes:.1f}m | Success: {success} | Failed: {failed} | Verified: {verified} | Unverified: {unverified}")

    def worker(self, url: str):
        """Worker function for threaded scanning"""
        try:
            # Normalize URL to handle domains without protocol
            urls_to_try = self.normalize_url(url)
            
            for test_url in urls_to_try:
                result = self.detect_salesforce(test_url)
                if result:
                    with self.detected_sites_lock:
                        self.detected_instances.append(result)
                    
                    with self.detected_count_lock:
                        self.detected_count += 1
                    
                # Send Discord and Telegram notifications for this detection
                domain = urlparse(result['final_url']).netloc
                signals = result.get('signals', [])
                
                with self.sent_to_discord_lock:
                    if domain not in self.sent_to_discord:
                        # Send Discord notification
                        self.send_discord_message(
                            result['final_url'],
                            signals
                        )
                        
                        # Send Telegram notification
                        self.send_telegram_embed(
                            domain, 
                            result['final_url'], 
                            result.get('detection_method', 'unknown'),
                            result['final_url'],
                            signals
                        )
                        
                        self.sent_to_discord.add(domain)
                    
                    # Update progress with verified finding
                    self.update_progress(success=True, verified=True)
                    self.print_progress()
                    return  # Found a match, no need to try other protocols
                    
            # No Salesforce detected
            self.update_progress(success=True, verified=False)
            self.print_progress()
                        
        except Exception as e:
            self.update_progress(success=False, verified=False)
            self.print_progress()
            # Error logging is handled in detect_salesforce method

    def scan_urls(self, urls: List[str]) -> List[Dict]:
        """Scan multiple URLs for Salesforce instances"""
        results = []
        
        # Initialize scan statistics
        with self.stats_lock:
            self.scan_stats['total_urls'] = len(urls)
            self.scan_stats['start_time'] = time.time()
            self.scan_stats['processed_count'] = 0
            self.scan_stats['successful_scans'] = 0
            self.scan_stats['failed_scans'] = 0
            self.scan_stats['verified_findings'] = 0
            self.scan_stats['unverified_findings'] = 0
        
        if self.high_performance:
            print(f"[*] Using high-performance mode for {len(urls)} URLs")
            print(f"[*] Performance settings: {self.max_workers} workers, {self.concurrent_downloads} concurrent downloads, {self.batch_size} batch size")
            print(f"[*] Starting high-performance scan of {len(urls)} URLs")
            print(f"[*] Configuration: {self.concurrent_downloads} concurrent downloads, {self.batch_size} batch size, {self.max_workers} workers")
            
            # Process in batches
            num_batches = math.ceil(len(urls) / self.batch_size)
            for batch_num in range(num_batches):
                start_idx = batch_num * self.batch_size
                end_idx = min(start_idx + self.batch_size, len(urls))
                batch_urls = urls[start_idx:end_idx]
                
                print(f"[*] Processing chunk {batch_num + 1}/{num_batches} ({len(batch_urls)} URLs)")
                
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    executor.map(self.worker, batch_urls)
            
            results = self.detected_instances.copy()
        else:
            print(f"[*] Using legacy mode for {len(urls)} URLs")
            for i, url in enumerate(urls, 1):
                print(f"[+] Scanning {url}")
                
                # Normalize URL to handle domains without protocol
                urls_to_try = self.normalize_url(url)
                
                found_salesforce = False
                for test_url in urls_to_try:
                    result = self.detect_salesforce(test_url)
                    if result:
                        results.append(result)
                        self.detected_instances.append(result)
                        print(f"[+] Salesforce found in {test_url}: {', '.join(result.get('signals', []))}")
                        found_salesforce = True
                        break  # Found a match, no need to try other protocols
                
                # Update progress
                self.update_progress(success=True, verified=found_salesforce)
                
                # Add delay between requests to be respectful
                time.sleep(1)
        
        return results
    
    def scan_from_file(self, filepath: str) -> List[Dict]:
        """Scan URLs from a file (one URL per line)"""
        try:
            with open(filepath, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            logger.info("Loaded {} URLs from {}".format(len(urls), filepath))
            return self.scan_urls(urls)
            
        except FileNotFoundError:
            logger.error("File not found: {}".format(filepath))
            return []
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate a human-readable report"""
        detected = [r for r in results if r.get("status") == "detected"]
        
        report = f"""
# Salesforce Detection Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- Total URLs analyzed: {len(results)}
- Salesforce instances detected: {len(detected)}

## Detected Instances
"""
        
        for i, result in enumerate(detected, 1):
            report += f"""
### Instance {i}
- **Original URL:** {result['original_url']}
- **Final URL:** {result['final_url']}
- **Detection Method:** {result['detection_method']}
- **Redirect Chain:** {' → '.join(result['redirect_chain'])}
- **Timestamp:** {result['timestamp']}
"""
        
        return report
    
    def print_scan_summary(self):
        """Print scan summary in jshunter style"""
        with self.stats_lock:
            total = self.scan_stats['total_urls']
            success = self.scan_stats['successful_scans']
            failed = self.scan_stats['failed_scans']
            verified = self.scan_stats['verified_findings']
            unverified = self.scan_stats['unverified_findings']
            total_findings = verified + unverified
        
        print(f"\n[+] Scan Summary:")
        print(f"    Total URLs: {total}")
        print(f"    Successful scans: {success}")
        print(f"    Failed scans: {failed}")
        print(f"    Verified findings: {verified}")
        print(f"    Unverified findings: {unverified}")
        print(f"    Total findings: {total_findings}")
        print(f"\n[+] Scan complete: {success}/{total} successful, {total_findings} total findings")

def main():
    print(BANNER)
    
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
    parser.add_argument("-v", "--version", action="version", version="SFHunter v1.0.0")
    
    args = parser.parse_args()
    
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
