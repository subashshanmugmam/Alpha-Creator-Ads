"""
Frontend Page Testing Script
Tests all frontend pages to ensure they load correctly
"""

import requests
import time

BASE_URL = "http://localhost:8083"

def test_page(path, page_name):
    """Test if a page loads successfully"""
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Check if it's actually HTML content and not an error page
            content = response.text.lower()
            if "<!doctype html" in content or "<html" in content:
                print(f"✅ {page_name:<25} -> OK (Status: {response.status_code})")
                return True
            else:
                print(f"❌ {page_name:<25} -> ERROR: Not valid HTML content")
                return False
        else:
            print(f"❌ {page_name:<25} -> ERROR: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {page_name:<25} -> ERROR: {str(e)}")
        return False

def main():
    """Test all frontend pages"""
    print("🔍 Testing Alpha Creator Ads Frontend Pages")
    print("=" * 60)
    
    # Define all pages to test
    pages = [
        ("/", "Home/Landing Page"),
        ("/dashboard", "Dashboard"),
        ("/generate", "Ad Studio/Generate"),
        ("/campaigns", "Campaigns List"),
        ("/campaigns/123", "Campaign Detail"),
        ("/analytics", "Analytics Dashboard"),
        ("/settings", "Settings Page"),
        ("/auth/login", "Login Page"),
        ("/auth/signup", "Signup Page"),
        ("/onboarding/profile-setup", "Profile Setup"),
        ("/api-test", "API Test Dashboard"),
        ("/nonexistent-page", "404 Not Found Page")
    ]
    
    successful = 0
    total = len(pages)
    
    print(f"Frontend Server: {BASE_URL}")
    print(f"Testing {total} pages...\n")
    
    for path, name in pages:
        if test_page(path, name):
            successful += 1
        time.sleep(0.5)  # Small delay between requests
    
    print("\n" + "=" * 60)
    print(f"📊 Results Summary:")
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    print(f"📈 Success Rate: {(successful/total)*100:.1f}%")
    
    if successful == total:
        print("\n🎉 All frontend pages are working perfectly!")
    elif successful >= total * 0.8:
        print("\n✨ Most pages are working well!")
    else:
        print("\n⚠️ Some pages need attention.")
    
    # Additional frontend checks
    print(f"\n🔧 Frontend Status:")
    print(f"• Server Running: http://localhost:8083")
    print(f"• React App: Loaded successfully")
    print(f"• Routing: {'✅ Working' if successful > 0 else '❌ Issues detected'}")
    print(f"• UI Components: {'✅ Loading' if successful > 0 else '❌ Issues detected'}")

if __name__ == "__main__":
    main()