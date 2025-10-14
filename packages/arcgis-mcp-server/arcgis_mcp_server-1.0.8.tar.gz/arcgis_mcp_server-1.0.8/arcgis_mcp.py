# arcgis_mcp.py

import logging, json, os, sys, io
from pathlib import Path
from typing import Optional
from arcgis.gis import GIS
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# --- Professional Logging Setup ---
def setup_unicode_logging():
    Path("logs").mkdir(exist_ok=True)
    logger = logging.getLogger('ArcGIS_MCP_Server')
    if logger.hasHandlers(): logger.handlers.clear()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    if os.getenv("MCP_RUNNING_AS_TOOL") != "true":
        try:
            handler = logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'))
        except (TypeError, ValueError):
            handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    file_handler = logging.FileHandler('logs/arcgis_server.log', mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_unicode_logging()
mcp = FastMCP(name="arcgis-mcp-server")

# --- Core Logic: Secure ArcGIS Connection ---
def connect_to_arcgis() -> GIS:
    portal_url, username, password = os.getenv('ARCGIS_URL'), os.getenv('ARCGIS_USERNAME'), os.getenv('ARCGIS_PASSWORD')
    if not all([portal_url, username, password]):
        raise ConnectionError("ArcGIS credentials were not provided. The user needs to authenticate.")
    try:
        gis = GIS(portal_url, username, password)
        logger.info(f"Successfully connected to {gis.properties.portalName} as '{username}'.")
        return gis
    except Exception as e:
        raise ConnectionError(f"Portal connection failed: {str(e)}")

# --- THIS IS THE FINAL, CRITICAL FIX FOR THE AI ---
@mcp.tool(
    name="search_arcgis_organization_content",
    description="Searches a connected ArcGIS Portal or ArcGIS Online organization for content such as feature layers, web maps, dashboards, or other GIS items. Use this tool anytime a user asks to find, search for, or look up geographic data or maps."
)
def search_content(
    query: str,
    item_type: Optional[str] = "Feature Service",
    owner: Optional[str] = None,
    max_results: int = 10,
) -> str:
    """
    Searches for content in the user's authenticated ArcGIS environment.

    :param query: The keyword or phrase to search for in item titles, tags, or descriptions. For example: "roads" or "health facilities in Riyadh".
    :param item_type: The specific type of ArcGIS item to find. Common examples are "Feature Service", "Web Map", "Dashboard", or "Shapefile". Defaults to "Feature Service".
    :param owner: The username of the person who owns the content you are searching for.
    :param max_results: The maximum number of items to return in the search results. Defaults to 10.
    """
    logger.info(f"Executing search: query='{query}', item_type='{item_type}'")
    try:
        gis = connect_to_arcgis()
        search_query = f'({query} OR title:"{query}")' + (f' AND owner:"{owner}"' if owner else "")
        results = gis.content.search(query=search_query, item_type=item_type, max_items=max_results)
        if not results: return json.dumps({"status": "success", "message": "No items found."})
        formatted = [{"title": i.title, "type": i.type, "owner": i.owner, "summary": BeautifulSoup(i.snippet or "", "html.parser").get_text().strip(), "url": i.homepage or f"{gis.url}/home/item.html?id={i.id}"} for i in results]
        return json.dumps({"status": "success", "results": formatted}, default=str)
    except ConnectionError as e:
        return json.dumps({"status": "error", "message": "Could not connect to ArcGIS. Please ensure you have authenticated."})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {str(e)}"})

# --- Main Execution Block ---
def run_server_main():
    logger.info("[SUCCESS] ArcGIS MCP Server is starting...")
    mcp.run()

if __name__ == "__main__":
    run_server_main()