# Django IPC - Examples

Auto-generated **TypeScript** and **Python** RPC clients with full logging support.

---

## 🚀 Quick Start

### 1. Generate Clients

```bash
# Using Makefile (recommended)
make generate

# Or directly with Python
cd codegen
python generate_client_with_config.py
```

### 2. Use Generated Clients

**Python:**
```python
from clients.python import RPCClient

# Auto-detect environment from DJANGO_ENV
client = RPCClient.from_env()
await client.connect()

# Call RPC methods - automatically logged!
result = await client.create_user(params)
await client.disconnect()
```

**TypeScript:**
```typescript
import { RPCClient } from './clients/typescript';

// Auto-detect from NODE_ENV
const client = RPCClient.fromEnv();
await client.connect();

// Call RPC methods - automatically logged!
const result = await client.createUser(params);
await client.disconnect();
```

---

## 📂 Structure

```
examples/
├── Makefile              # 🔧 Build automation
├── README.md             # This file
├── codegen/              # 📦 Code generation
│   ├── simple_server.py           # Example RPC server
│   ├── generate_client.py         # Simple generation
│   ├── generate_client_with_config.py  # With environment config
│   ├── README.md                  # Detailed docs
│   └── clients/                   # Generated output
│       ├── python/                # Python client
│       └── typescript/            # TypeScript client
├── pyproject.toml        # Python dependencies
└── poetry.lock          # Locked dependencies
```

---

## 🛠️ Makefile Commands

```bash
make generate         # Generate clients (with env config)
make generate-simple  # Generate without config
make clean           # Remove generated files
make clean-clients   # Remove only client dirs
make help            # Show all commands
```

---

## 📦 Generated Clients

### Python Client (10 files)

```
clients/python/
├── client.py          # WebSocket RPC client with logger
├── models.py          # Pydantic models
├── logger.py          # ClientLogger with JSON logs & rotation
├── __init__.py        # Package exports
├── requirements.txt   # Dependencies
├── setup.py          # Package setup
├── pyproject.toml    # Modern packaging
├── README.md         # Usage documentation
├── .gitignore        # Git exclusions
└── .editorconfig     # Editor config
```

**Features:**
- ✅ Full type hints
- ✅ Auto environment detection
- ✅ JSON structured logging
- ✅ Log rotation (10MB files)
- ✅ Correlation ID tracking
- ✅ Performance metrics

### TypeScript Client (12 files)

```
clients/typescript/
├── client.ts         # WebSocket RPC client with logger
├── types.ts          # TypeScript interfaces
├── logger.ts         # ClientLogger with consola
├── index.ts          # Barrel exports
├── package.json      # npm config
├── tsconfig.json     # TypeScript config
├── README.md         # Usage docs
├── .eslintrc.json    # ESLint config
├── .prettierrc       # Prettier config
├── .gitignore        # Git exclusions
└── .editorconfig     # Editor config
```

**Features:**
- ✅ Full TypeScript types
- ✅ Auto environment detection
- ✅ Beautiful console output (consola)
- ✅ SessionStorage persistence
- ✅ Correlation ID tracking
- ✅ Performance metrics

---

## 🎯 Logging Features

Both clients include automatic RPC call logging:

### Python
- **Structured JSON logs** in `./client_logs/client_rpc.log`
- **Automatic rotation** at 10MB
- **Correlation IDs** for request tracking
- **Performance metrics** (duration in ms)
- **Success/failure status**

### TypeScript
- **Beautiful console output** with emoji and colors
- **SessionStorage persistence** (auto-clears on tab close)
- **In-memory log storage** for debugging
- **Export/download logs** as JSON
- **Correlation IDs** for request tracking

---

## 🌍 Environment Detection

Both clients auto-detect environment:

**Priority:**
1. `DJANGO_ENV` / `NODE_ENV` (Python / TypeScript)
2. `ENV` (fallback)
3. `DEBUG` flag (Python only)
4. Default: `development`

**Supported aliases:**
- `dev`, `devel`, `develop`, `local` → `development`
- `prod` → `production`
- `stage` → `staging`
- `test` → `testing`

**Example:**
```bash
# Python
DJANGO_ENV=production python my_script.py

# TypeScript
NODE_ENV=production npm start
```

---

## 📝 Example: Custom Logger Config

### Python
```python
from clients.python import RPCClient
from clients.python.logger import ClientLoggerConfig

config = ClientLoggerConfig(
    log_dir="./my_logs",
    level="DEBUG",
    log_rpc_calls=True
)

client = RPCClient(logger_config=config)
```

### TypeScript
```typescript
import { RPCClient } from './clients/typescript';

const client = new RPCClient(undefined, {
    level: 4,  // DEBUG
    logRPCCalls: true,
    useSessionStorage: true
});
```

---

## 📚 Documentation

- **Codegen README**: [`codegen/README.md`](codegen/README.md) - Detailed generation guide
- **Python Client**: `clients/python/README.md` (after generation)
- **TypeScript Client**: `clients/typescript/README.md` (after generation)

---

## 🔧 Customization

Edit [`codegen/generate_client_with_config.py`](codegen/generate_client_with_config.py) to customize:

```python
rpc_config = RPCServerConfig(
    production=RPCEndpointConfig(
        websocket_url="wss://your-api.com/ws",
        redis_url="redis://your-redis:6379/0",
    ),
)
```

Then regenerate:
```bash
make generate
```

---

## 🧹 Cleanup

```bash
# Remove generated clients only
make clean-clients

# Full cleanup (clients + cache)
make clean
```

---

## 💡 Tips

### Regenerate After Changes
```bash
# After modifying simple_server.py
make clean && make generate
```

### Check Generated Code Quality
```bash
# Python
cd clients/python
python -m py_compile *.py

# TypeScript
cd clients/typescript
npm install
npm run build
npm run lint
```

### View Logs
```python
# Python - logs auto-saved to ./client_logs/
import json
with open('client_logs/client_rpc.log') as f:
    for line in f:
        print(json.loads(line))
```

```typescript
// TypeScript - view in console
client.logger?.printLogs();
client.logger?.downloadLogs('my-logs.json');
```

---

## 🐛 Troubleshooting

**Import errors?**
```bash
# Ensure dependencies installed
poetry install
```

**Generation fails?**
```bash
# Check simple_server.py is in codegen/
ls codegen/simple_server.py
```

**Can't find generated clients?**
```bash
# They're in codegen/clients/
ls codegen/clients/python/
ls codegen/clients/typescript/
```

---

**Happy coding! 🚀**

Generated by django-ipc codegen.
