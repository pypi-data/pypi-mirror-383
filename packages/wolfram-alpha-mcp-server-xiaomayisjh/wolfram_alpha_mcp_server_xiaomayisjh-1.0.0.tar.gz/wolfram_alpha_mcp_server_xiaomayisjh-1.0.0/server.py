from mcp.server.fastmcp import FastMCP
import os
import requests
import urllib.parse
import anyio
from hashlib import md5
from urllib.parse import urlsplit, urlencode, unquote_plus

# Create the MCP server
mcp = FastMCP("Wolfram Alpha Integration")

# Mobile app configuration
HEADERS = {"User-Agent": "Wolfram Android App"}
APPID = "3H4296-5YPAGQUJK7"  # Mobile app AppId
SERVER = "api.wolframalpha.com"
SIG_SALT = "vFdeaRwBTVqdc5CL"  # Mobile app salt

# Create session with headers
s = requests.Session()
s.headers.update(HEADERS)

def calc_sig(query):
    """
    Calculates WA sig value(md5(salt + concatenated_query)) with pre-known salt
    
    @query
    In format of "input=...&arg1=...&arg2=..."
    """
    params = []
    for param in query.split("&"):
        if "=" in param:
            key, value = param.split("=", 1)
            params.append([key, value])
    
    params.sort(key=lambda x: x[0])  # sort by the key

    sig_string = SIG_SALT
    # Concatenate query together
    for key, val in params:
        sig_string += key + val
    sig_string = sig_string.encode("utf-8")
    return md5(sig_string).hexdigest().upper()

def craft_signed_url(url):
    """
    Craft valid signed URL if parameters known
    
    @query
    In format of "https://server/path?input=...&arg1=...&arg2=..."
    """
    (scheme, netloc, path, query, _) = urlsplit(url)
    _query = {"appid": APPID}

    # Parse query parameters safely
    if query:
        for param in query.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                _query[unquote_plus(key)] = unquote_plus(value)
    
    query_string = urlencode(_query)
    _query.update({"sig": calc_sig(query_string)})  # Calculate signature of all query before we set "sig" up.
    return f"{scheme}://{netloc}{path}?{urlencode(_query)}"

def perform_mobile_query(query_input, format_type="plaintext", output_type="json", podstate=None):
    """
    Perform query using Wolfram Alpha mobile API
    
    @query_input: The input query string
    @format_type: Response format (plaintext, html, etc.)
    @output_type: Output type (json, xml, etc.)
    @podstate: Specific pod state to request (optional)
    """
    query_part = f"input={urllib.parse.quote_plus(query_input)}"
    if podstate:
        query_part += f"&podstate={urllib.parse.quote_plus(podstate)}"
    query_part += f"&format={format_type}&output={output_type}"
    
    try:
        r = s.get(craft_signed_url(f"https://{SERVER}/v2/query.jsp?{query_part}"))
        if r.status_code == 200:
            return r.text
        else:
            raise Exception(f"Error({r.status_code}) happened!\n{r.text}")
    except Exception as e:
        return f"Error querying Wolfram Alpha: {str(e)}"

@mcp.tool()
async def wolfram_alpha_query(query: str):
    """Query Wolfram Alpha using mobile API for scientific and factual information"""
    return await anyio.to_thread.run_sync(perform_query, query)

@mcp.tool()
async def wolfram_mobile_query(
    query: str,
    format_type: str = "plaintext",
    output_type: str = "json",
    podstate: str = None
):
    """
    Query Wolfram Alpha using mobile API with custom format options
    
    Args:
        query: The input query string
        format_type: Response format (plaintext, html, etc.) - default: plaintext
        output_type: Output type (json, xml, etc.) - default: json
        podstate: Specific pod state to request (optional)
    """
    return await anyio.to_thread.run_sync(
        perform_mobile_query, query, format_type, output_type, podstate
    )

@mcp.tool()
async def wolfram_step_by_step(query: str):
    """
    Get step-by-step solution from Wolfram Alpha
    
    Args:
        query: The mathematical query string
    """
    return await anyio.to_thread.run_sync(
        perform_mobile_query, 
        query, 
        "plaintext", 
        "json", 
        "Solution__Step-by-step+solution"
    )

def perform_query(query):
    query_part = f"input={urllib.parse.quote_plus(query)}&format=plaintext&output=json"
    try:
        r = s.get(craft_signed_url(f"https://{SERVER}/v2/query.jsp?{query_part}"))
        if r.status_code == 200:
            return r.text
        else:
            raise Exception(f"Error({r.status_code}) happened!\n{r.text}")
    except Exception as e:
        return f"Error querying Wolfram Alpha: {str(e)}"

if __name__ == "__main__":
    mcp.run()

