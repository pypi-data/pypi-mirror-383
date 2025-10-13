# Cost Katana Python 🥷

**AI that just works. With automatic cost tracking.**

```python
import cost_katana as ck

response = ck.ai('gpt-4', 'Hello, world!')
print(response.text)        # "Hello! How can I help you today?"
print(f"Cost: ${response.cost}")  # "Cost: $0.0012"
```

That's it. No setup. No configuration. No complexity.

## Installation

```bash
pip install costkatana
```

> **Package Names:**
> - **Python**: `costkatana` (PyPI)
> - **JavaScript/Node**: `cost-katana` (NPM)
> - **CLI**: `cost-katana-cli` (NPM) or included with Python package

## Quick Start

### Zero Configuration

```python
import cost_katana as ck

# Just works with any AI model
ck.ai('gpt-4', 'Explain quantum computing')
ck.ai('claude-3-sonnet', 'Write a haiku')
ck.ai('gemini-pro', 'Solve this: 2x + 5 = 13')
```

### Chat Conversations

```python
import cost_katana as ck

chat = ck.chat('gpt-4')
chat.send('Hello!')
chat.send('What can you help me with?')
chat.send('Tell me a joke')

print(f"Total cost: ${chat.total_cost}")
```

### Compare Models

```python
import cost_katana as ck

models = ['gpt-4', 'claude-3-sonnet', 'gemini-pro']
prompt = 'Explain relativity in one sentence'

for model in models:
    response = ck.ai(model, prompt)
    print(f"{model}: ${response.cost:.4f}")
```

## Features

### 💰 Cost Tracking

Every response includes cost information:

```python
response = ck.ai('gpt-4', 'Write a story')
print(f"Cost: ${response.cost}")
print(f"Tokens: {response.tokens}")
print(f"Model: {response.model}")
print(f"Provider: {response.provider}")
```

### 💾 Smart Caching

Save money by caching repeated requests:

```python
# First call - costs money
r1 = ck.ai('gpt-4', 'What is 2+2?', cache=True)
print(r1.cached)  # False

# Second call - free from cache
r2 = ck.ai('gpt-4', 'What is 2+2?', cache=True)
print(r2.cached)  # True - saved money!
```

### ⚡ Cortex Optimization

Reduce costs by 70-95%:

```python
response = ck.ai('gpt-4', 'Write a comprehensive guide to Python', 
                 cortex=True)

print(response.optimized)  # True
print(f"Saved: ${response.saved_amount}")
```

### 🔄 Auto-Failover

Never fail - automatically switch providers:

```python
# If OpenAI is down, automatically uses Claude or Gemini
response = ck.ai('gpt-4', 'Hello')
print(response.provider)  # Might be 'anthropic' if OpenAI failed
```

### 📊 Analytics Dashboard

All usage syncs to your dashboard at [costkatana.com](https://costkatana.com):

```python
response = ck.ai('gpt-4', 'Hello')
# Automatically tracked in your dashboard
# View at: https://costkatana.com/dashboard
```

## Configuration

### Environment Variables

```bash
# Option 1: Cost Katana (Recommended - all features)
export COST_KATANA_KEY="dak_your_key_here"

# Option 2: Direct provider keys (limited features)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Manual Configuration

```python
import cost_katana as ck

ck.configure(
    api_key='dak_your_key',
    cortex=True,     # 70-95% cost savings
    cache=True,      # Smart caching
    firewall=True    # Security
)
```

### Advanced Options

```python
response = ck.ai('gpt-4', 'Your prompt',
    temperature=0.7,        # Creativity level (0-2)
    max_tokens=500,         # Response length limit
    system_message='You are helpful',  # System prompt
    cache=True,             # Enable caching
    cortex=True            # Enable optimization
)
```

## Multi-Provider Support

Works with all major AI providers:

```python
# OpenAI
ck.ai('gpt-4', 'Hello')
ck.ai('gpt-3.5-turbo', 'Hello')

# Anthropic
ck.ai('claude-3-sonnet', 'Hello')
ck.ai('claude-3-haiku', 'Hello')

# Google
ck.ai('gemini-pro', 'Hello')
ck.ai('gemini-flash', 'Hello')

# AWS Bedrock
ck.ai('nova-pro', 'Hello')
ck.ai('nova-lite', 'Hello')

# And many more...
```

## Real-World Examples

### Customer Support Bot

```python
import cost_katana as ck

support = ck.chat('gpt-3.5-turbo',
    system_message='You are a helpful customer support agent.')

def handle_customer_query(query: str):
    response = support.send(query)
    print(f"Cost so far: ${support.total_cost}")
    return response
```

### Content Generation

```python
import cost_katana as ck

def generate_blog_post(topic: str):
    # Use Cortex for long-form content (70-95% savings)
    post = ck.ai('gpt-4', f'Write a blog post about {topic}',
                 cortex=True, max_tokens=2000)
    
    return {
        'content': post.text,
        'cost': post.cost,
        'word_count': len(post.text.split())
    }
```

### Code Assistant

```python
import cost_katana as ck

def review_code(code: str):
    review = ck.ai('claude-3-sonnet',
        f'Review this code and suggest improvements:\n\n{code}',
        cache=True)  # Cache for repeated reviews
    
    return review.text
```

### Translation Service

```python
import cost_katana as ck

def translate(text: str, target_language: str):
    # Use cheaper model for translations
    translated = ck.ai('gpt-3.5-turbo',
        f'Translate to {target_language}: {text}',
        cache=True)
    
    return translated.text
```

## Framework Integration

### FastAPI

```python
from fastapi import FastAPI
import cost_katana as ck

app = FastAPI()

@app.post('/api/chat')
async def chat(request: dict):
    response = ck.ai('gpt-4', request['prompt'])
    return {
        'text': response.text,
        'cost': response.cost
    }
```

### Flask

```python
from flask import Flask, request, jsonify
import cost_katana as ck

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    prompt = request.json['prompt']
    response = ck.ai('gpt-4', prompt)
    return jsonify({
        'text': response.text,
        'cost': response.cost
    })
```

### Django

```python
from django.http import JsonResponse
import cost_katana as ck

def chat_view(request):
    prompt = request.POST.get('prompt')
    response = ck.ai('gpt-4', prompt)
    return JsonResponse({
        'text': response.text,
        'cost': response.cost
    })
```

## Command Line Interface

The Python package includes a CLI:

```bash
# After installing the package
pip install costkatana

# Use the CLI
costkatana chat
costkatana ask "What is Python?"
```

Or install the dedicated CLI:

```bash
npm install -g cost-katana-cli
cost-katana chat
```

## Error Handling

```python
import cost_katana as ck
from cost_katana.exceptions import CostKatanaError

try:
    response = ck.ai('gpt-4', 'Hello')
    print(response.text)
except CostKatanaError as e:
    if 'API key' in str(e):
        print('Please set your API key')
    elif 'rate limit' in str(e):
        print('Rate limit exceeded')
    elif 'model' in str(e):
        print('Model not found')
    else:
        print(f'Error: {e}')
```

## Cost Optimization Tips

### 1. Use Appropriate Models

```python
# For simple tasks, use cheaper models
ck.ai('gpt-3.5-turbo', 'Simple question')  # $0.0001

# For complex tasks, use powerful models
ck.ai('gpt-4', 'Complex analysis')  # $0.01
```

### 2. Enable Caching

```python
# Cache repeated queries
ck.ai('gpt-4', 'Common question', cache=True)
```

### 3. Use Cortex for Long Content

```python
# 70-95% savings on long-form content
ck.ai('gpt-4', 'Write a book chapter', cortex=True)
```

### 4. Batch Similar Requests

```python
session = ck.chat('gpt-3.5-turbo')
# Reuse session for related queries
session.send('Query 1')
session.send('Query 2')
```

## Monitoring & Analytics

### Track Usage

```python
import cost_katana as ck

chat = ck.chat('gpt-4')
chat.send('Hello')
chat.send('How are you?')

print(f'Messages: {len(chat.history)}')
print(f'Total cost: ${chat.total_cost}')
print(f'Total tokens: {chat.total_tokens}')
```

### Dashboard Features

Visit [costkatana.com/dashboard](https://costkatana.com/dashboard) to see:

- Real-time cost tracking
- Usage by model and provider
- Daily/weekly/monthly spending
- Token usage analytics
- Optimization recommendations
- Team usage breakdown
- Budget alerts

## Migration Guide

### From OpenAI SDK

```python
# Before (OpenAI SDK)
from openai import OpenAI
client = OpenAI(api_key='sk-...')
completion = client.chat.completions.create(
    model='gpt-4',
    messages=[{'role': 'user', 'content': 'Hello'}]
)
print(completion.choices[0].message.content)

# After (Cost Katana)
import cost_katana as ck
response = ck.ai('gpt-4', 'Hello')
print(response.text)
print(f"Cost: ${response.cost}")  # Bonus: cost tracking!
```

### From Anthropic SDK

```python
# Before (Anthropic SDK)
import anthropic
client = anthropic.Anthropic(api_key='sk-ant-...')
message = client.messages.create(
    model='claude-3-sonnet-20241022',
    messages=[{'role': 'user', 'content': 'Hello'}]
)

# After (Cost Katana)
import cost_katana as ck
response = ck.ai('claude-3-sonnet', 'Hello')
```

### From Google AI SDK

```python
# Before (Google AI SDK)
import google.generativeai as genai
genai.configure(api_key='...')
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('Hello')

# After (Cost Katana)
import cost_katana as ck
response = ck.ai('gemini-pro', 'Hello')
```

## Package Naming

**Important**: Different package names for different languages to avoid conflicts:

| Language | Package Manager | Install Command | Import |
|----------|----------------|-----------------|--------|
| **Python** | PyPI | `pip install costkatana` | `import cost_katana` |
| **JavaScript/Node** | NPM | `npm install cost-katana` | `import { ai } from 'cost-katana'` |
| **CLI (NPM)** | NPM | `npm install -g cost-katana-cli` | `cost-katana chat` |
| **CLI (Python)** | PyPI | `pip install costkatana` | `costkatana chat` |

## Troubleshooting

### No API Keys Found

```bash
# Set Cost Katana key (recommended)
export COST_KATANA_KEY="dak_your_key"

# Or set provider keys directly
export OPENAI_API_KEY="sk-..."
```

### Model Not Available

```python
# Check available models
try:
    response = ck.ai('model-name', 'test')
except Exception as e:
    print(f'Error: {e}')
    # Error message includes available models
```

### Rate Limits

```python
# Automatic retry with backoff
response = ck.ai('gpt-4', 'Hello', retry=True)
```

## Support

- **Dashboard**: [costkatana.com](https://costkatana.com)
- **Documentation**: [docs.costkatana.com](https://docs.costkatana.com)
- **GitHub**: [github.com/Hypothesize-Tech/cost-katana-python](https://github.com/Hypothesize-Tech/cost-katana-python)
- **Email**: support@costkatana.com
- **Discord**: [discord.gg/Wcwzw8wM](https://discord.gg/Wcwzw8wM)

## License

MIT © Cost Katana

---

**Start saving on AI costs today!**

```bash
pip install costkatana
```

```python
import cost_katana as ck
response = ck.ai('gpt-4', 'Hello, world!')
```