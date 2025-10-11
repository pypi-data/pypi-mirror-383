# LLMTrace Python SDK

AI observability platform for LLM applications with automatic tracing.

## Installation

```bash
pip install llmtrace
```

For full functionality including async support and LLM client integrations:

```bash
pip install llmtrace[full]
```

## Quick Start

```python
import llmtrace

# Initialize once (like Laminar)
llmtrace.initialize(api_key="your-api-key")

# All LLM calls are now automatically traced!
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
# ↑ This is automatically traced with cost, latency, tokens, etc.
```

## Features

- **Zero-code tracing**: Just initialize and go
- **Automatic cost tracking**: Real-time cost calculation
- **Performance monitoring**: Latency, token usage, error rates  
- **Session correlation**: Group related LLM calls
- **Multi-provider support**: OpenAI, Anthropic, and more
- **Async support**: Works with httpx, aiohttp
- **Framework integration**: FastAPI, Django, Flask examples

## Usage Examples

### Manual Tracing
```python
@llmtrace.trace("My AI Function")
def process_text(text):
    llmtrace.add_attribute("input_length", len(text))
    
    # Your LLM calls here
    result = client.chat.completions.create(...)
    
    llmtrace.add_attribute("output_length", len(result))
    return result
```

### Session Tracking
```python
with llmtrace.trace("Document Analysis"):
    llmtrace.add_attribute("session_id", "session_123")
    
    # Multiple related LLM calls
    summary = summarize_document(doc)
    questions = generate_questions(doc)
    answers = answer_questions(questions, doc)
```

### Error Handling
```python
try:
    response = client.chat.completions.create(...)
except Exception as e:
    llmtrace.set_error(e)
    raise
```

## Direct Proxy Usage

You can also use LLMTrace as a proxy without the SDK:

```python
import requests

response = requests.post(
    "http://localhost:8080/proxy/openai/v1/chat/completions",
    headers={"Authorization": "Bearer your-llmtrace-api-key"},
    json={"model": "gpt-4", "messages": [...]}
)
```

## Configuration

```python
llmtrace.initialize(
    api_key="your-api-key",
    base_url="http://localhost:8080",  # LLMTrace server
    project_id="my-project", 
    timeout=30.0
)
```

## Web Framework Integration

### FastAPI
```python
from fastapi import FastAPI
import llmtrace

app = FastAPI()

@app.on_event("startup")
async def startup():
    llmtrace.initialize(api_key="your-key")

@app.post("/chat")
async def chat(message: str):
    with llmtrace.trace("Chat API"):
        # Your LLM logic here
        return {"response": "..."}
```

### Django
```python
# settings.py
MIDDLEWARE = [
    'myapp.middleware.LLMTraceMiddleware',
    # ... other middleware
]

# middleware.py
import llmtrace

class LLMTraceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        llmtrace.initialize(api_key="your-key")
    
    def __call__(self, request):
        with llmtrace.trace(f"{request.method} {request.path}"):
            return self.get_response(request)
```

## Documentation

- [Full Documentation](https://docs.llmtrace.io)
- [API Reference](https://docs.llmtrace.io/api)
- [Examples](https://github.com/tanmaysharma2001/llmtrace/tree/main/examples)

## License

MIT License