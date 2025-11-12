#!/usr/bin/env python3
"""
Final verification script for Alpha Creator Ads platform
Tests all components and generates a comprehensive status report
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "http://localhost:8001"  # Using alternative port
FRONTEND_URL = "http://localhost:8083"

class VerificationRunner:
    def __init__(self):
        self.results = {
            "backend": {"status": "unknown", "endpoints": {}, "errors": []},
            "frontend": {"status": "unknown", "errors": []},
            "integration": {"status": "unknown", "errors": []},
            "timestamp": datetime.now().isoformat()
        }
    
    def test_backend_endpoint(self, path, expected_status=200):
        """Test a single backend endpoint"""
        try:
            url = f"{BACKEND_URL}{path}"
            response = requests.get(url, timeout=10)
            
            success = response.status_code == expected_status
            self.results["backend"]["endpoints"][path] = {
                "status_code": response.status_code,
                "success": success,
                "response_size": len(response.content),
                "content_type": response.headers.get('content-type', 'unknown')
            }
            
            if success:
                print(f"✅ {path} -> {response.status_code}")
            else:
                print(f"❌ {path} -> {response.status_code} (expected {expected_status})")
            
            return success
        except Exception as e:
            print(f"❌ {path} -> ERROR: {e}")
            self.results["backend"]["endpoints"][path] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def test_backend(self):
        """Test all backend endpoints"""
        print("\n🔍 Testing Backend Endpoints...")
        print("=" * 50)
        
        endpoints = [
            "/health",
            "/metrics",
            "/api/v1/users/me",
            "/api/v1/campaigns/list", 
            "/api/v1/ads/list",
            "/api/v1/analytics/summary",
            "/sample/users",
            "/sample/campaigns",
            "/sample/ads",
            "/sample/analytics"
        ]
        
        successes = 0
        for endpoint in endpoints:
            if self.test_backend_endpoint(endpoint):
                successes += 1
        
        success_rate = (successes / len(endpoints)) * 100
        self.results["backend"]["status"] = "healthy" if success_rate >= 80 else "degraded" if success_rate >= 50 else "failed"
        self.results["backend"]["success_rate"] = success_rate
        
        print(f"\n📊 Backend Results: {successes}/{len(endpoints)} endpoints working ({success_rate:.1f}%)")
        return success_rate >= 80
    
    def test_frontend(self):
        """Test frontend accessibility"""
        print("\n🎨 Testing Frontend...")
        print("=" * 50)
        
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            if response.status_code == 200 and "html" in response.headers.get('content-type', '').lower():
                print("✅ Frontend accessible and serving HTML")
                self.results["frontend"]["status"] = "healthy"
                return True
            else:
                print(f"❌ Frontend returned {response.status_code}")
                self.results["frontend"]["status"] = "failed"
                return False
        except Exception as e:
            print(f"❌ Frontend error: {e}")
            self.results["frontend"]["status"] = "failed"
            self.results["frontend"]["errors"].append(str(e))
            return False
    
    def test_integration(self):
        """Test integration between frontend and backend"""
        print("\n🔗 Testing Integration...")
        print("=" * 50)
        
        # Test if frontend can reach backend through API test page
        try:
            api_test_url = f"{FRONTEND_URL}/api-test"
            response = requests.get(api_test_url, timeout=10)
            if response.status_code == 200:
                print("✅ API test dashboard accessible")
                self.results["integration"]["status"] = "healthy"
                return True
            else:
                print(f"❌ API test dashboard returned {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Integration test error: {e}")
            self.results["integration"]["errors"].append(str(e))
            return False
    
    def generate_report(self):
        """Generate final verification report"""
        print("\n" + "=" * 70)
        print("🎯 FINAL VERIFICATION REPORT")
        print("=" * 70)
        
        # Overall status
        backend_ok = self.results["backend"]["status"] == "healthy"
        frontend_ok = self.results["frontend"]["status"] == "healthy"
        integration_ok = self.results["integration"]["status"] == "healthy"
        
        overall_status = "✅ PASS" if (backend_ok and frontend_ok) else "⚠️ PARTIAL" if backend_ok or frontend_ok else "❌ FAIL"
        
        print(f"📊 Overall Status: {overall_status}")
        print(f"🔧 Backend: {'✅' if backend_ok else '❌'} {self.results['backend']['status'].upper()}")
        print(f"🎨 Frontend: {'✅' if frontend_ok else '❌'} {self.results['frontend']['status'].upper()}")
        print(f"🔗 Integration: {'✅' if integration_ok else '❌'} {self.results['integration']['status'].upper()}")
        
        # Detailed backend results
        if "success_rate" in self.results["backend"]:
            success_rate = self.results["backend"]["success_rate"]
            working_endpoints = len([ep for ep in self.results["backend"]["endpoints"].values() if ep.get("success", False)])
            total_endpoints = len(self.results["backend"]["endpoints"])
            print(f"📡 API Endpoints: {working_endpoints}/{total_endpoints} working ({success_rate:.1f}%)")
        
        # Access URLs
        print(f"\n🌐 Access URLs:")
        print(f"   Backend API: {BACKEND_URL}")
        print(f"   Frontend App: {FRONTEND_URL}")
        print(f"   API Docs: {BACKEND_URL}/docs")
        print(f"   API Tests: {FRONTEND_URL}/api-test")
        
        # Recommendations
        print(f"\n💡 Next Steps:")
        if backend_ok and frontend_ok:
            print("   ✅ Platform is ready for development and testing!")
            print("   🚀 You can start building features and integrating real services")
        elif backend_ok:
            print("   🔧 Backend is working - check frontend server")
            print("   📝 Run: npm run start (in frontend directory)")
        elif frontend_ok:
            print("   🔧 Frontend is working - check backend server")
            print("   📝 Run: python start_server.py (in backend directory)")
        else:
            print("   ⚠️ Both services need attention - check the troubleshooting guide")
        
        # Save detailed results
        with open("verification_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📋 Detailed results saved to: verification_results.json")
    
    def run_all_tests(self):
        """Run complete verification suite"""
        print("🚀 Alpha Creator Ads - Final Verification")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests
        backend_result = self.test_backend()
        frontend_result = self.test_frontend()
        integration_result = self.test_integration()
        
        # Generate report
        self.generate_report()
        
        return backend_result and frontend_result

def main():
    """Main verification function"""
    verifier = VerificationRunner()
    success = verifier.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()