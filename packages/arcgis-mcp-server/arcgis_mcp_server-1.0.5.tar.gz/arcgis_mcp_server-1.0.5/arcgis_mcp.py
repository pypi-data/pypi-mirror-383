# arcgis_mcp.py

# --- Core Imports ---
import logging
import json
import os
import sys
import io
from pathlib import Path
from typing import Optional

# --- Library Imports ---
from arcgis.gis import GIS
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# --- Initial Setup ---
load_dotenv()

# --- Professional Logging Setup ---
def setup_unicode_logging():
    """Sets up robust, unicode-aware logging to both console and file."""
    Path("logs").mkdir(exist_ok=True)
    logger = logging.getLogger('ArcGIS_MCP_Server')
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    if os.getenv("MCP_RUNNING_AS_TOOL") != "true":
        try:
            # Use a wrapper for robust UTF-8 handling on Windows
            console_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            console_handler = logging.StreamHandler(console_stream)
        except (TypeError, ValueError):
            console_handler = logging.StreamHandler(sys.stdout) # Fallback for other OS
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    file_handler = logging.FileHandler('logs/arcgis_server.log', mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_unicode_logging()

# --- MCP Server Initialization ---
mcp = FastMCP(name="arcgis-mcp-server")

# --- Core Logic: Secure ArcGIS Connection ---
def connect_to_arcgis() -> GIS:
    """
    Establishes a secure connection to ArcGIS by checking for credentials
    in the environment, raising an error if they are not found to trigger
    the client's authentication prompt.
    """
    portal_url = os.getenv('ARCGIS_URL')
    username = os.getenv('ARCGIS_USERNAME')
    password = os.getenv('ARCGIS_PASSWORD')

    if not all([portal_url, username, password]):
        logger.error("Connection failed: Missing ArcGIS credentials in environment.")
        raise ConnectionError("ArcGIS credentials were not provided. The user needs to authenticate.")

    try:
        logger.info(f"Attempting to connect to portal: {portal_url}...")
        gis = GIS(portal_url, username, password)
        logger.info(f"Successfully established connection to {gis.properties.portalName} as '{username}'.")
        return gis
    except Exception as e:
        logger.error(f"Failed to establish portal connection: {e}", exc_info=True)
        raise ConnectionError(f"Portal connection failed: {str(e)}")


# --- AI Tool Definition (with Enhanced Description) ---
@mcp.tool(
    name="search_content",
    description="Finds items like feature layers, web maps, and other content in an ArcGIS Portal or ArcGIS Online organization. Use this tool to search for geographic data by name, type, or owner."
)
def search_content(
    query: str,
    item_type: Optional[str] = "Feature Service",
    owner: Optional[str] = None,
    max_results: int = 10,
) -> str:
    """
    Searches for content in the user's authenticated ArcGIS environment.

    :param query: The search term for item titles, tags, or descriptions.
    :param item_type: The type of item to search for (e.g., "Feature Service", "Web Map").
    :param owner: The specific owner of the content to find.
    :param max_results: The maximum number of results to return.
    """
    logger.info(f"Executing search: query='{query}', item_type='{item_type}'")
    try:
        gis = connect_to_arcgis()
        search_query = f'({query} OR title:"{query}")'
        if owner:
            search_query += f' AND owner:"{owner}"'
        search_results = gis.content.search(query=search_query, item_type=item_type, max_items=max_results, outside_org=False)

        if not search_results:
            return json.dumps({"status": "success", "message": "No items found."})

        # Format results for clarity
        formatted_results = []
        for item in search_results:
            snippet = BeautifulSoup(item.snippet or "", "html.parser").get_text().strip()
            formatted_results.append({
                "title": item.title,
                "type": item.type,
                "owner": item.owner,
                "summary": snippet,
                "url": item.homepage or f"{gis.url}/home/item.html?id={item.id}"
            })
        return json.dumps({"status": "success", "results": formatted_results}, default=str)
    except ConnectionError as e:
        logger.error(f"Search failed due to connection error: {e}")
        return json.dumps({"status": "error", "message": "Could not connect to ArcGIS. Please ensure you have authenticated."})
    except Exception as e:
        logger.error(f"An unexpected error occurred during search: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {str(e)}"})


# --- Main Execution Block for the Entry Point ---
def run_server_main():
    """Main function to initialize and run the MCP server."""
    logger.info("[SUCCESS] ArcGIS MCP Server is starting...")
    mcp.run()

if __name__ == "__main__":
    run_server_main()