#!/usr/bin/env python3
"""
Test the WhatsApp webhook directly
"""

import requests
import json

# Your ngrok URL
webhook_url = "https://09306c68bc7b.ngrok-free.app/webhook"

# Test data that mimics what Twilio sends
test_data = {
    'Body': 'What is quantum computing?',
    'From': 'whatsapp:+919360011424',
    'To': 'whatsapp:+14155238886'
}

print(f"🧪 Testing webhook at: {webhook_url}")
print(f"📤 Sending test message: {test_data['Body']}")

try:
    response = requests.post(webhook_url, data=test_data, timeout=30)
    print(f"✅ Response Status: {response.status_code}")
    print(f"📤 Response Text: {response.text}")
    
    if response.status_code == 200:
        print("🎉 Webhook is working!")
    else:
        print("⚠️ Webhook returned an error status")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Error testing webhook: {e}")
