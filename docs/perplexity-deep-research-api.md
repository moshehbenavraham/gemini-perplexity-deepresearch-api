# Perplexity Sonar Deep Research API Documentation

> Source: [Perplexity API Documentation](https://docs.perplexity.ai)

## Overview

**Sonar Deep Research** is Perplexity's expert-level research model that conducts exhaustive searches across hundreds of sources and generates comprehensive reports with citations.

### Key Capabilities

- Deep research and reasoning capabilities
- Exhaustive multi-source research functionality
- Detailed report generation with citations
- **128K token context window**
- Expert-level subject analysis
- No training on customer data

### Use Cases

- Academic research and comprehensive reports
- Market analysis and competitive intelligence
- Due diligence and investigative research
- Complex topic synthesis from multiple sources

---

## API Endpoint

```
POST https://api.perplexity.ai/chat/completions
```

## Authentication

Bearer token authentication via the `Authorization` header:

```
Authorization: Bearer <your-api-key>
```

---

## Request Parameters

### Required Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | enum | Must be `sonar-deep-research` |
| `messages` | array | List of message objects with `role` and `content` |

### Message Object Structure

```json
{
  "role": "system" | "user" | "assistant",
  "content": "string or content chunks"
}
```

### Optional Parameters

#### Search & Filtering

| Parameter | Type | Description |
|-----------|------|-------------|
| `search_mode` | string | `"academic"`, `"sec"`, or `"web"` (default: `"web"`) |
| `search_domain_filter` | array | Domains for allowlisting/denylisting (max 20) |
| `search_recency_filter` | string | Time-based filter (e.g., `"week"`, `"day"`) |
| `search_after_date_filter` | string | Format: `%m/%d/%Y` |
| `search_before_date_filter` | string | Format: `%m/%d/%Y` |
| `disable_search` | boolean | Use only training data |
| `enable_search_classifier` | boolean | Auto-detect if search needed |

#### Response Control

| Parameter | Type | Description |
|-----------|------|-------------|
| `max_tokens` | integer | Maximum completion tokens |
| `temperature` | float | 0-2 (default: 0.2) for randomness control |
| `top_p` | float | 0-1 (default: 0.9) for nucleus sampling |
| `top_k` | integer | Top-k filtering |
| `presence_penalty` | float | 0-2 for topic diversity |
| `frequency_penalty` | float | 0-2 to reduce repetition |
| `response_format` | object | For structured JSON output |
| `stream` | boolean | Enable incremental responses |

#### Content Control

| Parameter | Type | Description |
|-----------|------|-------------|
| `return_images` | boolean | Include images (default: false) |
| `return_related_questions` | boolean | Include related questions (default: false) |
| `reasoning_effort` | string | `"low"`, `"medium"`, `"high"` (sonar-deep-research only) |

#### Advanced Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `web_search_options` | object | Contains `search_context_size` (`"low"`/`"medium"`/`"high"`) and `user_location` |
| `media_response.overrides` | object | Control `return_videos` and `return_images` |

---

## Response Schema

### Success Response (200)

```json
{
  "id": "string",
  "model": "sonar-deep-research",
  "created": 1234567890,
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 500,
    "total_tokens": 600,
    "search_context_size": "high",
    "citation_tokens": 50,
    "num_search_queries": 15,
    "reasoning_tokens": 200
  },
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "message": {
        "content": "Comprehensive research report...",
        "role": "assistant"
      },
      "finish_reason": "stop"
    }
  ],
  "search_results": [
    {
      "title": "Source Title",
      "url": "https://example.com/article",
      "date": "2025-01-15"
    }
  ],
  "videos": [
    {
      "url": "string",
      "thumbnail_url": "string",
      "thumbnail_width": 480,
      "thumbnail_height": 360,
      "duration": 120
    }
  ]
}
```

### Response Fields

| Field | Description |
|-------|-------------|
| `id` | Unique completion identifier |
| `model` | Model used for completion |
| `created` | Unix timestamp of creation |
| `usage` | Token usage breakdown |
| `choices` | Array of completion choices |
| `search_results` | Array of cited sources with URLs |
| `videos` | Array of related video content |

### Usage Metrics

| Metric | Description |
|--------|-------------|
| `prompt_tokens` | Input tokens consumed |
| `completion_tokens` | Output tokens generated |
| `citation_tokens` | Tokens from citations |
| `num_search_queries` | Number of searches executed |
| `reasoning_tokens` | Tokens used for reasoning |

### Streaming Response

Uses `text/event-stream` content type with `chat.completion.chunk` objects containing delta updates.

---

## Example Request

### cURL

```bash
curl --request POST \
  --url https://api.perplexity.ai/chat/completions \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "sonar-deep-research",
    "messages": [
      {
        "role": "system",
        "content": "You are a research assistant. Provide comprehensive, well-cited reports."
      },
      {
        "role": "user",
        "content": "Provide a comprehensive analysis of the current state of quantum computing and its potential applications in cryptography."
      }
    ],
    "search_mode": "web",
    "max_tokens": 4000,
    "temperature": 0.2,
    "reasoning_effort": "high"
  }'
```

### Python

```python
import requests

url = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": "Bearer <your-api-key>",
    "Content-Type": "application/json"
}

payload = {
    "model": "sonar-deep-research",
    "messages": [
        {
            "role": "system",
            "content": "You are a research assistant. Provide comprehensive, well-cited reports."
        },
        {
            "role": "user",
            "content": "Provide a comprehensive analysis of the current state of quantum computing."
        }
    ],
    "search_mode": "web",
    "max_tokens": 4000,
    "temperature": 0.2,
    "reasoning_effort": "high"
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()

print(result["choices"][0]["message"]["content"])
print("\nSources:")
for source in result.get("search_results", []):
    print(f"  - {source['title']}: {source['url']}")
```

### JavaScript/Node.js

```javascript
const response = await fetch('https://api.perplexity.ai/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <your-api-key>',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'sonar-deep-research',
    messages: [
      {
        role: 'system',
        content: 'You are a research assistant. Provide comprehensive, well-cited reports.'
      },
      {
        role: 'user',
        content: 'Provide a comprehensive analysis of the current state of quantum computing.'
      }
    ],
    search_mode: 'web',
    max_tokens: 4000,
    temperature: 0.2,
    reasoning_effort: 'high'
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

---

## Pricing

### Token Pricing (per 1 Million tokens)

| Component | Cost |
|-----------|------|
| Input Tokens | $2 |
| Output Tokens | $8 |
| Citation Tokens | $2 |
| Reasoning Tokens | $3 |

### Request Fees (per 1,000 requests)

Pricing varies by search context depth:

| Context Size | Cost per 1K Requests |
|--------------|---------------------|
| Low | $5-$6 |
| Medium | $8-$10 |
| High | $12-$14 |

### Search Query Fees

- **$5 per 1,000 search queries**

### Cost Considerations

Sonar Deep Research typically costs more than other models due to:
- Multiple search queries per request
- Extended reasoning token usage
- Comprehensive citation processing

---

## Model Comparison

| Model | Type | Best For |
|-------|------|----------|
| **Sonar** | Search | Quick factual queries, topic summaries |
| **Sonar Pro** | Search | Complex queries with follow-ups |
| **Sonar Reasoning** | Reasoning | Fast problem-solving with search |
| **Sonar Reasoning Pro** | Reasoning | Precise multi-step reasoning (DeepSeek-R1 powered) |
| **Sonar Deep Research** | Research | Exhaustive research, comprehensive reports |

---

## Best Practices

1. **Use appropriate reasoning effort**: Set `reasoning_effort` to `"high"` for complex topics requiring thorough analysis.

2. **Leverage search modes**: Use `"academic"` for scholarly research, `"sec"` for financial/regulatory documents.

3. **Filter by date**: Use `search_after_date_filter` and `search_before_date_filter` for time-sensitive research.

4. **Domain filtering**: Use `search_domain_filter` to focus on authoritative sources or exclude unreliable ones.

5. **Handle costs**: Monitor `usage` in responses to track token consumption and search queries.

6. **Stream for long responses**: Enable `stream: true` for real-time output on comprehensive reports.

---

## Rate Limits

Refer to your API dashboard for current rate limits based on your subscription tier.

---

## Additional Resources

- [Perplexity API Documentation](https://docs.perplexity.ai)
- [API Reference](https://docs.perplexity.ai/api-reference/chat-completions-post)
- [Pricing Page](https://docs.perplexity.ai/getting-started/pricing)

---

*Last updated: December 2025*
