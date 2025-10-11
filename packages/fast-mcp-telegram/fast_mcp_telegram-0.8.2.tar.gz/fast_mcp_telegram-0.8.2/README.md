<img alt="Hero image" src="https://github.com/user-attachments/assets/635236f6-b776-41c7-b6e5-0dd14638ecc1" />

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://github.com/leshchenko1979/fast-mcp-telegram)

**Fast MCP Telegram Server** - Production-ready Telegram integration for AI assistants with comprehensive search, messaging, and direct API access capabilities.

## 🌐 Demo

1. Open https://tg-mcp.redevest.ru/setup to begin the authentication flow.
2. After finishing, you'll receive a ready-to-use `mcp.json` with your Bearer token. 
3. Use the config with your MCP client to check out this MCP server capabilities.
4. Or try the HTTP‑MTProto Bridge right away with curl (replace TOKEN):
```bash
curl -X POST "https://tg-mcp.redevest.ru/mtproto-api/messages.SendMessage" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"params": {"peer": "me", "message": "Hello from Demo!"}}'
```

## 📖 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [🏗️ Server Modes](#️-server-modes)
- [🌐 HTTP-MTProto Bridge](#-http-mtproto-bridge)
- [📚 Documentation](#-documentation)
- [🔒 Security](#-security)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Multi-User Authentication** | Production-ready Bearer token auth with session isolation and LRU cache management |
| 🌐 **HTTP-MTProto Bridge** | Direct curl access to any Telegram API method with entity resolution and safety guardrails |
| 🔍 **Intelligent Search** | Global & per-chat message search with multi-query support and intelligent deduplication |
| 🏗️ **Dual Transport** | Seamless development (stdio) and production (HTTP) deployment support |
| 📁 **Secure File Handling** | Rich media sharing with SSRF protection, size limits, and album support |
| 💬 **Advanced Messaging** | Send, edit, reply with formatting, file attachments, and phone number messaging |
| 📊 **Unified Session Management** | Single configuration system for setup and server, with multi-account support |
| 👥 **Smart Contact Discovery** | Search users, groups, channels with uniform entity schemas and profile enrichment |
| ⚡ **High Performance** | Async operations, parallel queries, connection pooling, and memory optimization |
| 🛡️ **Production Reliability** | Auto-reconnect, structured logging, comprehensive error handling |
| 🎯 **AI-Optimized** | Literal parameter constraints and LLM-friendly API design |
| 🌍 **Web Setup Interface** | Browser-based authentication flow with immediate config generation |

## 🚀 Quick Start

### 1. Install from PyPI
```bash
pip install fast-mcp-telegram
```

### 2. Authenticate with Telegram
```bash
fast-mcp-telegram-setup --api-id="your_api_id" --api-hash="your_api_hash" --phone-number="+123456789"
```

**🌐 Prefer a browser?** Run the server and open `/setup` to authenticate and download a ready‑to‑use `mcp.json`.

### 3. Configure Your MCP Client

**STDIO Mode (Development with Cursor IDE):**
```json
{
  "mcpServers": {
    "telegram": {
      "command": "fast-mcp-telegram",
      "env": {
        "API_ID": "your_api_id",
        "API_HASH": "your_api_hash",
        "PHONE_NUMBER": "+123456789"
      }
    }
  }
}
```

**HTTP_AUTH Mode (Production with Bearer Token):**
```json
{
  "mcpServers": {
    "telegram": {
      "url": "https://your-server.com",
      "headers": {
        "Authorization": "Bearer AbCdEfGh123456789KLmnOpQr..."
      }
    }
  }
}
```

### 4. Start Using!
```json
{"tool": "search_messages_globally", "params": {"query": "hello", "limit": 5}}
{"tool": "send_message", "params": {"chat_id": "me", "message": "Hello from AI!"}}
```

**📝 For detailed installation instructions, see [Installation Guide](docs/Installation.md)**

## 🏗️ Server Modes

| Mode | Transport | Authentication | Use Case |
|------|----------|----------------|----------|
| **STDIO** | stdio | Disabled | Development with Cursor IDE |
| **HTTP_NO_AUTH** | HTTP | Disabled | Development HTTP server |
| **HTTP_AUTH** | HTTP | Required (Bearer token) | Production deployment |

## 🌐 HTTP-MTProto Bridge

**Direct curl access to any Telegram API method** - Execute any Telegram MTProto method via HTTP requests with automatic entity resolution and safety guardrails.

### Quick Examples
```bash
# Send message with automatic entity resolution
curl -X POST "https://your-domain.com/mtproto-api/messages.SendMessage" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "params": {"peer": "@username", "message": "Hello from curl!"},
        "resolve": true
      }'

# Send message using params_json (works with n8n and other tools)
curl -X POST "https://your-domain.com/mtproto-api/messages.SendMessage" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "params_json": "{\"peer\": \"@username\", \"message\": \"Hello from curl!\"}",
        "resolve": true
      }'

# Get message history with peer resolution
curl -X POST "https://your-domain.com/mtproto-api/messages.getHistory" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "params": {"peer": "me", "limit": 10},
        "resolve": true
      }'
```

**📖 For complete MTProto Bridge documentation, see [MTProto Bridge Guide](docs/MTProto-Bridge.md)**

## 📚 Documentation

- **[Installation Guide](docs/Installation.md)** - Detailed installation and configuration
- **[Deployment Guide](docs/Deployment.md)** - Docker deployment and production setup
- **[Tools Reference](docs/Tools-Reference.md)** - Complete tools documentation with examples
- **[Search Guidelines](docs/Search-Guidelines.md)** - Search best practices and limitations
- **[Operations Guide](docs/Operations.md)** - Health monitoring and troubleshooting
- **[Project Structure](docs/Project-Structure.md)** - Code organization and architecture
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup and contribution guidelines

## 🔒 Security

**Key Security Features:**
- Bearer token authentication with session isolation
- SSRF protection for file downloads
- Dangerous method blocking with opt-in override
- Session file security and automatic cleanup

**📖 For complete security information, see [SECURITY.md](SECURITY.md)**

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for:

- Development setup instructions
- Testing guidelines
- Code quality standards
- Pull request process

**Quick Start for Contributors:**
1. Fork the repository
2. Read the [Contributing Guide](CONTRIBUTING.md)
3. Create a feature branch
4. Make your changes and add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram API library
- [Model Context Protocol](https://modelcontextprotocol.io) - Protocol specification

---

<div align="center">

**Made with ❤️ for the AI automation community**

[⭐ Star us on GitHub](https://github.com/leshchenko1979/fast-mcp-telegram) • [💬 Join our community](https://t.me/mcp_telegram)

</div>

---

mcp-name: io.github.leshchenko1979/fast-mcp-telegram
