"""
Quick API Endpoint Verification Script
Tests all endpoints that the frontend is expecting
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(url, method="GET"):
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url)
        
        print(f"✅ {method} {url} -> {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and len(str(data)) < 200:
                print(f"   Data: {data}")
            else:
                print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
        else:
            print(f"   Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ {method} {url} -> ERROR: {e}")
        return False

def main():
    print("🔍 Testing Alpha Creator Ads API Endpoints\n")
    
    endpoints = [
        # System endpoints
        (f"{BASE_URL}/health", "GET"),
        (f"{BASE_URL}/metrics", "GET"),
        
        # Database endpoints
        (f"{BASE_URL}/api/v1/users/me", "GET"),
        (f"{BASE_URL}/api/v1/campaigns/list", "GET"),
        (f"{BASE_URL}/api/v1/ads/list", "GET"),
        (f"{BASE_URL}/api/v1/analytics/summary", "GET"),
        (f"{BASE_URL}/api/v1/campaigns/create-demo", "POST"),
        
        # Sample endpoints
        (f"{BASE_URL}/sample/users", "GET"),
        (f"{BASE_URL}/sample/campaigns", "GET"),
        (f"{BASE_URL}/sample/ads", "GET"),
        (f"{BASE_URL}/sample/analytics", "GET"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for url, method in endpoints:
        if test_endpoint(url, method):
            success_count += 1
        print()
    
    print("="*60)
    print(f"📊 Results: {success_count}/{total_count} endpoints working ({(success_count/total_count)*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 All endpoints are working correctly!")
    else:
        print("⚠️  Some endpoints need attention.")

if __name__ == "__main__":
    main()