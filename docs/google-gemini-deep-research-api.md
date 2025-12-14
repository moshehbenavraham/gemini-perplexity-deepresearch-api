# Google Gemini Deep Research API Documentation

> Source: [Google AI Developer Documentation](https://ai.google.dev/gemini-api/docs/deep-research)

## Overview

**Gemini Deep Research** is Google's agentic research system powered by Gemini 3 Pro. It performs multi-step research through autonomous planning, execution, and synthesis, navigating complex information landscapes using web search and your own data to produce detailed, cited reports.

### Agent ID

```
deep-research-pro-preview-12-2025
```

### Core Capabilities

- **Multi-step research**: Plans → Searches → Reads → Iterates → Outputs
- **Autonomous planning and execution**
- **Web search integration** (Google Search enabled by default)
- **Private document search** via File Search stores
- **Detailed reports with citations**
- **Long-form analysis and comparative tables**
- **Steerable output formatting**

### Use Cases

- Comprehensive research reports
- Comparative analysis across multiple sources
- Academic and market research
- Document synthesis from web and private data
- Complex multi-source investigations

---

## API Architecture

### Interactions API

Deep Research uses the **Interactions API** exclusively (not `generate_content`). This API provides:

- Unified interface for models and agents
- State management and tool orchestration
- Long-running task support
- Conversation continuity

### Base URL

```
https://generativelanguage.googleapis.com/v1beta/interactions
```

### Authentication

API key passed via header:

```
x-goog-api-key: YOUR_API_KEY
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1beta/interactions` | Create new interaction |
| GET | `/v1beta/interactions/{id}` | Retrieve/poll interaction |
| DELETE | `/v1beta/interactions/{id}` | Delete stored interaction |

---

## Request Parameters

### Required Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent` | string | Must be `deep-research-pro-preview-12-2025` |
| `input` | string/array | Research prompt or content objects |
| `background` | boolean | Must be `True` (async execution required) |

### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `previous_interaction_id` | string | Link to prior interaction for follow-ups |
| `stream` | boolean | Enable real-time progress updates |
| `store` | boolean | Persist interaction (default: true, required with background) |
| `tools` | array | Tool configurations (file_search, etc.) |
| `agent_config` | object | Agent-specific settings |

### Agent Configuration

```python
agent_config = {
    "type": "deep-research",
    "thinking_summaries": "auto"  # Enable thought process visibility
}
```

### Tools Configuration

#### File Search (for private documents)

```python
tools = [
    {
        "type": "file_search",
        "file_search_store_names": ["fileSearchStores/my-store-name"]
    }
]
```

---

## Response Schema

### Interaction Object

```json
{
  "id": "interaction-unique-id",
  "status": "completed",
  "outputs": [
    {
      "text": "Detailed research report...",
      "type": "text"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 5000,
    "total_tokens": 5150
  },
  "error": null
}
```

### Status Values

| Status | Description |
|--------|-------------|
| `in_progress` | Research is ongoing |
| `completed` | Research finished successfully |
| `failed` | Research encountered an error |

### Streaming Events

| Event Type | Description |
|------------|-------------|
| `interaction.start` | Research initiated, provides interaction ID |
| `content.delta` | Incremental content updates |
| `interaction.complete` | Research finished |
| `error` | Error occurred |

### Delta Types (Streaming)

| Delta Type | Description |
|------------|-------------|
| `text` | Report content chunks |
| `thought_summary` | Agent's thinking process |

---

## Code Examples

### Python SDK Installation

```bash
pip install google-genai
```

### Basic Usage (Background Execution)

```python
import time
from google import genai

client = genai.Client()

# Start deep research
interaction = client.interactions.create(
    input="Research the history of quantum computing and its current applications.",
    agent='deep-research-pro-preview-12-2025',
    background=True
)

print(f"Research started: {interaction.id}")

# Poll for completion
while True:
    interaction = client.interactions.get(interaction.id)

    if interaction.status == "completed":
        print(interaction.outputs[-1].text)
        break
    elif interaction.status == "failed":
        print(f"Research failed: {interaction.error}")
        break

    time.sleep(10)  # Poll every 10 seconds
```

### Streaming with Real-time Updates

```python
from google import genai

client = genai.Client()

stream = client.interactions.create(
    input="Research the latest developments in renewable energy technology.",
    agent="deep-research-pro-preview-12-2025",
    background=True,
    stream=True,
    agent_config={
        "type": "deep-research",
        "thinking_summaries": "auto"
    }
)

interaction_id = None
last_event_id = None

for chunk in stream:
    if chunk.event_type == "interaction.start":
        interaction_id = chunk.interaction.id
        print(f"Interaction started: {interaction_id}")

    if chunk.event_id:
        last_event_id = chunk.event_id

    if chunk.event_type == "content.delta":
        if chunk.delta.type == "text":
            print(chunk.delta.text, end="", flush=True)
        elif chunk.delta.type == "thought_summary":
            print(f"\n[Thought]: {chunk.delta.content.text}", flush=True)

    elif chunk.event_type == "interaction.complete":
        print("\n\nResearch Complete")
```

### File Search Integration (Private Documents)

```python
import time
from google import genai

client = genai.Client()

# Research combining web and private documents
interaction = client.interactions.create(
    input="Compare our 2025 fiscal year report against current public market trends.",
    agent="deep-research-pro-preview-12-2025",
    background=True,
    tools=[
        {
            "type": "file_search",
            "file_search_store_names": ["fileSearchStores/company-docs"]
        }
    ]
)

# Poll for completion
while True:
    interaction = client.interactions.get(interaction.id)
    if interaction.status == "completed":
        print(interaction.outputs[-1].text)
        break
    elif interaction.status == "failed":
        print(f"Failed: {interaction.error}")
        break
    time.sleep(10)
```

### Follow-up Questions

```python
from google import genai

client = genai.Client()

# After initial research completes, ask follow-up
follow_up = client.interactions.create(
    input="Can you elaborate on the second point in the report?",
    model="gemini-3-pro-preview",
    previous_interaction_id="COMPLETED_INTERACTION_ID"
)

print(follow_up.outputs[-1].text)
```

### Reconnection Handling (Resilient Pattern)

```python
import time
from google import genai

client = genai.Client()

agent_name = 'deep-research-pro-preview-12-2025'
prompt = 'Comprehensive analysis of AI regulation frameworks worldwide'

last_event_id = None
interaction_id = None
is_complete = False

def process_stream(event_stream):
    global last_event_id, interaction_id, is_complete

    for event in event_stream:
        if event.event_type == "interaction.start":
            interaction_id = event.interaction.id
            print(f"Interaction started: {interaction_id}")

        if event.event_id:
            last_event_id = event.event_id

        if event.event_type == "content.delta":
            if event.delta.type == "text":
                print(event.delta.text, end="", flush=True)
            elif event.delta.type == "thought_summary":
                print(f"\n[Thought]: {event.delta.content.text}", flush=True)

        if event.event_type in ['interaction.complete', 'error']:
            is_complete = True

# Initial connection
try:
    print("Starting Research...")
    initial_stream = client.interactions.create(
        input=prompt,
        agent=agent_name,
        background=True,
        stream=True,
        agent_config={
            "type": "deep-research",
            "thinking_summaries": "auto"
        }
    )
    process_stream(initial_stream)
except Exception as e:
    print(f"\nConnection dropped: {e}")

# Reconnection loop
while not is_complete and interaction_id:
    print(f"\nResuming from event {last_event_id}...")
    time.sleep(2)

    try:
        resume_stream = client.interactions.get(
            id=interaction_id,
            stream=True,
            last_event_id=last_event_id
        )
        process_stream(resume_stream)
    except Exception as e:
        print(f"Reconnection failed, retrying... ({e})")
```

### cURL Example

```bash
# Start research
curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/interactions" \
  -H "x-goog-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "deep-research-pro-preview-12-2025",
    "input": "Research the current state of nuclear fusion technology.",
    "background": true
  }'

# Poll for results
curl -X GET \
  "https://generativelanguage.googleapis.com/v1beta/interactions/INTERACTION_ID" \
  -H "x-goog-api-key: YOUR_API_KEY"
```

---

## Pricing

### Model Inference

Deep Research uses **Gemini 3 Pro** pricing:

| Component | Cost (per 1M tokens) |
|-----------|---------------------|
| Input (≤200K context) | $2.00 |
| Input (>200K context) | $4.00 |
| Output | $12.00 - $18.00 |

### Tool Usage

| Tool | Cost |
|------|------|
| Google Search | Free through January 5, 2026 |
| Google Search (after free tier) | $35 per 1,000 queries |
| File Search | Standard token rates apply |

### Batch API

50% discount available for batch processing.

---

## Limitations

| Limitation | Details |
|------------|---------|
| Maximum research time | 60 minutes (typical: ~20 minutes) |
| Custom Function Calling | Not supported |
| MCP servers | Not supported |
| Structured output | Not supported |
| Human-approved planning | Not available |
| Audio inputs | Not supported |
| Storage requirement | `store=True` required with `background=True` |
| Status | Beta (schema may change) |

---

## Best Practices

1. **Handle missing data explicitly**: Instruct the agent on what to do when information isn't found.

2. **Provide contextual constraints**: Be specific about scope, time periods, or geographic focus in prompts.

3. **Use streaming for long research**: Enable `stream=True` to monitor progress in real-time.

4. **Implement reconnection logic**: Track `interaction_id` and `last_event_id` for network resilience.

5. **Verify citations**: Always validate sources in the final report.

6. **Use multimodal inputs cautiously**: Images/documents increase cost and token overflow risk.

7. **Steer output format**: Include formatting instructions in prompts for specific structures (tables, sections, etc.).

---

## Model Comparison

| Model | Type | Best For |
|-------|------|----------|
| Gemini 2.5 Flash | Fast inference | Quick queries, cost-effective |
| Gemini 2.5 Pro | Advanced reasoning | Complex analysis |
| Gemini 3 Pro | Flagship | Highest capability tasks |
| **Deep Research** | Agentic research | Exhaustive multi-source reports |

---

## Supported Tools

| Tool | Description | Default |
|------|-------------|---------|
| Google Search | Web search grounding | Enabled |
| URL Context | Fetch and analyze URLs | Available |
| File Search | Search private document stores | Optional |

---

## Additional Resources

- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Interactions API Reference](https://ai.google.dev/gemini-api/docs/interactions)
- [Pricing Details](https://ai.google.dev/pricing)
- [Google AI Studio](https://aistudio.google.com)

---

*Last updated: December 2025*
