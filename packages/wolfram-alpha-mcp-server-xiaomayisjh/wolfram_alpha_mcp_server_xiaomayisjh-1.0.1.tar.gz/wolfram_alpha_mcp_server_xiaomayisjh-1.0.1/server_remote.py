#!/usr/bin/env python3
"""
Wolfram Alpha MCP Server - Remote Version
支持远程调用的 Wolfram Alpha MCP 服务器
"""

from mcp.server.fastmcp import FastMCP
import os
import requests
import urllib.parse
import anyio
from hashlib import md5
from urllib.parse import urlsplit, urlencode, unquote_plus
import logging
import json
import asyncio
from typing import AsyncGenerator, Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("Wolfram Alpha Mobile API Integration")

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

def perform_mobile_query(query_input, format_type="plaintext", output_type="json", podstate=None, stream=False):
    """
    Perform query using Wolfram Alpha mobile API
    
    @query_input: The input query string
    @format_type: Response format (plaintext, html, etc.)
    @output_type: Output type (json, xml, etc.)
    @podstate: Specific pod state to request (optional)
    @stream: Whether to return streaming response
    """
    try:
        query_part = f"input={urllib.parse.quote_plus(query_input)}"
        if podstate:
            query_part += f"&podstate={urllib.parse.quote_plus(podstate)}"
        query_part += f"&format={format_type}&output={output_type}"
        
        logger.info(f"Querying Wolfram Alpha: {query_input[:50]}...")
        
        if stream:
            # For streaming, we'll simulate chunked response
            return perform_streaming_query(query_input, query_part)
        else:
            r = s.get(craft_signed_url(f"https://{SERVER}/v2/query.jsp?{query_part}"))
            
            if r.status_code == 200:
                logger.info("Query successful")
                return r.text
            else:
                error_msg = f"Error({r.status_code}) happened!\n{r.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Error querying Wolfram Alpha: {str(e)}"
        logger.error(error_msg)
        return error_msg

def perform_streaming_query(query_input, query_part):
    """
    Perform streaming query - simulates chunked response for better UX
    """
    try:
        r = s.get(craft_signed_url(f"https://{SERVER}/v2/query.jsp?{query_part}"))
        
        if r.status_code == 200:
            logger.info("Streaming query successful")
            # Parse the response and create streaming chunks
            response_data = r.text
            
            # If it's JSON, try to parse and stream individual results
            if query_part.endswith("output=json"):
                try:
                    data = json.loads(response_data)
                    return create_streaming_chunks(data, query_input)
                except json.JSONDecodeError:
                    # If not valid JSON, return as plain text chunks
                    return create_text_chunks(response_data)
            else:
                return create_text_chunks(response_data)
        else:
            error_msg = f"Error({r.status_code}) happened!\n{r.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Error in streaming query: {str(e)}"
        logger.error(error_msg)
        return error_msg

def create_streaming_chunks(data, query_input):
    """
    Create streaming chunks from JSON response
    """
    chunks = []
    
    # Add initial chunk with query info
    chunks.append({
        "type": "query_info",
        "content": f"Processing query: {query_input}",
        "timestamp": anyio.current_time()
    })
    
    # Process pods if available
    if isinstance(data, dict) and "queryresult" in data:
        queryresult = data["queryresult"]
        
        if "pods" in queryresult:
            for i, pod in enumerate(queryresult["pods"]):
                chunk = {
                    "type": "pod",
                    "pod_index": i,
                    "title": pod.get("title", ""),
                    "content": pod.get("subpods", [{}])[0].get("plaintext", ""),
                    "timestamp": anyio.current_time()
                }
                chunks.append(chunk)
        
        # Add final result chunk
        chunks.append({
            "type": "final_result",
            "content": "Query completed successfully",
            "timestamp": anyio.current_time()
        })
    
    return chunks

def create_text_chunks(text):
    """
    Create streaming chunks from plain text response
    """
    chunks = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if line.strip():  # Skip empty lines
            chunk = {
                "type": "text_chunk",
                "chunk_index": i,
                "content": line.strip(),
                "timestamp": anyio.current_time()
            }
            chunks.append(chunk)
    
    return chunks

@mcp.tool()
async def wolfram_alpha_query(query: str):
    """
    Query Wolfram Alpha using mobile API for scientific and factual information
    
    Args:
        query: The input query string
    """
    return await anyio.to_thread.run_sync(perform_mobile_query, query, "plaintext", "json")

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

@mcp.tool()
async def wolfram_streaming_query(
    query: str,
    format_type: str = "plaintext",
    output_type: str = "json",
    podstate: str = None
) -> str:
    """
    Query Wolfram Alpha with streaming response for real-time results
    
    Args:
        query: The input query string
        format_type: Response format (plaintext, html, etc.) - default: plaintext
        output_type: Output type (json, xml, etc.) - default: json
        podstate: Specific pod state to request (optional)
    
    Returns:
        JSON string containing streaming chunks with type, content, and metadata
    """
    try:
        # Get streaming chunks
        chunks = await anyio.to_thread.run_sync(
            perform_mobile_query, query, format_type, output_type, podstate, True
        )
        
        # Convert chunks to JSON string for MCP compatibility
        return json.dumps({
            "streaming_chunks": chunks,
            "query": query,
            "total_chunks": len(chunks)
        }, ensure_ascii=False, indent=2)
            
    except Exception as e:
        error_chunk = {
            "type": "error",
            "content": f"Error in streaming query: {str(e)}",
            "timestamp": anyio.current_time()
        }
        return json.dumps({
            "streaming_chunks": [error_chunk],
            "query": query,
            "total_chunks": 1,
            "error": True
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def wolfram_streaming_step_by_step(query: str) -> str:
    """
    Get step-by-step solution from Wolfram Alpha with streaming response
    
    Args:
        query: The mathematical query string
    
    Returns:
        JSON string containing streaming chunks with step-by-step solution
    """
    try:
        # Get streaming chunks for step-by-step solution
        chunks = await anyio.to_thread.run_sync(
            perform_mobile_query, 
            query, 
            "plaintext", 
            "json", 
            "Solution__Step-by-step+solution",
            True
        )
        
        # Convert chunks to JSON string for MCP compatibility
        return json.dumps({
            "streaming_chunks": chunks,
            "query": query,
            "total_chunks": len(chunks),
            "solution_type": "step_by_step"
        }, ensure_ascii=False, indent=2)
            
    except Exception as e:
        error_chunk = {
            "type": "error",
            "content": f"Error in streaming step-by-step query: {str(e)}",
            "timestamp": anyio.current_time()
        }
        return json.dumps({
            "streaming_chunks": [error_chunk],
            "query": query,
            "total_chunks": 1,
            "error": True,
            "solution_type": "step_by_step"
        }, ensure_ascii=False, indent=2)


def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Wolfram Alpha MCP Server...")
    mcp.run()

if __name__ == "__main__":
    main()
