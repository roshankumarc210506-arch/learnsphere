"""
Simple test script to verify LearnSphere backend is working
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def print_result(test_name, success, response=None):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if response and not success:
        print(f"   Error: {response}")
    print()

def test_backend():
    """Run all backend tests"""
    
    print("\n" + "="*60)
    print("🧪 Testing LearnSphere Backend")
    print("="*60 + "\n")
    
    session = requests.Session()
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = session.get(f"{BASE_URL}/api/health")
        success = response.status_code == 200
        print_result("Health Check", success, response.json() if success else response.text)
        if success:
            print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print_result("Health Check", False, str(e))
    
    # Test 2: Get Stats
    print("2. Testing Stats Endpoint...")
    try:
        response = session.get(f"{BASE_URL}/api/stats")
        success = response.status_code == 200
        print_result("Stats Endpoint", success, response.json() if success else response.text)
        if success:
            print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print_result("Stats Endpoint", False, str(e))
    
    # Test 3: Login as Student
    print("3. Testing Student Login...")
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": "student",
                "password": "1234",
                "role": "student"
            }
        )
        success = response.status_code == 200
        print_result("Student Login", success, response.json() if not success else None)
        if success:
            print(f"   ✓ Logged in as student\n")
    except Exception as e:
        print_result("Student Login", False, str(e))
    
    # Test 4: Get Student Profile
    print("4. Testing Get Student Profile...")
    try:
        response = session.get(f"{BASE_URL}/api/student/profile")
        success = response.status_code == 200
        print_result("Get Student Profile", success, response.json() if not success else None)
        if success:
            data = response.json()
            print(f"   Student: {data['user']['name']}")
            print(f"   Weak Topics: {data['profile']['weak_topics']}")
            print(f"   Streak: {data['profile']['streak']} days\n")
    except Exception as e:
        print_result("Get Student Profile", False, str(e))
    
    # Test 5: Get Personalized Quiz
    print("5. Testing Get Personalized Quiz...")
    try:
        response = session.get(f"{BASE_URL}/api/student/quiz")
        success = response.status_code == 200
        print_result("Get Personalized Quiz", success, response.json() if not success else None)
        if success:
            data = response.json()
            total_questions = sum(len(questions) for questions in data['quiz'].values())
            print(f"   ✓ Quiz generated with {total_questions} questions\n")
    except Exception as e:
        print_result("Get Personalized Quiz", False, str(e))
    
    # Test 6: Get Leaderboard
    print("6. Testing Leaderboard...")
    try:
        response = session.get(f"{BASE_URL}/api/student/leaderboard")
        success = response.status_code == 200
        print_result("Get Leaderboard", success, response.json() if not success else None)
        if success:
            data = response.json()
            print(f"   ✓ Leaderboard has {len(data['leaderboard'])} students\n")
    except Exception as e:
        print_result("Get Leaderboard", False, str(e))
    
    # Test 7: Test AI Tutor
    print("7. Testing AI Tutor (if configured)...")
    try:
        response = session.post(
            f"{BASE_URL}/api/ai-tutor/chat",
            json={"message": "What is 2+2?"}
        )
        if response.status_code == 503:
            print("   ⚠️  AI Service not configured (expected if no API key)")
            print("   To enable: Set GEMINI_API_KEY environment variable\n")
        else:
            success = response.status_code == 200
            print_result("AI Tutor", success, response.json() if not success else None)
            if success:
                print(f"   ✓ AI responded successfully\n")
    except Exception as e:
        print_result("AI Tutor", False, str(e))
    
    # Test 8: Logout
    print("8. Testing Logout...")
    try:
        response = session.post(f"{BASE_URL}/api/auth/logout")
        success = response.status_code == 200
        print_result("Logout", success, response.json() if not success else None)
    except Exception as e:
        print_result("Logout", False, str(e))
    
    # Test 9: Login as Teacher
    print("9. Testing Teacher Login...")
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": "teacher",
                "password": "1234",
                "role": "teacher"
            }
        )
        success = response.status_code == 200
        print_result("Teacher Login", success, response.json() if not success else None)
        if success:
            print(f"   ✓ Logged in as teacher\n")
    except Exception as e:
        print_result("Teacher Login", False, str(e))
    
    print("="*60)
    print("✅ Backend Testing Complete!")
    print("="*60)
    print("\n💡 Tips:")
    print("   • If tests fail, check if backend is running: python app.py")
    print("   • Check console for error messages")
    print("   • Verify database file exists: learnsphere.db")
    print("   • For AI features, set GEMINI_API_KEY environment variable\n")


if __name__ == '__main__':
    try:
        test_backend()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend!")
        print("   Make sure the backend is running:")
        print("   1. Open a terminal")
        print("   2. Run: python app.py")
        print("   3. Wait for 'Running on http://localhost:5000'")
        print("   4. Run this test script again\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")