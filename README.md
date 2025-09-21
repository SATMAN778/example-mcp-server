# Banking Tools MCP Server

A Model Context Protocol (MCP) server implementation that provides banking-related tools and utilities for UiPath automation workflows. This server offers tools for customer data retrieval, fund holdings analysis, credit worthiness assessment, and comprehensive customer risk evaluation.

## Features

- 🏦 **Customer Information Retrieval**
  - Async PostgreSQL database integration
  - Efficient connection pooling
  - Comprehensive error handling

- 📊 **Fund Holdings Analysis**
  - Excel file processing with pandas
  - Asset allocation calculations
  - Historical holdings tracking

- 🔍 **Credit Assessment**
  - Sanctions list checking
  - News sentiment analysis
  - Risk score calculation

- 🏥 **Health Monitoring**
  - Database connectivity checks
  - Service status monitoring
  - Dependency health tracking

## Installation

1. Create a Python virtual environment using `uv`:
```bash
uv venv
```

2. Install dependencies:
```bash
uv pip install fastapi sqlalchemy pandas python-dotenv asyncpg aiohttp
```

3. Set up environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
notepad .env  # or use your preferred editor
```

## Configuration

The server is configured via environment variables. Create a `.env` file with the following settings:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=banking_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_ECHO=False

# File Storage Configuration
DATA_DIR=data/holdings

# API Endpoints
SANCTIONS_API_URL=https://api.sanctions-check.example
NEWS_API_URL=https://api.news-sentiment.example
```

## Usage

### Running the Server

```bash
# Start the server
uvicorn server:mcp --reload
```

### Available Tools

1. **get_customer_info**
   ```python
   result = await get_customer_info("12345")
   print(f"Customer details: {result}")
   ```

2. **get_fund_holdings**
   ```python
   holdings = await get_fund_holdings("12345", "2025-09")
   print(f"Total value: ${holdings['total_value']}")
   ```

3. **check_credit_worthiness**
   ```python
   credit = await check_credit_worthiness("John Doe", "Acme Corp")
   print(f"Credit score: {credit['credit_score']}")
   ```

4. **assess_customer**
   ```python
   assessment = await assess_customer("12345", "2025-09")
   print(f"Risk score: {assessment['risk_score']}")
   print(f"Recommendations: {assessment['recommendations']}")
   ```

### Health Check

The server provides a health check endpoint that monitors:
- Server status
- Database connectivity
- Service dependencies

## Database Schema

The server expects the following database schema:

```sql
CREATE TABLE customers (
    id VARCHAR PRIMARY KEY,
    full_name VARCHAR NOT NULL,
    -- Add other customer fields
);

CREATE TABLE accounts (
    id VARCHAR PRIMARY KEY,
    customer_id VARCHAR REFERENCES customers(id),
    account_number VARCHAR NOT NULL,
    account_type VARCHAR NOT NULL,
    balance DECIMAL NOT NULL
    -- Add other account fields
);
```

## File Structure

Fund holdings data should be organized as follows:
```
data/
└── holdings/
    └── YYYY-MM/
        └── customer_ID.xlsx
```

Each Excel file should contain columns:
- `value`: Holding value
- `asset_class`: Type of asset
- Other relevant fund information

## Error Handling

The server implements comprehensive error handling:
- Database connectivity issues
- Missing or invalid data
- API service failures
- File access problems

All errors are returned with appropriate HTTP status codes and detailed error messages.

## Production Considerations

1. **Security**
   - Use proper authentication/authorization
   - Implement rate limiting
   - Secure sensitive endpoints
   - Use production-grade credentials

2. **Performance**
   - Configure appropriate pool sizes
   - Implement caching where needed
   - Monitor resource usage

3. **Monitoring**
   - Set up proper logging
   - Configure alerting
   - Monitor database performance

## Development

### Adding New Tools

1. Create a new async function with proper typing
2. Add comprehensive docstrings
3. Use the `@mcp.tool()` decorator
4. Implement error handling
5. Update tests and documentation

Example:
```python
@mcp.tool()
async def new_banking_tool() -> Dict[str, Any]:
    """Tool description and documentation."""
    try:
        # Implementation
        return {"result": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add/update tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
