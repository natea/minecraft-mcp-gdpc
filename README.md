# Minecraft MCP Server with GDPC and FastMCP

A powerful, extensible platform for programmatic Minecraft world generation and structure building using GDPC, FastMCP, and Supabase.

## Overview

This project combines:

- **GDPC** (Generative Design in Minecraft Python Client) for Minecraft world manipulation
- **FastMCP** (FastAPI-based MCP server) for RESTful API endpoints
- **Supabase** for database, authentication, and storage

The system enables programmatic creation and manipulation of Minecraft worlds, including terrain generation, structure building, and template management.

## Features

- **World Generation**: Create custom terrain using procedural algorithms
- **Structure Building**: Design, save, and place structures using a blueprint system
- **Template Management**: Share and discover building templates
- **Real-time Updates**: Monitor long-running operations via WebSockets
- **User Authentication**: Secure access control with Supabase Auth
- **API Access**: RESTful API for integration with other tools

## Getting Started

### Prerequisites

- Python 3.9+
- Minecraft Java Edition with [Fabric](https://fabricmc.net/) (1.19.4 recommended)
- [Fabric API mod](https://modrinth.com/mod/fabric-api)
- [GDMC HTTP Interface mod](https://github.com/Niels-NTG/gdmc_http_interface)
- [Supabase](https://supabase.com) account

### Installation

1. **Set up Minecraft server with GDMC HTTP Interface mod**

   See the [implementation plan](docs/implementation_plan.md) for detailed instructions

2. **Clone this repository**
   ```bash
   git clone https://github.com/natea/minecraft-mcp-gdpc.git
   cd minecraft-mcp-gdpc
   ```

3. **Create and activate a virtualenv**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials and other settings
   ```

6. **Run the server**
   ```bash
   python src/main.py
   ```

## Documentation

- [Implementation Plan](docs/implementation_plan.md) - Detailed project roadmap
- [API Specification](docs/api_spec.md) - REST API endpoints and usage
- [Database Schema](docs/database_schema.md) - Supabase database structure

## Architecture

The system follows a modular architecture with clear separation of concerns:

1. **FastMCP Server Layer**: API gateway, authentication, and request handling (see [FastMCP](https://gofastmcp.com))
2. **GDPC Integration Layer**: Interface with Minecraft worlds (see [GDPC Python library](https://github.com/avdstaaij/gdpc))
3. **Supabase Integration Layer**: Database, auth, and storage
4. **World Generation Features**: Terrain algorithms and biome management
5. **Structure Building System**: Blueprint format and component library

See the [architecture diagram](docs/architecture_diagram.mmd) for a visual representation.

## Development

### Project Structure

```
minecraft-mcp-gdpc/
├── docs/                       # Documentation
├── src/                        # Source code
│   ├── api/                    # FastMCP API endpoints
│   ├── gdpc_interface/         # GDPC integration layer
│   ├── world_gen/              # World generation algorithms
│   ├── structures/             # Structure building system
│   └── supabase/               # Supabase integration
├── tests/                      # Test suite
├── minecraft-server/           # Minecraft server files
├── config/                     # Configuration files
└── examples/                   # Example scripts and templates
```

### Testing

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run end-to-end tests
pytest tests/e2e
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [GDPC](https://github.com/avdstaaij/gdpc) - Generative Design in Minecraft Python Client
- [FastMCP](https://github.com/jlowin/fastmcp) - FastAPI-based MCP server
- [GDMC HTTP Interface](https://github.com/Niels-NTG/gdmc_http_interface) - Minecraft mod for HTTP interface
- [Supabase](https://supabase.io/) - Open source Firebase alternative