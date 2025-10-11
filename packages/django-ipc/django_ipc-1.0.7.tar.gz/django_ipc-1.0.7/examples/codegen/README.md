# RPC Client Code Generation

This directory contains scripts and tools for generating TypeScript and Python RPC clients from the django-ipc server.

## 🚀 Quick Start

### Using Makefile (Recommended)

From the `examples/` directory:

```bash
# Generate clients with environment configuration
make generate

# Or generate simple clients
make generate-simple

# Clean generated files
make clean

# See all available commands
make help
```

### Manual Generation

```bash
# Generate simple clients
cd codegen
python generate_client.py

# Or generate with environment configuration
python generate_client_with_config.py
```

## 📂 Output Structure

After running generation, clients will be created in:

```
codegen/clients/
├── python/
│   ├── client.py          # Python WebSocket client
│   ├── models.py          # Pydantic models
│   ├── logger.py          # RPC logger with rotation
│   ├── __init__.py        # Package exports
│   ├── requirements.txt   # Python dependencies
│   ├── setup.py          # Package setup
│   └── README.md         # Usage documentation
└── typescript/
    ├── client.ts         # TypeScript WebSocket client
    ├── types.ts          # TypeScript type definitions
    ├── logger.ts         # Browser-friendly logger with consola
    ├── index.ts          # Barrel exports
    ├── package.json      # npm package configuration
    ├── tsconfig.json     # TypeScript configuration
    └── README.md        # Usage documentation
```

## 🔧 Generation Modes

### Simple Mode (`generate_client.py`)

Generates clients without environment-specific configuration. Uses localhost for all environments.

**Best for:**
- Local development
- Simple single-environment setups
- Quick prototyping

### Config Mode (`generate_client_with_config.py`)

Generates clients with multi-environment configuration. Automatically detects environment from:
- Python: `DJANGO_ENV`, `ENV`, or `DEBUG` flag
- TypeScript: `NODE_ENV`, `DJANGO_ENV`, or `ENV`

**Best for:**
- Production deployments
- Multi-environment projects (dev, staging, production)
- Teams working across different environments

**Configured environments:**
```python
development → ws://localhost:8001/ws
production  → wss://api.myapp.com/ws
staging     → wss://staging-api.myapp.com/ws
testing     → ws://localhost:8002/ws
```

## 📝 Generated Features

Both clients include:

### ✅ Type Safety
- Full TypeScript types from Pydantic models
- Python type hints

### ✅ Automatic Logging
- **Python**: JSON logs with rotation to `./client_logs/`
- **TypeScript**: Beautiful console output with [consola](https://github.com/unjs/consola)
- RPC call tracking with correlation IDs
- Performance metrics (duration in ms)
- Success/failure status

### ✅ Environment Detection
- Auto-detect environment from ENV vars
- Explicit environment selection
- Custom URL override

### ✅ WebSocket Management
- Connection/disconnection handling
- Auto-reconnect (configurable)
- Request timeout handling
- Correlation ID tracking

## 💡 Usage Examples

### Python Client

```python
from clients.python import RPCClient

# Auto-detect environment
client = RPCClient.from_env()
await client.connect()

# Call RPC methods
result = await client.send_email(params)

await client.disconnect()
```

### TypeScript Client

```typescript
import { RPCClient } from './clients/typescript';

// Auto-detect environment
const client = RPCClient.fromEnv();
await client.connect();

// Call RPC methods
const result = await client.sendEmail(params);

await client.disconnect();
```

## 🧹 Cleaning Up

```bash
# Remove only generated client directories
make clean-clients

# Remove all generated files + Python cache
make clean
```

## 🔍 Customization

To customize the generation:

1. Edit `generate_client_with_config.py`
2. Modify the `rpc_config` with your endpoints
3. Run `make generate`

Example:
```python
rpc_config = RPCServerConfig(
    production=RPCEndpointConfig(
        websocket_url="wss://your-api.com/ws",
        redis_url="redis://your-redis:6379/0",
    ),
)
```

## 📚 More Information

- [Python Client README](./clients/python/README.md) - Generated after first run
- [TypeScript Client README](./clients/typescript/README.md) - Generated after first run
- [Main Examples README](../README.md) - Parent directory documentation

## 🐛 Troubleshooting

**ImportError: No module named 'django_ipc'**
- Make sure you're in the examples directory
- Run `make install` to install dependencies

**Router not found**
- Ensure `basic/simple_server.py` exists
- Check that the router is properly exported

**Permission denied**
- Make sure you have write permissions in the `codegen/` directory
- Try: `chmod +x generate_client.py`
