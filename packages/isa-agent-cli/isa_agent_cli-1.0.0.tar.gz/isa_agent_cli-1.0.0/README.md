# isA Agent - Smart Agent Service

A production-ready, modular agent service built with LangGraph for intelligent conversation workflows, MCP tool integration, and comprehensive streaming capabilities.

## 🎯 Features

- **🤖 Smart Agent Architecture**: LangGraph-based agent with reasoning, tool execution, and response nodes
- **🔄 Real-Time Streaming**: Server-Sent Events (SSE) streaming with comprehensive event types
- **🔧 MCP Integration**: Full Model Context Protocol support for tool discovery and execution
- **🧠 Multi-Model Support**: Flexible model integration via ISA Model service
- **📊 Durable Execution**: PostgreSQL-backed conversation persistence and checkpointing
- **🔐 Production Ready**: API-first design with authentication, rate limiting, and health monitoring
- **🐳 Docker Support**: Optimized Docker images (API mode: ~400MB, Local mode: ~3GB)
- **🔍 Service Discovery**: Consul integration for automatic service registration
- **🎨 Multiple Graph Types**: Specialized graphs for research, coding, and conversation workflows
- **🔌 Hardware Integration**: Support for IoT devices and sensor data processing
- **👥 Human-in-Loop**: Interactive approval and feedback system for critical decisions
- **📈 Advanced Tracing**: Comprehensive tracing with LangSmith integration
- **💳 Billing Integration**: Usage tracking and billing service support
- **🏗️ SDK Support**: Client SDK for easy integration

## 🏗️ Architecture

```
isA_Agent/
├── app/                          # Core application
│   ├── api/                     # API endpoints
│   │   ├── auth/               # Authentication
│   │   ├── chat.py             # Chat endpoints
│   │   ├── session.py          # Session management
│   │   ├── execution.py        # Execution control
│   │   ├── tracing.py          # Tracing & observability
│   │   └── graphs.py           # Graph management API
│   ├── components/              # Service components
│   │   ├── mcp_service.py      # MCP integration
│   │   ├── billing_service.py  # Billing & usage
│   │   ├── user_service.py     # User management
│   │   └── consul_discovery.py # Service discovery client
│   ├── graphs/                  # LangGraph workflows
│   │   ├── smart_agent_graph.py # Main agent graph
│   │   ├── graph_config_service.py # Graph configuration
│   │   ├── graph_registry_with_auth.py # Graph registry with permissions
│   │   ├── base_graph.py       # Base graph implementation
│   │   ├── research_graph.py   # Research-focused workflow
│   │   ├── coding_graph.py     # Code generation workflow
│   │   └── conversation_graph.py # Simple conversation workflow
│   ├── nodes/                   # Agent nodes
│   │   ├── reason_node.py      # Reasoning logic
│   │   ├── tool_node.py        # Tool execution
│   │   └── response_node.py    # Response generation
│   ├── services/                # Business logic
│   │   ├── chat_service.py     # Chat orchestration
│   │   ├── hil_service.py      # Human-in-loop
│   │   ├── tracing_service.py  # Tracing & metrics
│   │   ├── hardware_service.py # Hardware device integration
│   │   └── durable_service.py  # Durable execution service
│   ├── core/                    # Core utilities
│   │   ├── config/             # Configuration
│   │   └── resilience/         # Circuit breakers, rate limiting
│   ├── sdk/                     # Client SDK
│   └── types/                   # Type definitions
│       ├── response_models.py  # Response type definitions
│       └── hardware_types.py   # Hardware device types
├── deployment/                  # Deployment configurations
│   ├── dev/                    # Development environment
│   ├── test/                   # Testing environment
│   ├── staging/                # Staging environment
│   ├── production/             # Production environment
│   ├── scripts/                # Deployment scripts
│   │   ├── start_agent_service.sh  # Service starter
│   │   ├── docker_build.sh         # Docker build script
│   │   └── register_consul.py      # Consul registration
│   ├── Dockerfile.agent        # Production Dockerfile
│   └── README.md               # Deployment guide
└── main.py                     # Entry point
```

## 🚀 Quick Start

### Development Mode

```bash
# Install dependencies with UV (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate

# Start development server
./deployment/scripts/start_agent_service.sh -e dev start

# Or manually
uv pip install -r deployment/dev/requirements.txt
uvicorn main:app --reload --port 8080
```

### Docker Deployment

```bash
# Build lightweight API mode image (~400MB)
./deployment/scripts/docker_build.sh -m api -t isa-agent:v1.0.0

# Build local mode with embedded model (~3GB)
./deployment/scripts/docker_build.sh -m local -e cloud -t isa-agent:local

# Run container
docker run -p 8080:8080 \
  -e ISA_MODE=api \
  -e ISA_API_URL=http://model-service:8082 \
  -e MCP_SERVER_URL=http://mcp-service:8081 \
  isa-agent:v1.0.0
```

### Environment Configuration

Copy the example environment file:
```bash
cp deployment/env.example deployment/dev/.env
```

Key configurations:
```env
# ISA Model Configuration
ISA_MODE=api                           # api (connects to external service) or local (embedded model)
ISA_API_URL=http://localhost:8082     # ISA Model service URL (when ISA_MODE=api)

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8081  # MCP server URL

# API Server
API_HOST=0.0.0.0
API_PORT=8080

# Consul Service Discovery
CONSUL_HOST=localhost
CONSUL_PORT=8500
SERVICE_NAME=agents
```

## 📚 API Usage

### Health Check
```bash
curl http://localhost:8080/health
```

### Send Message (Streaming)
```bash
curl -N http://localhost:8080/api/v1/agents/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the weather in San Francisco?",
    "user_id": "user123"
  }'
```

### Send Message (Non-Streaming)
```bash
curl -X POST http://localhost:8080/api/v1/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "user_id": "user123",
    "thread_id": null
  }'
```

### Graph Management
```bash
# List available graphs for user
curl http://localhost:8080/api/v1/graphs/available/user123

# Select a specific graph
curl -X POST http://localhost:8080/api/v1/graphs/select \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "graph_type": "research"
  }'

# Auto-select graph based on task
curl -X POST http://localhost:8080/api/v1/graphs/auto-select \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "task_description": "Help me research quantum computing"
  }'
```

### Human-in-Loop Interaction
```bash
# Get pending approvals
curl http://localhost:8080/api/v1/execution/pending/user123

# Approve/reject an action
curl -X POST http://localhost:8080/api/v1/execution/approve \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "thread123",
    "approved": true
  }'
```

### Interactive API Documentation
Visit `http://localhost:8080/docs` for Swagger UI

## 🔧 Core Components

### Smart Agent Graph
The agent uses a LangGraph workflow with the following nodes:
- **Reason Node**: Analyzes user input and determines actions
- **Tool Node**: Executes MCP tools and external function calls
- **Response Node**: Generates final responses
- **Failsafe Node**: Handles errors and edge cases
- **Guardrail Node**: Safety checks and content filtering

### Specialized Graph Types

**Research Graph**
- Optimized for deep research and information gathering
- Enhanced search capabilities and source tracking
- Multi-step reasoning for complex queries

**Coding Graph**
- Specialized for code generation and debugging
- Integration with development tools
- Code review and optimization features

**Conversation Graph**
- Simple, fast conversational interface
- No tool execution for basic chat
- Optimized for low-latency responses

### ISA Modes

**API Mode (Recommended for Production)**
- Connects to external ISA Model service
- Lightweight deployment (~400MB Docker image)
- Scalable and flexible

**Local Mode**
- Embedded ISA Model with `[cloud]` or `[all]` extras
- Standalone deployment (~3-8GB Docker image)
- No external model service required

### MCP Integration
- Automatic tool discovery from MCP servers
- Dynamic tool binding to LangGraph agent
- Support for multiple MCP servers
- Health monitoring and circuit breakers
- Composio tool integration support

### Hardware Integration
- Support for IoT device contexts
- Sensor data processing and automation
- Device command execution
- Real-time device status monitoring

## 🐳 Docker Images

### Build Options

```bash
# API mode (lightweight)
docker build -f deployment/Dockerfile.agent \
  --build-arg ISA_MODE=api \
  -t isa-agent:api .

# Local mode with cloud extras
docker build -f deployment/Dockerfile.agent \
  --build-arg ISA_MODE=local \
  --build-arg ISA_MODEL_EXTRAS=cloud \
  -t isa-agent:local-cloud .

# Local mode with all extras
docker build -f deployment/Dockerfile.agent \
  --build-arg ISA_MODE=local \
  --build-arg ISA_MODEL_EXTRAS=all \
  -t isa-agent:local-full .
```

### Image Sizes
- **API mode**: ~400MB (base + agent dependencies)
- **Local mode [cloud]**: ~3GB (includes lightweight ML)
- **Local mode [all]**: ~8GB (includes full ML stack)

## 🔍 Service Discovery

The agent service automatically registers with Consul when available:

```bash
# Check service registration
curl http://localhost:8500/v1/health/service/agents?passing=true

# Service tags
- sse          # Server-Sent Events support
- agent        # Smart Agent service
- ai           # AI service
- streaming    # Streaming responses
- chat         # Chat functionality
```

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_chat_service.py

# With coverage
pytest --cov=app tests/
```

### Manual Testing
```bash
# Test streaming endpoint
curl -N http://localhost:8080/api/v1/agents/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "test"}'

# Test session management
curl http://localhost:8080/api/v1/agents/sessions?user_id=test
```

## 📊 Monitoring & Observability

### Metrics Endpoints
- `/health` - Service health check
- `/api/v1/agents/stats` - Agent statistics
- `/api/v1/agents/sessions` - Active sessions
- `/api/v1/graphs/stats` - Graph usage statistics
- `/api/v1/tracing/active` - Active traces

### Tracing
- LangSmith integration for execution tracing
- Structured logging with configurable levels
- Circuit breaker metrics
- Request/response correlation tracking
- Performance metrics per graph type

### Loki Integration (Optional)
```env
LOKI_URL=http://localhost:3100
LOKI_ENABLED=true
```

## 🔐 Security Features

- **API Key Authentication**: Master key and user-specific keys
- **Rate Limiting**: Per-user request limits
- **Circuit Breakers**: Automatic failure protection
- **Connection Limiting**: Resource protection
- **Input Validation**: Pydantic-based validation
- **Graph Access Control**: Permission-based graph access
- **Human-in-Loop**: Manual approval for sensitive operations
- **Audit Logging**: Comprehensive action tracking

## 🚢 Deployment

### Development
```bash
./deployment/scripts/start_agent_service.sh -e dev start
```

### Production
```bash
# Using Docker
docker run -d \
  --name isa-agent \
  -p 8080:8080 \
  --env-file deployment/production/.env.production \
  isa-agent:v1.0.0

# Using deployment script
./deployment/scripts/start_agent_service.sh -e production start
```

### Scaling
- Deploy multiple instances behind a load balancer
- Use external PostgreSQL for shared state
- Connect all instances to the same Consul cluster

## 📝 Configuration

See `deployment/env.example` for all available configuration options.

### Environment-Specific Configs
- `deployment/dev/.env` - Development
- `deployment/test/.env.test` - Testing
- `deployment/staging/.env.staging` - Staging
- `deployment/production/.env.production` - Production

## 🐛 Troubleshooting

### Service Won't Start
1. Check if ports are available: `lsof -i :8080`
2. Verify environment variables: `./deployment/scripts/start_agent_service.sh -e dev status`
3. Check logs: `tail -f logs/app.log`

### MCP Connection Issues
1. Verify MCP server is running: `curl http://localhost:8081/health`
2. Check MCP_SERVER_URL configuration
3. Review circuit breaker status at `/health` endpoint

### Docker Build Issues
1. Ensure Docker is running: `docker info`
2. Clean build cache: `docker builder prune`
3. Use `--no-cache` flag for clean build

## 📄 License

[Your License Here]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**isA Agent** - Production-ready AI agent service 🚀

## 💻 CLI Interface

### Installation
```bash
pip install -e .
```

### Available Commands
After installation, you can use:
- `isa-chat` - Primary CLI command
- `isa-agent` - Alternative command  
- `isachat` - Short version

### Quick CLI Usage
```bash
# Check API health
isa-chat --health

# Interactive chat
isa-chat

# Single message
isa-chat "Hello, what can you help me with?"

# Synchronous mode
isa-chat --sync "What is 2+2?"

# Custom API endpoint
isa-chat --api-url "https://api.example.com" --api-key "your-key" "Hello"
```

### Quick Links
- 📖 [Deployment Guide](deployment/README.md)
- 🔧 [API Documentation](http://localhost:8080/docs)
- 💻 [CLI Documentation](CBKB/HowTos/how_to_cli.md)
- 🐳 [Docker Build Script](deployment/scripts/docker_build.sh)
- 🚀 [Service Starter](deployment/scripts/start_agent_service.sh)
- 📚 [How-To Guides](CBKB/HowTos/)
  - [Chat Guide](CBKB/HowTos/how_to_chat.md)
  - [CLI Usage Guide](CBKB/HowTos/how_to_cli.md)
  - [Durable Execution](CBKB/HowTos/how_to_durable.md)
  - [Tracing Guide](CBKB/HowTos/how_to_trace.md)
  - [Graph Configuration](CBKB/HowTos/how_to_graph.md)
  - [Hardware Integration](CBKB/HowTos/how_to_hardware.md)
  - [Human-in-Loop](CBKB/HowTos/how_to_hil.md)
