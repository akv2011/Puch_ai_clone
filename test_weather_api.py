#!/usr/bin/env python3
"""
OpenWeatherMap API Key Test Script
Tests both basic weather API and One Call API 3.0
"""

import requests
import time

# Your API key
API_KEY = "01eded1679d0c2b005b5105e661f56cc"

def test_basic_weather_api():
    """Test basic weather API"""
    print("🌤️  Testing Basic Weather API...")
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Chennai&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Basic Weather API: WORKING")
            print(f"   Chennai Temperature: {data['main']['temp']}°C")
            print(f"   Weather: {data['weather'][0]['description']}")
            return True
        elif response.status_code == 401:
            print("❌ Basic Weather API: API key not activated yet")
            return False
        else:
            print(f"❌ Basic Weather API: Error {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Basic Weather API: Error - {e}")
        return False

def test_onecall_api():
    """Test One Call API 3.0"""
    print("\n🌍 Testing One Call API 3.0...")
    # Chennai coordinates
    lat, lon = 13.0827, 80.2707
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ One Call API 3.0: WORKING")
            print(f"   Current Temperature: {data['current']['temp']}°C")
            print(f"   8-day forecast available: {len(data['daily'])} days")
            return True
        elif response.status_code == 401:
            print("❌ One Call API 3.0: Not subscribed or API key not activated")
            return False
        elif response.status_code == 429:
            print("❌ One Call API 3.0: Rate limit exceeded")
            return False
        else:
            print(f"❌ One Call API 3.0: Error {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ One Call API 3.0: Error - {e}")
        return False

def main():
    print("🔑 OpenWeatherMap API Key Test")
    print(f"API Key: {API_KEY}")
    print("=" * 50)
    
    # Test basic API
    basic_works = test_basic_weather_api()
    
    # Test One Call API 3.0
    onecall_works = test_onecall_api()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    
    if basic_works and onecall_works:
        print("🎉 ALL APIs WORKING! Your weather server will work perfectly.")
        print("\n✅ Next steps:")
        print("   1. Your API key is fully activated")
        print("   2. Both basic and One Call API 3.0 are working")
        print("   3. You can now test weather queries via WhatsApp")
    elif basic_works and not onecall_works:
        print("⚠️  Basic API working, but One Call API 3.0 needs subscription")
        print("\n📋 Next steps:")
        print("   1. Go to: https://openweathermap.org/api/one-call-3")
        print("   2. Subscribe to the free tier (1,000 calls/day)")
        print("   3. Wait for activation (usually immediate)")
    elif not basic_works:
        print("⏳ API key not activated yet")
        print("\n📋 Next steps:")
        print("   1. Wait for API key activation (up to 2 hours)")
        print("   2. Run this script again to test")
        print("   3. Then subscribe to One Call API 3.0")
    
    print(f"\n🔄 Run this script again to retest: python test_weather_api.py")

if __name__ == "__main__":
    main()
