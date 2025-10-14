# Chainlit Documentation

## Overview

Chainlit is a Python library that allows you to build production-ready conversational AI applications in minutes. It provides a simple and intuitive interface for creating chat-based applications with various AI frameworks.

## Installation

Install Chainlit using pip:

```sh
pip install chainlit
```

To verify the installation:

```sh
chainlit hello
```

### Development Version

The latest in-development version can be installed from GitHub:

```sh
pip install git+https://github.com/Chainlit/chainlit.git#subdirectory=backend/
```

(Requires Node and pnpm installed on the system.)

## Quick Start

### Basic Chat Application

Create a new file `app.py` with the following code:

```python
import chainlit as cl

@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back a response to the user.

    Args:
        message: The user's message.
    """
    # Send a response back to the user
    await cl.Message(content=f"You said: {message.content}").send()
```

Run your application:

```sh
chainlit run app.py -w
```

The `-w` flag enables auto-reload when you make changes to your code.

## Core Decorators and Functions

### @cl.on_message

The `@cl.on_message` decorator is used to define the main message handler. This function is called every time a user sends a message in the chat interface.

```python
@cl.on_message
async def main(message: cl.Message):
    # Your message handling logic here
    await cl.Message(content="Response").send()
```

### @cl.on_chat_start

The `@cl.on_chat_start` decorator is called when a new chat session starts. Use it for initialization:

```python
@cl.on_chat_start
async def start():
    await cl.Message(content="Welcome! How can I help you today?").send()
```

### @cl.step

The `@cl.step` decorator allows you to create intermediate steps in your processing pipeline. This is useful for showing the user what's happening behind the scenes:

```python
@cl.step(type="tool")
async def tool():
    # Simulate processing
    await cl.sleep(2)
    return "Response from the tool!"

@cl.on_message
async def main(message: cl.Message):
    # Call the tool
    tool_res = await tool()
    await cl.Message(content=tool_res).send()
```

### Sending Messages

To send a message to the user:

```python
await cl.Message(content="Your message here").send()
```

To send a message with additional elements:

```python
await cl.Message(
    content="Here's the result",
    elements=[
        cl.Text(name="Details", content="Additional information", display="inline")
    ]
).send()
```

## Working with Different AI Frameworks

Chainlit integrates seamlessly with popular AI frameworks:

### LangChain Integration

```python
import chainlit as cl
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

@cl.on_message
async def main(message: cl.Message):
    llm = OpenAI(temperature=0)
    prompt = PromptTemplate(
        input_variables=["question"],
        template="Answer this question: {question}"
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    
    response = await chain.arun(question=message.content)
    await cl.Message(content=response).send()
```

### LlamaIndex Integration

```python
import chainlit as cl
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

@cl.on_chat_start
async def start():
    # Load documents
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    # Store the query engine in the user session
    cl.user_session.set("query_engine", index.as_query_engine())
    
    await cl.Message(content="Ready to answer questions!").send()

@cl.on_message
async def main(message: cl.Message):
    query_engine = cl.user_session.get("query_engine")
    response = await query_engine.aquery(message.content)
    
    await cl.Message(content=str(response)).send()
```

## User Session

Chainlit provides a session storage mechanism to persist data across messages within a chat session:

```python
# Store data in the session
cl.user_session.set("key", value)

# Retrieve data from the session
value = cl.user_session.get("key")
```

## File Uploads

Allow users to upload files:

```python
@cl.on_message
async def main(message: cl.Message):
    # Check if files are attached
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.File):
                # Process the file
                content = element.content
                await cl.Message(content=f"Received file: {element.name}").send()
```

## Configuration

Create a `.chainlit` directory in your project root with a `config.toml` file:

```toml
[project]
# Whether to enable telemetry (default: true). No personal data is collected.
enable_telemetry = true

# List of environment variables to be provided by each user to use the app.
user_env = []

# Duration (in seconds) during which the session is saved when the connection is lost
session_timeout = 3600

# Enable third parties caching (e.g LangChain cache)
cache = false

[UI]
# Name of the app and chatbot.
name = "My Chainlit App"

# Description of the app and chatbot.
description = "A conversational AI application"

# Large size content are by default collapsed for a cleaner ui
default_collapse_content = true

# The default value for the expand messages settings.
default_expand_messages = false

# Hide the chain of thought details from the user in the UI.
hide_cot = false

# Link to your github repo. This will add a github button in the UI's header.
# github = "https://github.com/your/repo"

[UI.theme]
# Override default MUI light theme. (Check theme.ts)
[UI.theme.light]
    background = "#FAFAFA"
    paper = "#FFFFFF"

    [UI.theme.light.primary]
        main = "#F80061"
        dark = "#980039"
        light = "#FFE7EB"
```

## Best Practices

1. **Use async/await**: Chainlit is built on asyncio, so make your functions async for best performance
2. **Manage state with user_session**: Store conversation context and data using `cl.user_session`
3. **Show progress**: Use `@cl.step` to show users intermediate steps in long-running operations
4. **Handle errors gracefully**: Wrap your code in try-except blocks and send friendly error messages
5. **Use the `-w` flag during development**: This enables auto-reload for faster iteration

## Advanced Features

### Streaming Responses

Stream responses token by token for better UX:

```python
@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    
    async for token in your_streaming_function():
        await msg.stream_token(token)
    
    await msg.send()
```

### Ask for User Input

Prompt the user for additional input:

```python
@cl.on_message
async def main(message: cl.Message):
    res = await cl.AskUserMessage(content="What's your preference?", timeout=30).send()
    
    if res:
        await cl.Message(content=f"You chose: {res['content']}").send()
```

### Action Buttons

Add interactive buttons to messages:

```python
actions = [
    cl.Action(name="action1", value="value1", label="Option 1"),
    cl.Action(name="action2", value="value2", label="Option 2")
]

await cl.Message(content="Choose an option:", actions=actions).send()

@cl.action_callback("action1")
async def on_action(action):
    await cl.Message(content="You clicked Option 1!").send()
```

## Resources

- **Documentation**: https://docs.chainlit.io
- **GitHub**: https://github.com/Chainlit/chainlit
- **Cookbook**: https://github.com/Chainlit/cookbook
- **Discord**: https://discord.gg/k73SQ3FyUh
- **Help**: https://help.chainlit.io

## License

Chainlit is open-source and licensed under the Apache 2.0 license.
