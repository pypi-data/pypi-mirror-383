#!/usr/bin/env python3
"""
Metabase FastMCP Server

A FastMCP server that provides tools to interact with Metabase databases,
execute queries, manage cards, and work with collections.
"""

import asyncio
import logging
import os
import sys
from enum import Enum
from typing import Any, Optional

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Metabase configuration from environment variables
METABASE_URL = os.getenv("METABASE_URL")
METABASE_USER_EMAIL = os.getenv("METABASE_USER_EMAIL")
METABASE_PASSWORD = os.getenv("METABASE_PASSWORD")
METABASE_API_KEY = os.getenv("METABASE_API_KEY")

if not METABASE_URL or (
    not METABASE_API_KEY and (not METABASE_USER_EMAIL or not METABASE_PASSWORD)
):
    raise ValueError(
        "METABASE_URL is required, and either METABASE_API_KEY or both METABASE_USER_EMAIL and METABASE_PASSWORD must be provided"
    )


# Authentication method enum
class AuthMethod(Enum):
    SESSION = "session"
    API_KEY = "api_key"


# Initialize FastMCP server
mcp = FastMCP(name="metabase-mcp")


class MetabaseClient:
    """HTTP client for Metabase API operations"""

    def __init__(self):
        self.base_url = METABASE_URL.rstrip("/")
        self.session_token: str | None = None
        self.api_key: str | None = METABASE_API_KEY
        self.auth_method = AuthMethod.API_KEY if METABASE_API_KEY else AuthMethod.SESSION
        self.client = httpx.AsyncClient(timeout=30.0)

        logger.info(f"Using {self.auth_method.value} authentication method")

    async def _get_headers(self) -> dict[str, str]:
        """Get appropriate authentication headers"""
        headers = {"Content-Type": "application/json"}

        if self.auth_method == AuthMethod.API_KEY and self.api_key:
            headers["X-API-KEY"] = self.api_key
        elif self.auth_method == AuthMethod.SESSION:
            if not self.session_token:
                await self._get_session_token()
            if self.session_token:
                headers["X-Metabase-Session"] = self.session_token

        return headers

    async def _get_session_token(self) -> str:
        """Get Metabase session token for email/password authentication"""
        if self.auth_method == AuthMethod.API_KEY and self.api_key:
            return self.api_key

        if not METABASE_USER_EMAIL or not METABASE_PASSWORD:
            raise ValueError("Email and password required for session authentication")

        login_data = {"username": METABASE_USER_EMAIL, "password": METABASE_PASSWORD}

        response = await self.client.post(f"{self.base_url}/api/session", json=login_data)

        if response.status_code != 200:
            error_data = response.json() if response.content else {}
            raise Exception(f"Authentication failed: {response.status_code} - {error_data}")

        session_data = response.json()
        self.session_token = session_data.get("id")
        logger.info("Successfully obtained session token")
        return self.session_token

    async def request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        """Make authenticated request to Metabase API"""
        url = f"{self.base_url}/api{path}"
        headers = await self._get_headers()

        logger.debug(f"Making {method} request to {path}")

        response = await self.client.request(method=method, url=url, headers=headers, **kwargs)

        if not response.is_success:
            error_data = response.json() if response.content else {}
            error_message = (
                f"API request failed with status {response.status_code}: {response.text}"
            )
            logger.warning(f"{error_message} - {error_data}")
            raise Exception(error_message)

        logger.debug(f"Successful response from {path}")
        return response.json()

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global client instance
metabase_client = MetabaseClient()


# =============================================================================
# Tool Definitions - Database Operations
# =============================================================================

@mcp.tool
async def list_databases() -> dict[str, Any]:
    """
    List all databases configured in Metabase.
    
    Returns:
        A dictionary containing all available databases with their metadata.
    """
    try:
        result = await metabase_client.request("GET", "/database")
        return result
    except Exception as e:
        logger.error(f"Error listing databases: {e}")
        raise


@mcp.tool
async def list_tables(database_id: int) -> str:
    """
    List all tables in a specific database.
    
    Args:
        database_id: The ID of the database to query.
    
    Returns:
        Formatted markdown table showing table details.
    """
    try:
        result = await metabase_client.request("GET", f"/database/{database_id}/metadata")
        
        # Extract and format tables
        tables = result.get("tables", [])
        formatted_tables = [
            {
                "table_id": table.get("id"),
                "display_name": table.get("display_name"),
                "description": table.get("description") or "No description",
                "entity_type": table.get("entity_type")
            }
            for table in tables
        ]
        
        # Sort for better readability
        formatted_tables.sort(key=lambda x: x.get("display_name", ""))
        
        # Generate markdown output
        markdown_output = f"# Tables in Database {database_id}\n\n"
        markdown_output += f"**Total Tables:** {len(formatted_tables)}\n\n"
        
        if not formatted_tables:
            markdown_output += "*No tables found in this database.*\n"
            return markdown_output
        
        # Create markdown table
        markdown_output += "| Table ID | Display Name | Description | Entity Type |\n"
        markdown_output += "|----------|--------------|-------------|--------------|\n"
        
        for table in formatted_tables:
            table_id = table.get("table_id", "N/A")
            display_name = table.get("display_name", "N/A")
            description = table.get("description", "No description")
            entity_type = table.get("entity_type", "N/A")
            
            # Escape pipe characters
            description = description.replace("|", "\\|")
            display_name = display_name.replace("|", "\\|")
            
            markdown_output += f"| {table_id} | {display_name} | {description} | {entity_type} |\n"
        
        return markdown_output
        
    except Exception as e:
        logger.error(f"Error listing tables for database {database_id}: {e}")
        raise


@mcp.tool
async def get_table_fields(table_id: int, limit: int = 20) -> dict[str, Any]:
    """
    Get all fields/columns in a specific table.
    
    Args:
        table_id: The ID of the table.
        limit: Maximum number of fields to return (default: 20).
    
    Returns:
        Dictionary with field metadata, truncated if necessary.
    """
    try:
        result = await metabase_client.request("GET", f"/table/{table_id}/query_metadata")
        
        # Apply field limiting
        if limit > 0 and "fields" in result and len(result["fields"]) > limit:
            total_fields = len(result["fields"])
            result["fields"] = result["fields"][:limit]
            result["_truncated"] = True
            result["_total_fields"] = total_fields
            result["_limit_applied"] = limit
        
        return result
    except Exception as e:
        logger.error(f"Error getting table fields for table {table_id}: {e}")
        raise


# =============================================================================
# Tool Definitions - Query Operations
# =============================================================================

@mcp.tool
async def execute_query(
    database_id: int,
    query: str,
    native_parameters: Optional[list[dict[str, Any]]] = None
) -> dict[str, Any]:
    """
    Execute a native SQL query against a Metabase database.
    
    Args:
        database_id: The ID of the database to query.
        query: The SQL query to execute.
        native_parameters: Optional parameters for the query.
    
    Returns:
        Query execution results.
    """
    try:
        payload = {
            "database": database_id,
            "type": "native",
            "native": {"query": query}
        }

        if native_parameters:
            payload["native"]["parameters"] = native_parameters

        result = await metabase_client.request("POST", "/dataset", json=payload)
        return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise


# =============================================================================
# Tool Definitions - Card/Question Operations
# =============================================================================

@mcp.tool
async def list_cards() -> dict[str, Any]:
    """
    List all saved questions/cards in Metabase.
    
    Returns:
        Dictionary containing all cards with their metadata.
    """
    try:
        result = await metabase_client.request("GET", "/card")
        return result
    except Exception as e:
        logger.error(f"Error listing cards: {e}")
        raise


@mcp.tool
async def execute_card(
    card_id: int,
    parameters: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Execute a saved Metabase question/card and retrieve results.
    
    Args:
        card_id: The ID of the card to execute.
        parameters: Optional parameters for the card execution.
    
    Returns:
        Card execution results.
    """
    try:
        payload = {}
        if parameters:
            payload["parameters"] = parameters

        result = await metabase_client.request("POST", f"/card/{card_id}/query", json=payload)
        return result
    except Exception as e:
        logger.error(f"Error executing card {card_id}: {e}")
        raise


@mcp.tool
async def create_card(
    name: str,
    database_id: int,
    query: str,
    description: Optional[str] = None,
    collection_id: Optional[int] = None,
    visualization_settings: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Create a new question/card in Metabase.
    
    Args:
        name: Name of the card.
        database_id: ID of the database to query.
        query: SQL query for the card.
        description: Optional description.
        collection_id: Optional collection to place the card in.
        visualization_settings: Optional visualization configuration.
    
    Returns:
        The created card object.
    """
    try:
        payload = {
            "name": name,
            "database_id": database_id,
            "dataset_query": {
                "database": database_id,
                "type": "native",
                "native": {"query": query},
            },
            "display": "table",
            "visualization_settings": visualization_settings or {},
        }

        if description:
            payload["description"] = description
        if collection_id is not None:
            payload["collection_id"] = collection_id

        result = await metabase_client.request("POST", "/card", json=payload)
        return result
    except Exception as e:
        logger.error(f"Error creating card: {e}")
        raise


# =============================================================================
# Tool Definitions - Collection Operations
# =============================================================================

@mcp.tool
async def list_collections() -> dict[str, Any]:
    """
    List all collections in Metabase.
    
    Returns:
        Dictionary containing all collections with their metadata.
    """
    try:
        result = await metabase_client.request("GET", "/collection")
        return result
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise


@mcp.tool
async def create_collection(
    name: str,
    description: Optional[str] = None,
    color: Optional[str] = None,
    parent_id: Optional[int] = None,
) -> dict[str, Any]:
    """
    Create a new collection in Metabase.
    
    Args:
        name: Name of the collection.
        description: Optional description.
        color: Optional color for the collection.
        parent_id: Optional parent collection ID.
    
    Returns:
        The created collection object.
    """
    try:
        payload = {"name": name}

        if description:
            payload["description"] = description
        if color:
            payload["color"] = color
        if parent_id is not None:
            payload["parent_id"] = parent_id

        result = await metabase_client.request("POST", "/collection", json=payload)
        return result
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise


# Cleanup handler
async def cleanup():
    """Clean up resources on shutdown"""
    await metabase_client.close()


def main():
    """
    Main entry point for the Metabase MCP server.
    
    Supports multiple transport methods:
    - STDIO (default): For IDE integration
    - SSE: Server-Sent Events for web apps
    - HTTP: Standard HTTP for API access
    """
    try:
        # Get configuration from environment
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))

        # Parse transport argument
        transport = "stdio"  # default
        if "--sse" in sys.argv:
            transport = "sse"
        elif "--http" in sys.argv:
            transport = "streamable-http"
        elif "--stdio" in sys.argv:
            transport = "stdio"

        logger.info(f"Starting Metabase MCP server with {transport} transport")

        # Run server with appropriate transport
        if transport in ["sse", "streamable-http"]:
            logger.info(f"Server will be available at http://{host}:{port}")
            mcp.run(transport=transport, host=host, port=port)
        else:
            mcp.run(transport=transport)

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        asyncio.run(cleanup())


if __name__ == "__main__":
    main()
