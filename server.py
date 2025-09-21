"""
Banking Tools MCP Server Example

This server provides tools for banking operations including:
- Customer data retrieval from PostgreSQL database
- Fund holdings analysis from Excel files
- Credit worthiness assessment using web searches
- Health check endpoints

The server demonstrates how to build complex banking tools using FastMCP framework.
"""

import asyncio
import aiohttp
import os
import pandas as pd
from typing import Any, Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Banking Tools Server")

# Database configuration from environment
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'banking_db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '5'))
DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '10'))

# Construct database URL
DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine with environment configuration
engine = create_async_engine(
    DB_URL,
    echo=bool(os.getenv('DB_ECHO', 'False').lower() == 'true'),
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Configure file paths from environment
DATA_DIR = os.getenv('DATA_DIR', 'data/holdings')

# Health check endpoints
@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify server status and its dependencies.

    Returns:
        Dict containing status of various components and server uptime
    """
    try:
        # Test database connection
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "database": db_status
        }
    }

@mcp.tool()
async def get_customer_info(customer_id: str) -> Dict[str, Any]:
    """Retrieve customer information from the PostgreSQL database.

    Args:
        customer_id: Unique identifier for the customer

    Returns:
        Dictionary containing customer details including:
        - Personal information
        - Account details
        - Contact information

    Raises:
        HTTPException: If customer not found or database error occurs
    """
    try:
        async with async_session() as session:
            # Example query - adjust according to your schema
            query = text("""
                SELECT c.*, a.account_number, a.account_type, a.balance
                FROM customers c
                LEFT JOIN accounts a ON c.id = a.customer_id
                WHERE c.id = :customer_id
            """)
            result = await session.execute(query, {"customer_id": customer_id})
            customer_data = result.mappings().first()

            if not customer_data:
                raise HTTPException(status_code=404, detail="Customer not found")

            return dict(customer_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@mcp.tool()
async def get_fund_holdings(customer_id: str, month: str) -> Dict[str, Any]:
    """Read customer's fund holdings from Excel file for a specific month.

    Args:
        customer_id: Unique identifier for the customer
        month: Month for which to retrieve holdings (format: YYYY-MM)

    Returns:
        Dictionary containing:
        - Total holdings value
        - List of fund positions
        - Performance metrics

    Raises:
        HTTPException: If file not found or invalid data
    """
    try:
        # Use configured data directory
        file_path = os.path.join(DATA_DIR, month, f"customer_{customer_id}.xlsx")
        
        # Read Excel file using pandas
        df = pd.read_excel(file_path)
        
        # Calculate holdings summary
        holdings_summary = {
            "total_value": float(df["value"].sum()),
            "positions": df.to_dict(orient="records"),
            "asset_allocation": df.groupby("asset_class")["value"].sum().to_dict()
        }
        
        return holdings_summary
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Holdings data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing holdings: {str(e)}")

@mcp.tool()
async def check_credit_worthiness(
    customer_name: str,
    company_name: Optional[str] = None
) -> Dict[str, Any]:
    """Check customer's credit worthiness using web searches for sanctions and criminal records.

    Args:
        customer_name: Full name of the customer
        company_name: Optional company name if customer represents a business

    Returns:
        Dictionary containing:
        - Credit score estimation
        - Risk factors found
        - Sanctions list matches
        - News sentiment analysis

    Note:
        This is a simplified example. In production, you would want to:
        - Use proper APIs for sanctions checking
        - Implement more sophisticated name matching
        - Add rate limiting and caching
        - Include proper error handling for API failures
    """
    async with aiohttp.ClientSession() as session:
        try:
            # Example: Check sanctions lists (implement with proper API in production)
            sanctions_check = await session.get(
                "https://api.sanctions-check.example",
                params={"name": customer_name}
            )
            
            # Example: Get news sentiment (implement with proper API in production)
            news_check = await session.get(
                "https://api.news-sentiment.example",
                params={"entity": customer_name}
            )

            # Combine and analyze results
            # This is a simplified example - implement proper scoring logic
            return {
                "credit_score": 85,  # Example score
                "risk_factors": ["none"],
                "sanctions_matches": [],
                "news_sentiment": "positive",
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error checking credit worthiness: {str(e)}"
            )

@mcp.tool()
async def assess_customer(customer_id: str, month: str) -> Dict[str, Any]:
    """Comprehensive customer assessment combining all available data sources.

    This tool demonstrates how to combine multiple data sources and tools
    to create a comprehensive customer assessment.

    Args:
        customer_id: Unique identifier for the customer
        month: Month for which to assess holdings (format: YYYY-MM)

    Returns:
        Dictionary containing:
        - Customer information
        - Fund holdings
        - Credit assessment
        - Overall risk score
        - Recommendations

    Example:
        ```python
        result = await assess_customer("12345", "2025-09")
        print(f"Customer risk score: {result['risk_score']}")
        ```
    """
    # Gather data from all sources in parallel
    customer_info, holdings, credit_info = await asyncio.gather(
        get_customer_info(customer_id),
        get_fund_holdings(customer_id, month),
        check_credit_worthiness(customer_info["full_name"])
    )

    # Calculate overall risk score (example logic)
    risk_score = calculate_risk_score(
        credit_score=credit_info["credit_score"],
        total_holdings=holdings["total_value"],
        account_history=customer_info
    )

    return {
        "customer_info": customer_info,
        "holdings": holdings,
        "credit_assessment": credit_info,
        "risk_score": risk_score,
        "recommendations": generate_recommendations(risk_score),
        "assessment_date": datetime.utcnow().isoformat()
    }

def calculate_risk_score(
    credit_score: float,
    total_holdings: float,
    account_history: Dict[str, Any]
) -> float:
    """Calculate customer risk score based on multiple factors.

    This is a simplified example. In production, implement proper risk modeling.
    """
    # Example risk calculation logic
    base_score = credit_score * 0.5
    holdings_factor = min(total_holdings / 1000000, 1) * 25
    history_factor = 25  # Based on account history analysis

    return base_score + holdings_factor + history_factor

def generate_recommendations(risk_score: float) -> List[str]:
    """Generate business recommendations based on risk score.

    This is a simplified example. In production, implement proper recommendation logic.
    """
    if risk_score >= 90:
        return ["Eligible for premium services", "Consider wealth management offering"]
    elif risk_score >= 70:
        return ["Standard services approved", "Monitor for premium eligibility"]
    else:
        return ["Enhanced due diligence required", "Regular monitoring recommended"]

def print_tool_info(tool_name: str, tool_func: callable) -> None:
    """Helper function to print formatted tool information."""
    print(f"\n📌 {tool_name}")
    if tool_func.__doc__:
        # Get the first line of the docstring
        desc = tool_func.__doc__.strip().split('\n')[0]
        print(f"   {desc}")

def print_resource_info() -> None:
    """Helper function to print available resources and their configuration."""
    print("\n🔧 Available Resources:")
    print(f"\n1. Database Connection")
    print(f"   - Host: {DB_HOST}:{DB_PORT}")
    print(f"   - Database: {DB_NAME}")
    print(f"   - Pool Size: {DB_POOL_SIZE} (Max Overflow: {DB_MAX_OVERFLOW})")
    
    print(f"\n2. File Storage")
    print(f"   - Data Directory: {DATA_DIR}")
    
    print(f"\n3. External Services")
    print(f"   - Sanctions Check API")
    print(f"   - News Sentiment API")

if __name__ == "__main__":
    print("\n🏦 Banking Tools MCP Server")
    print("==========================")
    
    # Print available tools
    print("\n🛠️ Available Tools:")
    
    # Get all tools from the MCP instance
    tools = [
        (name, func) for name, func in globals().items()
        if callable(func) and hasattr(func, '__mcp_tool__')
    ]
    
    # Print information for each tool
    for tool_name, tool_func in sorted(tools):
        print_tool_info(tool_name, tool_func)
    
    # Print resource information
    print_resource_info()
    
    print("\n📋 Server Usage:")
    print("   Run 'uvicorn server:mcp --reload' to start the server")
    
    # Optional: Start the server
    mcp.run(transport="http", host="127.0.0.1", port=8000)