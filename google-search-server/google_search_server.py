# Google Search MCP Server with Grounding
# Provides real-time news, sentiment analysis, and company information

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
import os
from datetime import datetime, timedelta
import json
import re

# Create MCP server instance
mcp = FastMCP(name="GoogleSearchServer")

class SearchResult(BaseModel):
    query: str = Field(..., description="The search query used")
    response_text: str = Field(..., description="The AI-generated response based on search results")
    web_queries: List[str] = Field(..., description="Actual search queries executed")
    sources: List[Dict[str, str]] = Field(..., description="Source URLs and titles")
    grounding_supports: List[Dict[str, Any]] = Field(..., description="Text segments with source mapping")

class CompanyNewsAnalysis(BaseModel):
    company: str = Field(..., description="Company name analyzed")
    overall_sentiment: str = Field(..., description="Overall sentiment: positive, negative, or neutral")
    key_findings: List[str] = Field(..., description="Key findings from recent news")
    recent_developments: List[str] = Field(..., description="Recent company developments")
    market_impact: str = Field(..., description="Potential market impact analysis")
    news_sources: List[Dict[str, str]] = Field(..., description="News source URLs and titles")
    analysis_date: str = Field(..., description="When this analysis was performed")

def get_gemini_client(api_key: Optional[str] = None) -> genai.Client:
    """Get Gemini client with API key"""
    if api_key:
        return genai.Client(api_key=api_key)
    
    # Try environment variable
    env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if env_key:
        return genai.Client(api_key=env_key)
    
    raise ValueError("No Gemini API key provided and no GEMINI_API_KEY or GOOGLE_API_KEY found in environment variables")

def extract_grounding_metadata(response) -> Dict[str, Any]:
    """Extract grounding metadata from Gemini response"""
    grounding_data = {
        "web_queries": [],
        "sources": [],
        "grounding_supports": []
    }
    
    try:
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                metadata = candidate.grounding_metadata
                
                # Extract web search queries
                if hasattr(metadata, 'web_search_queries'):
                    grounding_data["web_queries"] = metadata.web_search_queries
                
                # Extract grounding chunks (sources)
                if hasattr(metadata, 'grounding_chunks'):
                    for chunk in metadata.grounding_chunks:
                        if hasattr(chunk, 'web'):
                            grounding_data["sources"].append({
                                "url": chunk.web.uri,
                                "title": chunk.web.title
                            })
                
                # Extract grounding supports (text segments with sources)
                if hasattr(metadata, 'grounding_supports'):
                    for support in metadata.grounding_supports:
                        grounding_data["grounding_supports"].append({
                            "text": support.segment.text,
                            "start_index": support.segment.start_index,
                            "end_index": support.segment.end_index,
                            "source_indices": list(support.grounding_chunk_indices)
                        })
    except Exception as e:
        print(f"Warning: Could not extract grounding metadata: {e}")
    
    return grounding_data

@mcp.tool()
def search_real_time_news(
    query: str, 
    api_key: Optional[str] = None,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search for real-time news and information using Google Search with Gemini grounding
    
    Parameters:
        query: Search query (e.g., "Tesla latest news", "AI industry trends 2024")
        api_key: Gemini API key (optional, will read from environment if not provided)
        max_results: Maximum number of results to include in analysis
    
    Returns:
        Real-time search results with AI analysis, sources, and grounding information
    """
    try:
        client = get_gemini_client(api_key)
        
        # Configure grounding tool
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        
        # Enhanced prompt for better analysis
        enhanced_query = f"""
        Please search for and analyze: {query}
        
        Provide a comprehensive summary that includes:
        1. Latest developments and news
        2. Key facts and important details
        3. Timeline of recent events if applicable
        4. Different perspectives from multiple sources
        5. Any potential implications or impacts
        
        Please cite all sources and provide factual, up-to-date information.
        """
        
        # Make the grounded request
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=enhanced_query,
            config=config
        )
        
        # Extract grounding metadata
        grounding_data = extract_grounding_metadata(response)
        
        return {
            "success": True,
            "search_result": SearchResult(
                query=query,
                response_text=response.text,
                web_queries=grounding_data["web_queries"],
                sources=grounding_data["sources"][:max_results],
                grounding_supports=grounding_data["grounding_supports"]
            ).dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Search failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def analyze_company_sentiment(
    company_name: str,
    api_key: Optional[str] = None,
    time_period: str = "last 7 days",
    domains: str = "all"
) -> Dict[str, Any]:
    """
    Analyze sentiment and latest news about a specific company across all domains
    
    Parameters:
        company_name: Name of the company to analyze (e.g., "Apple", "Tesla", "Microsoft")
        api_key: Gemini API key (optional, will read from environment if not provided)
        time_period: Time period for news analysis (e.g., "last 7 days", "last month")
        domains: News domains to search (e.g., "tech,business,finance" or "all")
    
    Returns:
        Comprehensive sentiment analysis with recent news, market impact, and sources
    """
    try:
        client = get_gemini_client(api_key)
        
        # Configure grounding tool
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        
        # Create comprehensive search query
        domain_filter = ""
        if domains != "all":
            domain_filter = f" site:techcrunch.com OR site:reuters.com OR site:bloomberg.com OR site:wsj.com OR site:cnbc.com"
        
        search_query = f"""
        Analyze the latest news and sentiment about {company_name} from the {time_period}.
        
        Please provide:
        
        1. OVERALL SENTIMENT ANALYSIS:
        - Determine if the overall sentiment is POSITIVE, NEGATIVE, or NEUTRAL
        - Explain the reasoning behind this sentiment classification
        
        2. KEY RECENT DEVELOPMENTS:
        - Major news events, announcements, or changes
        - Product launches, partnerships, acquisitions
        - Financial results or guidance updates
        - Leadership changes or strategic shifts
        
        3. MARKET AND BUSINESS IMPACT:
        - How these developments might affect the company's business
        - Potential impact on stock price or market position
        - Industry implications or competitive effects
        
        4. NEWS SOURCE DIVERSITY:
        - Include perspectives from technology, business, financial, and general news sources
        - Look for both mainstream and specialized industry coverage
        
        5. FACTUAL ACCURACY:
        - Focus on verifiable facts and confirmed developments
        - Distinguish between rumors and confirmed information
        
        Search for: {company_name} news {time_period} sentiment analysis business impact{domain_filter}
        """
        
        # Make the grounded request
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=search_query,
            config=config
        )
        
        # Extract grounding metadata
        grounding_data = extract_grounding_metadata(response)
        
        # Parse the response to extract structured sentiment analysis
        response_text = response.text
        
        # Extract sentiment using regex and keywords
        sentiment = "neutral"
        if re.search(r'\bpositive\b|\boptimistic\b|\bbullish\b|\bstrong\b|\bgrowth\b', response_text.lower()):
            sentiment = "positive"
        elif re.search(r'\bnegative\b|\bpessimistic\b|\bbearish\b|\bweak\b|\bdecline\b|\bconcerns\b', response_text.lower()):
            sentiment = "negative"
        
        # Extract key findings (look for bullet points or numbered lists)
        key_findings = []
        developments = []
        
        lines = response_text.split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if line:
                if any(keyword in line.lower() for keyword in ['key', 'major', 'important', 'significant']):
                    current_section = "findings"
                elif any(keyword in line.lower() for keyword in ['development', 'news', 'announcement', 'launch']):
                    current_section = "developments"
                elif line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line):
                    if current_section == "findings":
                        key_findings.append(line.lstrip('- •').lstrip('0123456789. '))
                    elif current_section == "developments":
                        developments.append(line.lstrip('- •').lstrip('0123456789. '))
        
        # Extract market impact section
        market_impact = "Impact analysis pending - please review full response for details"
        if "impact" in response_text.lower():
            impact_start = response_text.lower().find("impact")
            if impact_start != -1:
                impact_section = response_text[impact_start:impact_start+500]
                market_impact = impact_section[:impact_section.find('\n\n')] if '\n\n' in impact_section else impact_section
        
        return {
            "success": True,
            "analysis": CompanyNewsAnalysis(
                company=company_name,
                overall_sentiment=sentiment,
                key_findings=key_findings[:5] if key_findings else ["Please review full response for detailed findings"],
                recent_developments=developments[:5] if developments else ["Please review full response for recent developments"],
                market_impact=market_impact,
                news_sources=grounding_data["sources"][:10],
                analysis_date=datetime.now().isoformat()
            ).dict(),
            "full_response": response_text,
            "search_queries": grounding_data["web_queries"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Sentiment analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def search_industry_trends(
    industry: str,
    api_key: Optional[str] = None,
    focus_area: str = "latest trends and developments"
) -> Dict[str, Any]:
    """
    Search for latest trends and developments in a specific industry
    
    Parameters:
        industry: Industry to analyze (e.g., "artificial intelligence", "electric vehicles", "fintech")
        api_key: Gemini API key (optional, will read from environment if not provided)
        focus_area: Specific focus area (e.g., "emerging technologies", "market trends", "regulatory changes")
    
    Returns:
        Industry trend analysis with latest developments, key players, and market insights
    """
    try:
        client = get_gemini_client(api_key)
        
        # Configure grounding tool
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        
        search_query = f"""
        Analyze the latest trends and developments in the {industry} industry, focusing on {focus_area}.
        
        Please provide:
        1. Current market trends and patterns
        2. Emerging technologies or innovations
        3. Key players and their recent activities
        4. Market size and growth projections
        5. Regulatory or policy changes
        6. Investment and funding activities
        7. Future outlook and predictions
        
        Search for recent information from the last 3 months for the most current insights.
        """
        
        # Make the grounded request
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=search_query,
            config=config
        )
        
        # Extract grounding metadata
        grounding_data = extract_grounding_metadata(response)
        
        return {
            "success": True,
            "industry_analysis": {
                "industry": industry,
                "focus_area": focus_area,
                "analysis": response.text,
                "sources": grounding_data["sources"],
                "search_queries": grounding_data["web_queries"],
                "analysis_date": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Industry trend analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def search_competitor_analysis(
    company_name: str,
    api_key: Optional[str] = None,
    include_startups: bool = True
) -> Dict[str, Any]:
    """
    Analyze a company's competitive landscape and recent competitor developments
    
    Parameters:
        company_name: Name of the company to analyze competitors for
        api_key: Gemini API key (optional, will read from environment if not provided)
        include_startups: Whether to include startup competitors and emerging players
    
    Returns:
        Competitive analysis with key competitors, recent developments, and market positioning
    """
    try:
        client = get_gemini_client(api_key)
        
        # Configure grounding tool
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        
        startup_clause = "including both established companies and emerging startups" if include_startups else "focusing on established market players"
        
        search_query = f"""
        Analyze the competitive landscape for {company_name}, {startup_clause}.
        
        Please provide:
        1. Main direct competitors and their recent activities
        2. Indirect competitors and potential disruptors
        3. Recent competitive moves (product launches, partnerships, acquisitions)
        4. Market share and positioning analysis
        5. Competitive advantages and disadvantages
        6. Emerging threats or opportunities in the competitive landscape
        7. Recent funding or investment activities by competitors
        
        Focus on developments from the last 6 months for current competitive intelligence.
        """
        
        # Make the grounded request
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=search_query,
            config=config
        )
        
        # Extract grounding metadata
        grounding_data = extract_grounding_metadata(response)
        
        return {
            "success": True,
            "competitive_analysis": {
                "target_company": company_name,
                "analysis": response.text,
                "sources": grounding_data["sources"],
                "search_queries": grounding_data["web_queries"],
                "includes_startups": include_startups,
                "analysis_date": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Competitor analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# Start server
if __name__ == "__main__":
    # Check if environment variable is set
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        print("Gemini API key found in environment variables")
        print("Google Search MCP Server ready!")
    else:
        print("No Gemini API key found in environment variables")
        print("API key parameter required when calling tools")
    
    print("Starting Google Search MCP Server with Grounding...")
    mcp.run(transport='stdio')
