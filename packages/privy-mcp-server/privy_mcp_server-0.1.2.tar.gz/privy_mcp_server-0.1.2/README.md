# Privy.io MCP Server

A Model Context Protocol (MCP) server for [Privy.io](https://privy.io) - the Web3 wallet infrastructure platform. Provides comprehensive access to user management, wallet operations, and blockchain interactions through Claude and other MCP clients.

## Features

### User Management
- **Get User Details**: Retrieve user information by Privy DID including linked accounts, MFA methods, and metadata
- **List Users**: Paginated listing of all users (up to 500 per page)
- **Query by Wallet**: Find users by blockchain wallet address
- **Create Users**: Create new users with linked accounts (email, phone, wallet, OAuth providers)
- **Delete Users**: Remove users and associated data

### Wallet Management
- **Get Wallet**: Retrieve wallet details including address, chain type, and timestamps
- **List Wallets**: Paginated wallet listing with metadata
- **Create Wallets**: Generate wallets for users (Ethereum, Solana, Bitcoin, EVM-compatible chains)
- **Wallet Balance**: Check current wallet balances
- **Transaction History**: Retrieve wallet transaction history with pagination
- **Update Wallets**: Modify wallet metadata and configuration

## Installation

### Prerequisites
- Python 3.10 or higher
- Privy.io account with API credentials

### Quick Start with uvx (Recommended)

The easiest way to use this MCP server is with `uvx`, which automatically fetches the package from PyPI:

```bash
uvx privy-mcp-server
```

No installation needed! Configure your MCP client (see [Usage](#usage) below) and you're ready to go.

### Manual Installation (Development)

For local development:

1. **Clone the repository**:
```bash
git clone https://github.com/incentivai-io/privy-mcp-server.git
cd privy-mcp-server
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -e .
```

4. **Configure environment variables**:
```bash
cp .env.example .env
```

Edit `.env` and add your Privy credentials:
```env
PRIVY_APP_ID=your_app_id_here
PRIVY_APP_SECRET=your_app_secret_here
```

**Get your credentials**: Dashboard → App Settings → Basics on [Privy.io](https://dashboard.privy.io)

## Usage

### Running the Server

Run directly with Python:
```bash
python -m privy_mcp
```

Or use the MCP inspector for testing:
```bash
npx @modelcontextprotocol/inspector python -m privy_mcp
```

For example, from the project directory:
```bash
npx @modelcontextprotocol/inspector python -m privy_mcp
```

### Configuring with Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### Using uvx (Recommended)

```json
{
  "mcpServers": {
    "privy": {
      "command": "uvx",
      "args": ["privy-mcp-server"],
      "env": {
        "PRIVY_APP_ID": "your_app_id_here",
        "PRIVY_APP_SECRET": "your_app_secret_here"
      }
    }
  }
}
```

#### Using local Python installation

```json
{
  "mcpServers": {
    "privy": {
      "command": "python",
      "args": ["-m", "privy_mcp"],
      "env": {
        "PRIVY_APP_ID": "your_app_id_here",
        "PRIVY_APP_SECRET": "your_app_secret_here"
      }
    }
  }
}
```

Restart Claude Desktop after configuration.

## Available Tools

### User Management
- `get_user` - Get user details by Privy DID. Returns user data including linked accounts (email, phone, wallet, OAuth providers), MFA methods, creation timestamps, terms acceptance, and custom metadata
- `list_users` - List all users with pagination support. Returns paginated list of users with their linked accounts, wallets, and metadata (max 500 per page)
- `get_user_by_wallet` - Query and retrieve user information by blockchain wallet address. Supports Ethereum, Solana, Bitcoin, and all EVM-compatible chains
- `create_user` - Create a new user with linked accounts. Supports email, phone, wallet, and 15+ OAuth providers (Apple, Discord, GitHub, Google, Farcaster, Telegram, Twitter, etc.). Optionally creates an embedded wallet
- `delete_user` - Delete a user by Privy DID. This action is permanent and removes all associated data

### Wallet Management
- `get_wallet` - Get wallet details by wallet ID. Returns wallet address, chain type, creation/export/import timestamps, policy IDs, and owner information
- `list_wallets` - List all wallets with pagination. Returns wallet addresses, chain types, and associated metadata
- `create_wallet` - Create or pregenerate a wallet for a user. Supports Ethereum, Solana, Bitcoin, and all EVM-compatible chains
- `get_wallet_balance` - Get the current balance of a wallet
- `get_wallet_transactions` - Get transaction history for a wallet with pagination support
- `update_wallet` - Update wallet metadata and configuration

## Example Queries

Once configured with Claude Desktop, you can ask:

- "List all users in my Privy application"
- "Get user details for DID did:privy:xxx"
- "Find the user with wallet address 0x123..."
- "Create a new user with email user@example.com"
- "Create a wallet for user did:privy:xxx on Solana"
- "Show me all wallets in the system"
- "Get transaction history for wallet xyz"
- "What's the balance of wallet xyz?"
- "Update wallet metadata for wallet xyz"

## API Rate Limits

Privy.io enforces rate limits:
- **User data endpoints**: 500 requests per 10 seconds
- Contact Privy support for rate limit increases

## Authentication

This server uses **HTTP Basic Authentication** with custom headers:
- `Authorization: Basic <base64(app_id:app_secret)>`
- `privy-app-id: <app_id>`

All requests are made over HTTPS to `https://api.privy.io/v1`.

## Supported Blockchain Chains

- Ethereum and all EVM-compatible chains
- Solana
- Bitcoin
- Base, Polygon, Arbitrum, Optimism, and more

## OAuth Providers Supported

Users can link accounts from 15+ providers:
- Apple
- Discord
- Farcaster
- GitHub
- Google
- LinkedIn
- Spotify
- Telegram
- TikTok
- Twitter
- And more

## Development

### Running Tests
```bash
pip install -e ".[dev]"
pytest
```

### Project Structure
```
privy-mcp-server/
├── src/
│   └── privy_mcp/
│       ├── __init__.py      # Package initialization
│       ├── client.py        # Privy API client
│       └── server.py        # MCP server implementation
├── pyproject.toml           # Project dependencies
├── .env.example             # Environment template
└── README.md                # Documentation
```

## Security Considerations

- **Never commit** `.env` file or expose API credentials
- Store credentials securely using environment variables or secrets management
- API credentials have full access to your Privy application
- This is a **defensive security tool** - do not use for malicious purposes
- Review Privy's security documentation: [docs.privy.io/security](https://docs.privy.io/security)

## Troubleshooting

### Authentication Errors
- Verify `PRIVY_APP_ID` and `PRIVY_APP_SECRET` are correct
- Check credentials at Dashboard → App Settings → Basics
- Ensure environment variables are loaded

### Rate Limit Errors
- Reduce request frequency
- Implement exponential backoff
- Contact Privy support for limit increases

### Connection Errors
- Verify internet connectivity
- Check Privy API status
- Ensure firewall allows HTTPS requests

## Resources

- [Privy.io Documentation](https://docs.privy.io)
- [Privy API Reference](https://docs.privy.io/reference/api)
- [MCP Specification](https://modelcontextprotocol.io)
- [Privy Dashboard](https://dashboard.privy.io)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- **Server Issues**: [GitHub Issues](https://github.com/incentivai-io/privy-mcp-server/issues)
- **Privy Support**: hi@privy.io
- **MCP Specification**: [Model Context Protocol](https://modelcontextprotocol.io)
- **Documentation**: [docs.privy.io](https://docs.privy.io)

## Disclaimer

This is an unofficial MCP server implementation. Privy.io has identified MCP as an emerging technology and encourages collaboration. For production use cases, review Privy's official guidance and contact their team at hi@privy.io.

## Acknowledgments

Built on:
- [Privy.io](https://privy.io) - Web3 wallet infrastructure
- [Model Context Protocol](https://modelcontextprotocol.io) - Anthropic's MCP specification
- [HTTPX](https://www.python-httpx.org) - Modern HTTP client for Python
