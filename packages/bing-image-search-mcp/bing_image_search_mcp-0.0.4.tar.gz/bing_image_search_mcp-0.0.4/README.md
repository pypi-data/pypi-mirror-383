# bing-image-search-mcp

MCP Server of Bing Web Search With No Access Key Requested

This MCP server is a mcp wrapper of pypi package Bing Image Search Web URL (https://github.com/AI-Hub-Admin/bing-image-search-mcp) which easy to use Bing Image Search APIs.

# Features


# Install
```
pip install bing-image-search-mcp
```

# MCP Integration

### OneKey MCP Router
StreamingHttpConnection 

Beta Test Keys 
```
DEEPNLP_ONEKEY_ROUTER_ACCESS=BETA_TEST_KEY_OCT_2025
```
You can also generate your personal non-contraint keys here [OneKey](https://www.deepnlp.org/workspace/keys) and Seee the onekey mcp router Demo [Google Maps MCP Server OneKey Example](https://www.deepnlp.org/store/mcp-server/map/pub-google-maps/google-maps) for reference on how to use one access key to access commercial MCPs.


```
{
    "mcpServers": {
		"deepnlp-onekey-bing-image-search": {
			"url": "https://agent.deepnlp.org/mcp?server_name=bing-image-search-mcp&onekey=BETA_TEST_KEY_OCT_2025"
		}
    }
}
```


### UVX
```
{
    "mcpServers": {
        "bing-image-search-mcp": {
            "command": "uvx",
            "args": ["bing-image-search-mcp"]
        }
    }
}
```


### GitHub Source Running Localing
```
git clone https://github.com/AI-Hub-Admin/bing-image-search-mcp
cd bing-image-search-mcp

```

Run From Your Local Folder

```
{
    "mcpServers": {
        "bing-image-search-mcp": {
            "command": "uv",
            "args": ["--directory", "/path_to_folder/bing-image-search-mcp/src/bing_image_search_mcp", "run", "server.py"]
        }
    }
}
```

