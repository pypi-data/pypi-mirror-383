# Chainlit

> Chainlit is an open-source Python package to build production ready Conversational AI applications with authentication, data persistence, and multi-platform support.

<!-- sep---sep -->

## What is Chainlit?

Chainlit enables developers to rapidly build and deploy Conversational AI applications with a focus on user experience and production readiness. The framework provides a complete solution for creating chat-based applications that integrate with any Python program or library.

Chainlit addresses the challenge of building production-grade conversational applications by providing built-in authentication, data persistence, multi-step reasoning visualization, and seamless integration with popular AI frameworks. It allows developers to focus on their AI logic rather than building UI components and infrastructure from scratch.

<!-- sep---sep -->

## Key Features

Chainlit provides comprehensive features for building production-ready conversational applications:

- **Build Fast**: Get started with just a couple lines of Python code
- **Authentication**: Integrate with corporate identity providers and existing authentication infrastructure (OAuth, Password, Header-based)
- **Data Persistence**: Collect, monitor and analyze data from your users with built-in chat history and feedback collection
- **Visualize Multi-Steps Reasoning**: Understand the intermediary steps that produced an output at a glance using the Step abstraction
- **Multi-Platform**: Write your assistant logic once, deploy everywhere with consistent behavior across platforms
- **Streaming Support**: Stream responses token-by-token for better user experience
- **Multi-Modal Support**: Handle text, images, audio, video, and file uploads in conversations
- **Testing & Debugging**: Built-in tools for testing and debugging your conversational applications

<!-- sep---sep -->

## Core Concepts

### Chat Life Cycle

The Chainlit application follows a structured life cycle with specific hooks for different events:

- **`@cl.on_chat_start`**: Called when a new chat session starts, perfect for initialization logic
- **`@cl.on_message`**: Called every time a user sends a message, the main message handler
- **`@cl.on_chat_end`**: Called when a chat session ends, useful for cleanup
- **`@cl.on_chat_resume`**: Called when resuming a previous chat session

### Message

The `Message` class is the primary way to communicate with users. Messages can include:
- Text content
- Elements (images, files, text blocks, PDFs)
- Actions (interactive buttons)
- Author information

### Step

A `Step` represents an intermediary operation in your application. Steps help users understand what's happening behind the scenes and are crucial for debugging and transparency. Steps can be nested to show hierarchical operations and support different types like "tool", "llm", "embedding", etc.

### User Session

The user session provides a way to store data that persists across messages within a single chat session. Use `cl.user_session.set()` and `cl.user_session.get()` to manage session state without relying on global variables.

### Element

Elements are rich content types that can be attached to messages:
- **Text**: Display formatted text blocks
- **Image**: Show images inline or as side content
- **File**: Attach downloadable files
- **Audio**: Embed audio content
- **Video**: Embed video content
- **PDF**: Display PDF documents

### Action

Actions are interactive buttons that users can click. They enable rich interactions beyond simple text responses and can trigger callbacks in your application code.

<!-- sep---sep -->

## Integration Support

Chainlit is compatible with all Python programs and libraries, with dedicated integrations for popular AI frameworks:

**LangChain**: Seamless integration with LangChain agents, chains, and callbacks for automatic step visualization

**OpenAI**: Direct support for OpenAI API calls with automatic streaming and function calling

**OpenAI Assistant**: Full integration with OpenAI Assistants API including thread management

**Mistral AI**: Native support for Mistral AI models and API calls

**Llama Index**: Integration with Llama Index agents, query engines, and chat engines with automatic step tracking

**Semantic Kernel**: Support for Microsoft Semantic Kernel agents and skills

**Autogen**: Integration with Microsoft Autogen multi-agent frameworks

<!-- sep---sep -->

## Basic Application Structure

A minimal Chainlit application follows this pattern:

```python
import chainlit as cl

@cl.on_chat_start
async def start():
    # Initialize your application
    # Set up models, load data, etc.
    await cl.Message(content="Welcome! How can I help you?").send()

@cl.on_message
async def main(message: cl.Message):
    # Process the user's message
    # Call your AI logic
    response = process_message(message.content)
    
    # Send response back to user
    await cl.Message(content=response).send()
```

### Showing Intermediate Steps

Use the `@cl.step` decorator to show users what's happening:

```python
@cl.step(type="tool")
async def retrieve_documents(query: str):
    # Simulate document retrieval
    results = search_documents(query)
    return results

@cl.on_message
async def main(message: cl.Message):
    # This step will be visible in the UI
    docs = await retrieve_documents(message.content)
    
    response = generate_response(docs, message.content)
    await cl.Message(content=response).send()
```

### Managing Session State

Store data across messages using the user session:

```python
@cl.on_chat_start
async def start():
    # Initialize and store in session
    query_engine = create_query_engine()
    cl.user_session.set("query_engine", query_engine)

@cl.on_message
async def main(message: cl.Message):
    # Retrieve from session
    query_engine = cl.user_session.get("query_engine")
    response = query_engine.query(message.content)
    await cl.Message(content=str(response)).send()
```

<!-- sep---sep -->

## Advanced Features

### Streaming

Stream responses token-by-token for better UX:

```python
@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    
    # Stream tokens as they arrive
    for token in stream_from_llm(message.content):
        await msg.stream_token(token)
    
    # Send the final message
    await msg.send()
```

### Ask User

Prompt users for additional input during processing:

```python
@cl.on_message
async def main(message: cl.Message):
    # Ask for clarification
    res = await cl.AskUserMessage(
        content="What format would you like?", 
        timeout=30
    ).send()
    
    if res:
        format_choice = res['content']
        # Process with user's choice
```

### Chat Profiles

Support multiple AI assistants or modes:

```python
@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(name="Assistant", icon="💬"),
        cl.ChatProfile(name="Code Helper", icon="💻"),
    ]

@cl.on_chat_start
async def start():
    profile = cl.user_session.get("chat_profile")
    # Initialize based on selected profile
```

### Chat Settings

Allow users to customize behavior with real-time settings:

```python
@cl.on_settings_update
async def setup_agent(settings):
    temperature = settings["temperature"]
    # Update your AI configuration
    cl.user_session.set("temperature", temperature)
```

### Starters

Provide suggested prompts to help users get started:

```python
@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Explain quantum computing",
            message="Can you explain quantum computing in simple terms?",
        ),
        cl.Starter(
            label="Write a poem",
            message="Write a short poem about AI",
        ),
    ]
```

<!-- sep---sep -->

## Data Persistence

### Chat History

Chainlit supports persistent chat history across sessions. Configure a data layer to automatically save and restore conversations.

### Human Feedback

Collect user feedback on messages:

```python
@cl.on_message
async def main(message: cl.Message):
    response = generate_response(message.content)
    
    # Users can provide feedback (thumbs up/down)
    msg = await cl.Message(content=response).send()
    
    # Access feedback later via data persistence layer
```

### Tags & Metadata

Attach custom metadata to conversations for analytics:

```python
@cl.on_chat_start
async def start():
    # Tag conversations for filtering and analysis
    cl.user_session.set("tags", ["customer-support", "billing-question"])
```

<!-- sep---sep -->

## Authentication

Chainlit provides multiple authentication methods:

**Password Authentication**: Simple username/password authentication for small teams

**Header-Based Authentication**: Integrate with existing authentication proxies

**OAuth**: Support for OAuth providers (Google, GitHub, Azure AD, Okta, etc.)

Configure authentication in your Chainlit configuration file to control access to your application.

<!-- sep---sep -->

## Customization

Chainlit applications can be fully customized:

- **Theme**: Customize colors, fonts, and styling via configuration
- **Logo and Favicon**: Add your company branding
- **Avatars**: Customize user and assistant avatars
- **Custom CSS**: Add custom styling for complete control
- **Custom JavaScript**: Extend functionality with custom JS
- **Translation**: Support multiple languages with i18n

<!-- sep---sep -->

## Model Context Protocol (MCP)

Chainlit supports the Model Context Protocol (MCP), allowing AI assistants to securely access tools and data sources. MCP enables:

- Tool discovery and execution
- Resource access (files, databases, APIs)
- Prompt templates
- Standardized communication between AI models and data sources

<!-- sep---sep -->

## Deployment

Chainlit applications can be deployed on various platforms:

- **Docker**: Containerize your application for consistent deployment
- **Cloud Platforms**: Deploy to AWS, GCP, Azure, or other cloud providers
- **Chainlit Cloud**: Use the official hosted solution for zero-config deployment
- **On-Premise**: Deploy within your corporate infrastructure

Chainlit applications are production-ready by default with built-in security, authentication, and monitoring capabilities.

<!-- sep---sep -->

## Getting Started

To get started with Chainlit:

1. **[Installation](https://docs.chainlit.io/get-started/installation)**: Install Chainlit using pip
2. **[Pure Python Example](https://docs.chainlit.io/get-started/pure-python)**: Create your first chat application
3. **[Choose Integration](https://docs.chainlit.io/integrations)**: Add LangChain, LlamaIndex, or other framework integration
4. **[Add Features](https://docs.chainlit.io/concepts)**: Implement streaming, steps, file uploads, and authentication
5. **[Deploy](https://docs.chainlit.io/deploy)**: Deploy to production

<!-- sep---sep -->

## Documentation and Resources

### Getting Started

- [Overview](https://docs.chainlit.io/get-started/overview) - Introduction to Chainlit and key features
- [Installation](https://docs.chainlit.io/get-started/installation) - Setup and installation instructions
- [Pure Python](https://docs.chainlit.io/get-started/pure-python) - Build your first chat application
- [Integrations](https://docs.chainlit.io/integrations) - Connect with AI frameworks

### Core Concepts

- [Chat Life Cycle](https://docs.chainlit.io/concepts/chat-lifecycle) - Understanding the application flow
- [Message](https://docs.chainlit.io/concepts/message) - Sending and receiving messages
- [Step](https://docs.chainlit.io/concepts/step) - Visualizing intermediate operations
- [User Session](https://docs.chainlit.io/concepts/user-session) - Managing session state
- [Element](https://docs.chainlit.io/concepts/element) - Rich content and file handling
- [Action](https://docs.chainlit.io/concepts/action) - Interactive buttons and callbacks
- [Starters](https://docs.chainlit.io/concepts/starters) - Suggested prompts for users

### Advanced Features

- [Streaming](https://docs.chainlit.io/advanced-features/streaming) - Token-by-token response streaming
- [MCP](https://docs.chainlit.io/advanced-features/mcp) - Model Context Protocol integration
- [Ask User](https://docs.chainlit.io/advanced-features/ask-user) - Interactive user prompts
- [Multi-Modality](https://docs.chainlit.io/advanced-features/multi-modality) - Handling images, audio, and video
- [Chat Profiles](https://docs.chainlit.io/advanced-features/chat-profiles) - Multiple AI assistants
- [Chat Settings](https://docs.chainlit.io/advanced-features/chat-settings) - User-configurable settings
- [Testing & Debugging](https://docs.chainlit.io/advanced-features/testing) - Development tools

### Data & Authentication

- [Data Persistence](https://docs.chainlit.io/data-persistence) - Saving conversations and feedback
- [Authentication](https://docs.chainlit.io/authentication) - User authentication methods
- [Customization](https://docs.chainlit.io/customisation) - Theming and branding

### Deployment

- [Deployment Overview](https://docs.chainlit.io/deploy/overview) - Production deployment strategies
- [Platforms](https://docs.chainlit.io/deploy/platforms) - Platform-specific guides

Chainlit provides a complete solution for building conversational AI applications with production-grade features and seamless integration with the Python AI ecosystem.
