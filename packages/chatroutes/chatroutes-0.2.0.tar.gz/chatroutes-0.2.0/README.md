# ChatRoutes Python SDK

[![PyPI](https://img.shields.io/pypi/v/chatroutes.svg)](https://pypi.org/project/chatroutes/)
[![Python](https://img.shields.io/pypi/pyversions/chatroutes.svg)](https://pypi.org/project/chatroutes/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chatroutes/chatroutes-python-sdk/blob/main/chatroutes_quickstart.ipynb)

Official Python SDK for the ChatRoutes API - A powerful conversation management platform with advanced branching capabilities.

> **⚠️ Beta Release**: ChatRoutes is currently in beta. The API may change without maintaining backward compatibility. Please use with caution in production environments.

## 🚀 Try It Now!

**Want to try ChatRoutes immediately?** Click the badge below to open an interactive notebook in Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chatroutes/chatroutes-python-sdk/blob/main/chatroutes_quickstart.ipynb)

No installation required - just run the cells and start experimenting!

## Installation

```bash
pip install chatroutes
```

## Getting Started

### 1. Get Your API Key

**IMPORTANT:** Before you can use ChatRoutes, you must obtain an API key:

1. **Visit** [chatroutes.com](https://chatroutes.com)
2. **Sign up** for a **free account**
3. **Go to Dashboard** → Navigate to the **API section**
4. **Generate** your API key
5. **Copy** and save your API key securely

### 2. Quick Start

```python
from chatroutes import ChatRoutes

client = ChatRoutes(api_key="your-api-key")

conversation = client.conversations.create({
    'title': 'My First Conversation',
    'model': 'gpt-5'  # or 'claude-opus-4-1', 'claude-sonnet-4-5', etc.
})

response = client.messages.send(
    conversation['id'],
    {
        'content': 'Hello, how are you?',
        'model': 'gpt-5'
    }
)

print(response['message']['content'])
```

## Supported Models

ChatRoutes currently supports the following AI models:

**OpenAI:**
- **`gpt-5`** (default) - OpenAI's GPT-5

**Anthropic Claude 4:**
- **`claude-opus-4-1`** - Claude Opus 4.1 (most capable)
- **`claude-opus-4`** - Claude Opus 4
- **`claude-opus-4-0`** - Claude Opus 4.0
- **`claude-sonnet-4-5`** - Claude Sonnet 4.5 (best for coding)
- **`claude-sonnet-4-0`** - Claude Sonnet 4.0

**Anthropic Claude 3:**
- **`claude-3-7-sonnet-latest`** - Claude 3.7 Sonnet (latest)
- **`claude-3-5-haiku-latest`** - Claude 3.5 Haiku (fastest)

**Important**: Use these exact model names. Other model names (e.g., `gpt-4o`, `gpt-4o-mini`, `claude-sonnet-4`) are not supported and will result in an error.

## Features

- **Conversation Management**: Create, list, update, and delete conversations
- **Message Handling**: Send messages with support for streaming responses
- **Branch Operations**: Create and manage conversation branches for exploring alternatives
- **Checkpoint Management**: Save and restore conversation context at specific points
- **Type Safety**: Full type hints using TypedDict for better IDE support
- **Error Handling**: Comprehensive exception hierarchy for different error scenarios
- **Retry Logic**: Built-in exponential backoff retry mechanism

## Usage Examples

### Creating a Conversation

```python
conversation = client.conversations.create({
    'title': 'Product Discussion',
    'model': 'gpt-5'
})
```

### Sending Messages

```python
response = client.messages.send(
    conversation_id='conv_123',
    data={
        'content': 'What are the key features?',
        'model': 'gpt-5',
        'temperature': 0.7
    }
)

print(response['message']['content'])  # AI response
print(f"Tokens used: {response['usage']['totalTokens']}")
```

### Streaming Responses

```python
def on_chunk(chunk):
    if chunk.get('type') == 'content' and chunk.get('content'):
        print(chunk['content'], end='', flush=True)

def on_complete(message):
    print(f"\n\nMessage ID: {message['id']}")

client.messages.stream(
    conversation_id='conv_123',
    data={'content': 'Tell me a story'},
    on_chunk=on_chunk,
    on_complete=on_complete
)
```

### Working with Branches

```python
branch = client.branches.create(
    conversation_id='conv_123',
    data={
        'title': 'Alternative Response',
        'contextMode': 'FULL'
    }
)

fork = client.branches.fork(
    conversation_id='conv_123',
    data={
        'forkPointMessageId': 'msg_456',
        'title': 'Exploring Different Approach'
    }
)
```

### Listing Conversations

```python
result = client.conversations.list({
    'page': 1,
    'limit': 10,
    'filter': 'all'
})

for conv in result['data']:
    print(f"{conv['title']} - {conv['createdAt']}")
```

### Managing Checkpoints

Checkpoints allow you to save conversation context at specific points and manage long conversations efficiently:

```python
branches = client.branches.list(conversation_id='conv_123')
main_branch = next(b for b in branches if b['isMain'])

checkpoint = client.checkpoints.create(
    conversation_id='conv_123',
    branch_id=main_branch['id'],
    anchor_message_id='msg_456'
)

print(f"Checkpoint created: {checkpoint['id']}")
print(f"Summary: {checkpoint['summary']}")
print(f"Token count: {checkpoint['token_count']}")

checkpoints = client.checkpoints.list('conv_123')
for cp in checkpoints:
    print(f"{cp['id']}: {cp['summary']}")

response = client.messages.send(
    conversation_id='conv_123',
    data={'content': 'Continue the conversation'}
)

metadata = response['message'].get('metadata', {})
if metadata.get('checkpoint_used'):
    print(f"Checkpoint was used for this response")
    print(f"Context messages: {metadata.get('context_message_count')}")
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from chatroutes import (
    ChatRoutesError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError
)

try:
    conversation = client.conversations.get('conv_123')
except AuthenticationError:
    print("Invalid API key")
except NotFoundError:
    print("Conversation not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ChatRoutesError as e:
    print(f"Error: {e.message}")
```

## API Reference

### ChatRoutes Client

```python
client = ChatRoutes(
    api_key="your-api-key",
    base_url="https://api.chatroutes.com/api/v1",  # optional
    timeout=30,  # optional, in seconds
    retry_attempts=3,  # optional
    retry_delay=1.0  # optional, in seconds
)
```

### Conversations Resource

- `create(data: CreateConversationRequest) -> Conversation`
- `list(params: ListConversationsParams) -> PaginatedResponse`
- `get(conversation_id: str) -> Conversation`
- `update(conversation_id: str, data: dict) -> Conversation`
- `delete(conversation_id: str) -> None`
- `get_tree(conversation_id: str) -> ConversationTree`

### Messages Resource

- `send(conversation_id: str, data: SendMessageRequest) -> SendMessageResponse`
- `stream(conversation_id: str, data: SendMessageRequest, on_chunk: Callable, on_complete: Callable) -> None`
- `list(conversation_id: str, branch_id: str) -> List[Message]`
- `update(message_id: str, content: str) -> Message`
- `delete(message_id: str) -> None`

### Branches Resource

- `list(conversation_id: str) -> List[Branch]`
- `create(conversation_id: str, data: CreateBranchRequest) -> Branch`
- `fork(conversation_id: str, data: ForkConversationRequest) -> Branch`
- `update(conversation_id: str, branch_id: str, data: dict) -> Branch`
- `delete(conversation_id: str, branch_id: str) -> None`
- `get_messages(conversation_id: str, branch_id: str) -> List[Message]`
- `merge(conversation_id: str, branch_id: str) -> Branch`

### Checkpoints Resource

- `list(conversation_id: str, branch_id: Optional[str] = None) -> List[Checkpoint]`
- `create(conversation_id: str, branch_id: str, anchor_message_id: str) -> Checkpoint`
- `delete(checkpoint_id: str) -> None`
- `recreate(checkpoint_id: str) -> Checkpoint`

## Type Definitions

The SDK includes comprehensive type definitions using TypedDict:

- `Conversation`
- `Message`
- `MessageMetadata` (includes checkpoint-related fields)
- `Branch`
- `Checkpoint`
- `CreateConversationRequest`
- `SendMessageRequest`
- `SendMessageResponse`
- `CreateBranchRequest`
- `ForkConversationRequest`
- `CheckpointCreateRequest`
- `CheckpointListResponse`
- `ConversationTree`
- `TreeNode`
- `ListConversationsParams`
- `PaginatedResponse`
- `StreamChunk`

## Development

### Setup

```bash
git clone https://github.com/chatroutes/chatroutes-python-sdk.git
cd chatroutes-python-sdk
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy chatroutes
```

### Code Formatting

```bash
black chatroutes
```

## License

MIT License - see LICENSE file for details

## Support

- Documentation: https://docs.chatroutes.com
- API Reference: https://api.chatroutes.com/docs
- Email: support@chatroutes.com
- GitHub Issues: https://github.com/chatroutes/chatroutes-python-sdk/issues
