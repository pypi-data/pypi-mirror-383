#!/usr/bin/env python3
"""
Example usage of SFHunter
"""

from sfhunter import SFHunter
import json

def main():
    # Initialize SFHunter
    detector = SFHunter("config.json", high_performance=True, max_workers=10)
    
    # Example URLs to test
    test_urls = [
        "https://example.com",
        "https://test.salesforce.com",
        "https://developer.salesforce.com",
        "https://login.salesforce.com",
        "https://community.force.com"
    ]
    
    print("🔍 Starting Salesforce detection...")
    print(f"Testing {len(test_urls)} URLs...")
    
    # Scan the URLs
    results = detector.scan_urls(test_urls)
    
    # Display results
    if results:
        print(f"\n✅ Found {len(results)} Salesforce instances:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['final_url']}")
            print(f"   Method: {result['detection_method']}")
            print(f"   Original: {result['original_url']}")
    else:
        print("\n❌ No Salesforce instances detected")
    
    # Save results
    if results:
        filepath = detector.save_results(results)
        print(f"\n💾 Results saved to: {filepath}")
        
        # Send to Discord (if configured)
        detector.send_to_discord(results, filepath)
        print("📱 Discord notification sent (if webhook configured)")
    
    print("\n🏁 Detection complete!")

if __name__ == "__main__":
    main()
