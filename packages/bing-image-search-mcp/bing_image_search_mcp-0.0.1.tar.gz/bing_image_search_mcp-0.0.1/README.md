# bing-image-search-mcp


MCP Server of Bing Web Search With No Access Key Requested

This MCP server is a mcp wrapper of pypi package Bing Image Search Web URL (https://github.com/AI-Hub-Admin/bing-image-search-mcp) which easy to use Bing Image Search APIs.


# Features


# Install
```
pip install bing-image-search-mcp
```


# MCP Integration
```
{
    "mcpServers": {
        "bing-image-search-mcp": {
            "command": "uv",
            "args": ["--directory", "/path_to_folder/finance-agent-mcp-server/src/finance-agent-mcp-server", "run", "server.py"]
        }
    }
}
```


```
{
    "mcpServers": {
        "bing-image-search-mcp": {
            "command": "uv",
            "args": ["--directory", "/path_to_folder/finance-agent-mcp-server/src/finance-agent-mcp-server", "run", "server.py"]
        }
    }
}
```

{
    "mcpServers": {
        "bing-image-search-mcp": {
            "command": "uvx",
            "args": ["your-package-entrypoint-name"] 
        }
    }
}



## 本地: 
uv --directory /path_to_folder/finance-agent-mcp-server/src/finance-agent-mcp-server run server.py

