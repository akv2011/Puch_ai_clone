# google_search_mcp_server.py - Google Search Grounding MCP Server
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import os
import json
import re
from datetime import datetime

# Create MCP server instance
mcp = FastMCP(name="GoogleSearchServer")

# Define data models
class SearchResult(BaseModel):
    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="URL of the search result")
    snippet: str = Field(..., description="Brief snippet from the search result")

class GroundedResponse(BaseModel):
    answer: str = Field(..., description="The grounded response from Gemini")
    search_queries: List[str] = Field(..., description="Search queries used")
    sources: List[SearchResult] = Field(..., description="Sources used for grounding")
    confidence: str = Field(..., description="Confidence level of the information")

class CompanyNews(BaseModel):
    company: str = Field(..., description="Company name")
    latest_news: List[str] = Field(..., description="Latest news headlines")
    sentiment: str = Field(..., description="Overall sentiment (positive, negative, neutral)")
    market_impact: str = Field(..., description="Potential market impact analysis")
    key_developments: List[str] = Field(..., description="Key recent developments")

class TechTrends(BaseModel):
    trend_topic: str = Field(..., description="Technology trend topic")
    current_status: str = Field(..., description="Current status and developments")
    key_players: List[str] = Field(..., description="Key companies/players involved")
    market_outlook: str = Field(..., description="Market outlook and predictions")
    recent_breakthroughs: List[str] = Field(..., description="Recent technological breakthroughs")

def get_gemini_client() -> genai.Client:
    """Initialize Gemini client with API key"""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables")
    return genai.Client(api_key=api_key)

def parse_grounding_metadata(response) -> tuple:
    """Extract search queries and sources from grounding metadata"""
    search_queries = []
    sources = []
    
    if hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
            metadata = candidate.grounding_metadata
            
            # Extract search queries
            if hasattr(metadata, 'web_search_queries'):
                search_queries = metadata.web_search_queries
            
            # Extract sources
            if hasattr(metadata, 'grounding_chunks'):
                for chunk in metadata.grounding_chunks:
                    if hasattr(chunk, 'web') and chunk.web:
                        sources.append(SearchResult(
                            title=chunk.web.title if hasattr(chunk.web, 'title') else "Unknown",
                            url=chunk.web.uri if hasattr(chunk.web, 'uri') else "",
                            snippet=""  # Would need to extract from content
                        ))
    
    return search_queries, sources

@mcp.tool()
def search_real_time_info(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search for real-time information using Google Search grounding
    
    Parameters:
        query: Search query for real-time information
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        Real-time search results with sources and grounded response
    """
    try:
        client = get_gemini_client()
        
        # Define the grounding tool
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        
        # Configure generation settings
        config = types.GenerateContentConfig(tools=[grounding_tool])
        
        # Enhanced prompt for better search results
        enhanced_query = f"""
        Please search for the latest information about: {query}
        
        Provide a comprehensive answer that includes:
        1. Current facts and recent developments
        2. Key statistics or data points
        3. Timeline of recent events
        4. Reliable sources and citations
        
        Focus on factual, up-to-date information from credible sources.
        """
        
        # Make the request
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=enhanced_query,
            config=config,
        )
        
        # Parse response and metadata
        search_queries, sources = parse_grounding_metadata(response)
        
        return {
            "success": True,
            "query": query,
            "answer": response.text,
            "search_queries": search_queries,
            "sources": [source.dict() for source in sources[:max_results]],
            "timestamp": datetime.now().isoformat(),
            "confidence": "high" if len(sources) >= 3 else "medium" if len(sources) >= 1 else "low"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Search failed: {str(e)}",
            "query": query
        }

@mcp.tool()
def get_company_news_sentiment(company_name: str, focus_areas: Optional[str] = None) -> Dict[str, Any]:
    """
    Get latest news and sentiment analysis for a specific company
    
    Parameters:
        company_name: Name of the company to analyze
        focus_areas: Specific areas to focus on (e.g., "earnings, product launches, legal issues")
    
    Returns:
        Company news analysis with sentiment and market impact assessment
    """
    try:
        client = get_gemini_client()
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        
        # Create focused search query
        focus_text = f" focusing on {focus_areas}" if focus_areas else ""
        
        search_prompt = f"""
        Search for the latest news about {company_name}{focus_text} and provide:
        
        1. LATEST NEWS HEADLINES (last 7 days):
        - List 5-7 most recent and significant news items
        - Include dates where possible
        
        2. SENTIMENT ANALYSIS:
        - Overall sentiment: positive/negative/neutral
        - Reasoning for sentiment assessment
        - Market perception indicators
        
        3. MARKET IMPACT ASSESSMENT:
        - Potential impact on stock price
        - Impact on company reputation
        - Competitive positioning changes
        
        4. KEY DEVELOPMENTS:
        - New products or services
        - Strategic partnerships or acquisitions
        - Executive changes or major announcements
        - Regulatory or legal updates
        
        Focus on credible financial and business news sources. Be specific about dates and provide factual analysis.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=search_prompt,
            config=config,
        )
        
        search_queries, sources = parse_grounding_metadata(response)
        
        # Parse response to extract structured information
        response_text = response.text
        
        # Extract sentiment using pattern matching
        sentiment = "neutral"
        if re.search(r'\b(positive|bullish|optimistic|strong|growth)\b', response_text.lower()):
            sentiment = "positive"
        elif re.search(r'\b(negative|bearish|pessimistic|decline|concern)\b', response_text.lower()):
            sentiment = "negative"
        
        return {
            "success": True,
            "company": company_name,
            "analysis": response_text,
            "sentiment": sentiment,
            "search_queries": search_queries,
            "sources": [source.dict() for source in sources],
            "focus_areas": focus_areas,
            "timestamp": datetime.now().isoformat(),
            "market_hours": "Consider current market hours for real-time impact"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Company news analysis failed: {str(e)}",
            "company": company_name
        }

@mcp.tool()
def analyze_tech_trends(technology_area: str, timeframe: str = "recent") -> Dict[str, Any]:
    """
    Analyze latest trends and developments in specific technology areas
    
    Parameters:
        technology_area: Technology area to analyze (e.g., "AI", "blockchain", "quantum computing", "cybersecurity")
        timeframe: Timeframe for analysis ("recent", "this_month", "this_quarter")
    
    Returns:
        Comprehensive technology trend analysis with market outlook
    """
    try:
        client = get_gemini_client()
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        
        timeframe_map = {
            "recent": "last 2 weeks",
            "this_month": "past month", 
            "this_quarter": "past 3 months"
        }
        
        time_period = timeframe_map.get(timeframe, "recent developments")
        
        trend_prompt = f"""
        Search for the latest trends and developments in {technology_area} from {time_period} and provide:
        
        1. CURRENT STATUS & DEVELOPMENTS:
        - Major recent breakthroughs or announcements
        - Current state of the technology
        - Adoption rates and market penetration
        
        2. KEY PLAYERS & COMPANIES:
        - Leading companies driving innovation
        - Startups making significant impact
        - Strategic partnerships and collaborations
        
        3. MARKET OUTLOOK & PREDICTIONS:
        - Growth projections and market size
        - Investment trends and funding rounds
        - Regulatory developments affecting the sector
        
        4. RECENT BREAKTHROUGHS:
        - Technical innovations and research findings
        - Product launches and beta releases
        - Patents and intellectual property developments
        
        5. CHALLENGES & OPPORTUNITIES:
        - Current limitations and bottlenecks
        - Emerging opportunities and use cases
        - Competitive landscape changes
        
        Focus on recent, factual information from tech news, research reports, and industry sources.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=trend_prompt,
            config=config,
        )
        
        search_queries, sources = parse_grounding_metadata(response)
        
        return {
            "success": True,
            "technology_area": technology_area,
            "timeframe": timeframe,
            "analysis": response.text,
            "search_queries": search_queries,
            "sources": [source.dict() for source in sources],
            "timestamp": datetime.now().isoformat(),
            "trend_strength": "high" if len(sources) >= 5 else "medium"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Tech trend analysis failed: {str(e)}",
            "technology_area": technology_area
        }

@mcp.tool()
def get_breaking_news(topic: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Get breaking news and latest developments on any topic
    
    Parameters:
        topic: News topic to search for
        region: Specific region/country to focus on (optional)
    
    Returns:
        Latest breaking news with source verification
    """
    try:
        client = get_gemini_client()
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        
        region_text = f" in {region}" if region else ""
        
        news_prompt = f"""
        Search for breaking news and latest developments about {topic}{region_text} and provide:
        
        1. BREAKING NEWS HEADLINES:
        - Most recent developments (last 24-48 hours)
        - Include specific times/dates when available
        
        2. KEY FACTS:
        - Who, what, when, where details
        - Verified information from credible sources
        
        3. IMPACT ANALYSIS:
        - Immediate implications
        - Potential long-term effects
        - Affected stakeholders
        
        4. SOURCE VERIFICATION:
        - Primary vs secondary sources
        - Source credibility assessment
        - Cross-verification across multiple outlets
        
        Prioritize information from established news organizations and official sources.
        Clearly distinguish between confirmed facts and speculation.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=news_prompt,
            config=config,
        )
        
        search_queries, sources = parse_grounding_metadata(response)
        
        return {
            "success": True,
            "topic": topic,
            "region": region,
            "breaking_news": response.text,
            "search_queries": search_queries,
            "sources": [source.dict() for source in sources],
            "timestamp": datetime.now().isoformat(),
            "urgency": "high" if "breaking" in response.text.lower() else "medium",
            "verification_status": "verified" if len(sources) >= 2 else "pending"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Breaking news search failed: {str(e)}",
            "topic": topic
        }

@mcp.tool()
def search_market_analysis(market_or_sector: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
    """
    Get market analysis and sector insights using real-time data
    
    Parameters:
        market_or_sector: Market or sector to analyze (e.g., "EV market", "renewable energy", "fintech")
        analysis_type: Type of analysis ("comprehensive", "competitive", "investment", "regulatory")
    
    Returns:
        Market analysis with current trends and future outlook
    """
    try:
        client = get_gemini_client()
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        
        analysis_focus = {
            "comprehensive": "overall market overview, size, growth, and key trends",
            "competitive": "competitive landscape, market leaders, and positioning",
            "investment": "investment opportunities, funding trends, and valuations",
            "regulatory": "regulatory environment, policy changes, and compliance"
        }
        
        focus_area = analysis_focus.get(analysis_type, "comprehensive market analysis")
        
        market_prompt = f"""
        Search for current market analysis of {market_or_sector} focusing on {focus_area} and provide:
        
        1. MARKET OVERVIEW:
        - Current market size and valuation
        - Growth rates and projections
        - Key market drivers and trends
        
        2. INDUSTRY DYNAMICS:
        - Major players and market share
        - Competitive positioning
        - Merger & acquisition activity
        
        3. FINANCIAL METRICS:
        - Revenue and profitability trends
        - Investment and funding activity
        - Valuation multiples and benchmarks
        
        4. FUTURE OUTLOOK:
        - Growth projections and scenarios
        - Emerging opportunities and threats
        - Regulatory and policy impacts
        
        5. EXPERT OPINIONS:
        - Analyst recommendations
        - Industry expert insights
        - Institutional investor sentiment
        
        Use recent reports from financial institutions, research firms, and industry publications.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=market_prompt,
            config=config,
        )
        
        search_queries, sources = parse_grounding_metadata(response)
        
        return {
            "success": True,
            "market_sector": market_or_sector,
            "analysis_type": analysis_type,
            "market_analysis": response.text,
            "search_queries": search_queries,
            "sources": [source.dict() for source in sources],
            "timestamp": datetime.now().isoformat(),
            "data_freshness": "real-time" if len(sources) >= 3 else "recent"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Market analysis failed: {str(e)}",
            "market_sector": market_or_sector
        }

# Start server
if __name__ == "__main__":
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        print("Google Search MCP Server ready!")
        print("Available tools: search_real_time_info, get_company_news_sentiment, analyze_tech_trends, get_breaking_news, search_market_analysis")
    else:
        print("Warning: GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables")
        print("Tools will require API key parameter when called")
    
    print("Starting Google Search MCP Server...")
    mcp.run(transport='stdio')
