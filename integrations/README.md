# MoveScout Integrations

This directory contains integrations with external APIs and services to enhance the AI negotiation system.

## 🔌 Current Integrations

### ✅ Perplexity API (Implemented)
**Purpose**: Real-time market research and moving industry insights

**Features**:
- Market research for moving costs and trends
- Company reputation analysis
- Up-to-date pricing information
- Online LLM with current data (2024)

**Setup**:
1. Get API key from [Perplexity Settings](https://www.perplexity.ai/settings/api)
2. Add to `.env`: `PERPLEXITY_API_KEY=your_key_here`
3. The integration uses OpenAI-compatible API (no extra package needed)

**Usage Example**:
```python
from integrations.perplexity_client import PerplexityClient

client = PerplexityClient()

# Get market insights
insights = client.get_moving_market_insights(
    origin="San Francisco, CA",
    destination="Miami, FL",
    move_type="long-distance"
)

# Research mover reputation
reputation = client.get_mover_reputation("United Van Lines")
```

**Testing**:
```bash
cd MoveScout
python test_perplexity.py
```

**Integration Point**: [strategist_agent.py](../agents/strategist_agent.py:40)
- Called before filtering movers
- Enhances negotiation strategy with market data
- Stored in state as `MarketResearch` model

---

## 🚧 Planned Integrations (Phase 2 & 3)

### Linkup API
**Purpose**: Real-time web search for mover reviews and ratings

**Status**: Not implemented
**Priority**: High (Phase 2)

### Structify API
**Purpose**: Extract pricing and service details from mover websites

**Status**: Not implemented
**Priority**: High (Phase 2)

### DeepL API
**Purpose**: Multi-language translation for negotiating with non-English movers

**Status**: Not implemented
**Priority**: Medium (Phase 3)

### ClickHouse
**Purpose**: Store historical negotiation data for analytics

**Status**: Not implemented
**Priority**: High (Phase 2)

### Datadog
**Purpose**: APM, metrics, and monitoring across all agents

**Status**: Not implemented
**Priority**: Critical (Phase 1)

---

## 📁 Integration Structure

Each integration follows this pattern:

```python
# integrations/{service}_client.py

class {Service}Client:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key from env or parameter"""
        self.api_key = api_key or os.getenv("{SERVICE}_API_KEY")

    def method_name(self, params) -> result:
        """Specific functionality"""
        pass

# Convenience functions
def helper_function():
    """Easy-to-use wrapper"""
    pass
```

---

## 🧪 Testing Integrations

Each integration should have a test file in the root:
- `test_perplexity.py` ✅ (Comprehensive test for all 3 features)
- `test_linkup.py` (TODO - Phase 2)
- `test_structify.py` (TODO - Phase 2)
- `test_deepl.py` (TODO - Phase 3)
- `test_clickhouse.py` (TODO - Phase 2)

Run tests:
```bash
cd MoveScout
python test_{integration}.py
```

---

## 🔐 Environment Variables

All API keys are stored in `.env` (see `.env.example`):

```bash
# Required
OPENAI_API_KEY=...
PERPLEXITY_API_KEY=...

# Optional (future)
LINKUP_API_KEY=...
STRUCTIFY_API_KEY=...
DEEPL_API_KEY=...
DD_API_KEY=...
```

---

## 📊 Integration Flow

```
ChatAgent (collect info)
    ↓
StrategistAgent
    ├─→ Perplexity: Market research ✅
    ├─→ Linkup: Review search (TODO)
    ├─→ Structify: Website parsing (TODO)
    └─→ Generate strategy
    ↓
VoiceAgent
    └─→ DeepL: Translation (TODO)
    ↓
AnalystAgent
    └─→ ClickHouse: Store results (TODO)
```

---

## 🛠️ Adding New Integrations

1. Create `integrations/{service}_client.py`
2. Add API key to `.env.example`
3. Create `test_{service}.py`
4. Update agent to use the integration
5. Update this README
6. Update `integrations/__init__.py`

Example:
```python
# integrations/__init__.py
from .perplexity_client import PerplexityClient
from .linkup_client import LinkupClient  # New

__all__ = ['PerplexityClient', 'LinkupClient']
```

---

## 📚 Resources

- [Perplexity API Docs](https://docs.perplexity.ai/)
- [Linkup API](https://linkup.so/)
- [Structify](https://structify.ai/)
- [DeepL API](https://www.deepl.com/pro-api)
- [Datadog APM](https://docs.datadoghq.com/tracing/)
- [ClickHouse](https://clickhouse.com/docs)
