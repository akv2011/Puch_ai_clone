#!/usr/bin/env python3
"""
Test script for Google Search MCP Server
Tests all available tools with example queries
"""

import os
import sys
from google_search_mcp_server import (
    search_real_time_info,
    get_company_news_sentiment, 
    analyze_tech_trends,
    get_breaking_news,
    search_market_analysis
)

def test_google_search_tools():
    """Test all Google Search MCP tools"""
    print("🔍 Google Search MCP Server Test")
    print("=" * 50)
    
    # Check API key
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY or GOOGLE_API_KEY not found in environment")
        print("Please set one of these environment variables and try again")
        return
    
    print("✅ API key found")
    print()
    
    # Test 1: Real-time search
    print("1️⃣ Testing Real-time Information Search...")
    try:
        result = search_real_time_info("latest developments in AI technology 2025")
        if result["success"]:
            print(f"✅ Success: Found {len(result.get('sources', []))} sources")
            print(f"📝 Answer preview: {result['answer'][:100]}...")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 2: Company news sentiment
    print("2️⃣ Testing Company News Sentiment...")
    try:
        result = get_company_news_sentiment("Apple", "earnings, product launches")
        if result["success"]:
            print(f"✅ Success: Sentiment = {result.get('sentiment', 'unknown')}")
            print(f"📰 Company: {result['company']}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 3: Tech trends
    print("3️⃣ Testing Technology Trends Analysis...")
    try:
        result = analyze_tech_trends("artificial intelligence", "recent")
        if result["success"]:
            print(f"✅ Success: Analyzed {result['technology_area']}")
            print(f"📊 Trend strength: {result.get('trend_strength', 'unknown')}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 4: Breaking news
    print("4️⃣ Testing Breaking News Search...")
    try:
        result = get_breaking_news("technology industry")
        if result["success"]:
            print(f"✅ Success: Found breaking news")
            print(f"🚨 Urgency: {result.get('urgency', 'unknown')}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 5: Market analysis  
    print("5️⃣ Testing Market Analysis...")
    try:
        result = search_market_analysis("electric vehicle market", "comprehensive")
        if result["success"]:
            print(f"✅ Success: Analyzed {result['market_sector']}")
            print(f"📈 Data freshness: {result.get('data_freshness', 'unknown')}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    print("🎉 Google Search MCP Server testing complete!")
    print()
    print("💡 Usage Examples for WhatsApp:")
    print("• 'What's the latest news about Tesla?'")
    print("• 'Current sentiment around Apple stock'") 
    print("• 'Latest AI technology trends'")
    print("• 'Breaking news in crypto market'")
    print("• 'Electric vehicle market analysis'")

if __name__ == "__main__":
    test_google_search_tools()
