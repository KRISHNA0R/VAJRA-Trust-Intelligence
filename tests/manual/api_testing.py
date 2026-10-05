"""
API Endpoint Testing Script

Run this to test basic API functionality without model inference.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        print("✅ Health check passed")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_register_and_login():
    """Test user registration and login"""
    print("\n" + "="*60)
    print("Testing User Registration & Login")
    print("="*60)
    
    try:
        # Create unique username
        username = f"test_user_{int(time.time())}"
        
        # Register
        register_data = {
            "username": username,
            "password": "test123456",
            "email": f"{username}@test.com"
        }
        
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        print(f"Register status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Response: {response.text}")
        
        # Login
        login_data = {
            "username": username,
            "password": "test123456"
        }
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        token = token_data["access_token"]
        print(f"✅ Login successful")
        print(f"   Token: {token[:30]}...")
        print(f"   Token type: {token_data['token_type']}")
        return token
    except Exception as e:
        print(f"❌ Registration/Login failed: {e}")
        return None


def test_model_status(token):
    """Test model availability endpoint"""
    print("\n" + "="*60)
    print("Testing Model Status Endpoint")
    print("="*60)
    
    if not token:
        print("⚠️  No token available, skipping test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/models/status", headers=headers)
        assert response.status_code == 200
        
        status = response.json()
        print("✅ Model status check passed")
        print(f"\n   Models Status:")
        print(f"   {'Model':<20} {'Status':<15} {'Details'}")
        print(f"   {'-'*60}")
        
        # TruFor status
        trufor = status.get('trufor', {})
        print(f"   {'TruFor':<20} {'✅ Available' if trufor.get('available') else '❌ Unavailable':<15}")
        
        # DeepfakeBench status
        dfbench = status.get('deepfakebench', {})
        available_models = dfbench.get('available_models', [])
        print(f"   {'DeepfakeBench':<20} {f'{len(available_models)} models':<15}")
        
        for model in available_models:
            print(f"      ↳ {model}")
        
        return True
    except Exception as e:
        print(f"❌ Model status check failed: {e}")
        return False


def test_history_endpoint(token):
    """Test detection history endpoint"""
    print("\n" + "="*60)
    print("Testing History Endpoint")
    print("="*60)
    
    if not token:
        print("⚠️  No token available, skipping test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/history", headers=headers)
        assert response.status_code == 200
        
        history = response.json()
        print(f"✅ History endpoint accessible")
        print(f"   Total records: {len(history)}")
        
        if len(history) > 0:
            print(f"   Latest detection:")
            latest = history[0]
            print(f"      File: {latest.get('filename')}")
            print(f"      Time: {latest.get('timestamp')}")
            print(f"      Result: {latest.get('prediction')}")
        
        return True
    except Exception as e:
        print(f"❌ History endpoint failed: {e}")
        return False


def main():
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "API ENDPOINT TESTS" + " "*25 + "║")
    print("╚" + "="*58 + "╝")
    print("\n📌 Make sure the server is running:")
    print("   docker-compose up -d")
    print("   OR")
    print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    
    input("\nPress Enter to start tests...")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    token = test_register_and_login()
    results.append(("Register & Login", token is not None))
    results.append(("Model Status", test_model_status(token)))
    results.append(("History Endpoint", test_history_endpoint(token)))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<25} {status}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except requests.exceptions.ConnectionError:
        print("\n\n❌ Cannot connect to server!")
        print("   Make sure the server is running on http://localhost:8000")

