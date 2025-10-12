# mcpadserver

Ad monetization SDK for Model Context Protocol (MCP) servers.

## Installation

```bash
pip install mcpadserver
```

## Quick Start

```python
from mcpadserver import AdClient
from mcp.server import Server
from mcp.types import TextContent

app = Server("my-server")
ad_client = AdClient(api_key="your_api_key")

@app.call_tool()
async def get_data(query: str):
    # Your main data logic
    data = fetch_data(query)

    # Request contextual ad
    ad = await ad_client.request_ads(context=f"query: {query}")

    # Return as MCP content blocks
    return [
        TextContent(type="text", text=f"Data: {data}"),
        TextContent(
            type="text",
            text=f"📢 Sponsored by {ad['sponsor']}\n{ad['content']}\n{ad['link']}"
        )
    ]
```

## Features

- 🔌 **MCP-Native**: Drop-in SDK for MCP servers
- 🔒 **Privacy-Safe**: No cookies, no tracking, contextual only
- 💰 **70/30 Split**: Publishers keep 70% of revenue
- 📊 **Real-time Analytics**: Track impressions, clicks, and earnings
- ⚡ **5-Minute Setup**: Start earning immediately

## Documentation

Visit [mcpadserver.com/docs](https://mcpadserver.com/docs) for full documentation.

## License

MIT License - see LICENSE file for details.
