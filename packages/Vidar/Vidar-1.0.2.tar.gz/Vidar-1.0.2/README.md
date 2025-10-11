# Vidar Python SDK

AI observability platform for LLM applications with automatic tracing.

## Installation

```bash
pip install vidar
```

For full functionality including async support and LLM client integrations:

```bash
pip install vidar[full]
```

## Quick Start

```python
import vidar

# Initialize once (like Laminar)
vidar.initialize(api_key="your-api-key")

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
@vidar.trace("My AI Function")
def process_text(text):
    vidar.add_attribute("input_length", len(text))
    
    # Your LLM calls here
    result = client.chat.completions.create(...)
    
    vidar.add_attribute("output_length", len(result))
    return result
```

### Session Tracking
```python
with vidar.trace("Document Analysis"):
    vidar.add_attribute("session_id", "session_123")
    
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
    vidar.set_error(e)
    raise
```

## Direct Proxy Usage

You can also use Vidar as a proxy without the SDK:

```python
import requests

response = requests.post(
    "http://localhost:8080/proxy/openai/v1/chat/completions",
    headers={"Authorization": "Bearer your-vidar-api-key"},
    json={"model": "gpt-4", "messages": [...]}
)
```

## Configuration

```python
vidar.initialize(
    api_key="your-api-key",
    base_url="http://localhost:8080",  # Vidar server
    project_id="my-project", 
    timeout=30.0
)
```

## Web Framework Integration

### FastAPI
```python
from fastapi import FastAPI
import vidar

app = FastAPI()

@app.on_event("startup")
async def startup():
    vidar.initialize(api_key="your-key")

@app.post("/chat")
async def chat(message: str):
    with vidar.trace("Chat API"):
        # Your LLM logic here
        return {"response": "..."}
```

### Django
```python
# settings.py
MIDDLEWARE = [
    'myapp.middleware.VidarMiddleware',
    # ... other middleware
]

# middleware.py
import vidar

class VidarMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        vidar.initialize(api_key="your-key")
    
    def __call__(self, request):
        with vidar.trace(f"{request.method} {request.path}"):
            return self.get_response(request)
```

## Documentation

- [Full Documentation](https://docs.vidar.io)
- [API Reference](https://docs.vidar.io/api)
- [Examples](https://github.com/tanmaysharma2001/vidar/tree/main/examples)

## License

MIT License