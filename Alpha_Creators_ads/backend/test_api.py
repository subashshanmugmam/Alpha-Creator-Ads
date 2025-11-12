"""
API Endpoint Testing Script
Tests all the major endpoints of the Alpha Creator Ads API
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"\n{'='*60}")
        print(f"Testing: {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            print(json.dumps(response.json(), indent=2))
        else:
            print(response.text)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")
        return False

def main():
    """Test all major endpoints"""
    print("🚀 Alpha Creator Ads API Testing")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now()}")
    
    endpoints_to_test = [
        # Health and system endpoints
        ("/health", "GET"),
        ("/metrics", "GET"),
        
        # Database demo endpoints
        ("/api/v1/users/me", "GET"),
        ("/api/v1/campaigns/list", "GET"),
        ("/api/v1/ads/list", "GET"),
        ("/api/v1/analytics/summary", "GET"),
        ("/api/v1/campaigns/create-demo", "POST"),
        
        # Sample endpoints
        ("/sample/users", "GET"),
        ("/sample/campaigns", "GET"),
        ("/sample/ads", "GET"),
        ("/sample/analytics", "GET"),
    ]
    
    successful_tests = 0
    total_tests = len(endpoints_to_test)
    
    for endpoint, method in endpoints_to_test:
        if test_endpoint(endpoint, method):
            successful_tests += 1
    
    print(f"\n{'='*60}")
    print(f"🎯 Test Results Summary")
    print(f"✅ Successful: {successful_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
    print(f"📊 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! API is fully functional.")
    elif successful_tests >= total_tests * 0.8:
        print("✨ Most tests passed! API is mostly functional.")
    else:
        print("⚠️ Several tests failed. Check the API configuration.")

if __name__ == "__main__":
    main()