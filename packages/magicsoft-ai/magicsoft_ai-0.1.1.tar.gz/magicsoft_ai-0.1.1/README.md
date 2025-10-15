# Magic Assistant Library

A Python library for building conversational AI assistants with support for dynamic tools, token counting, and time monitoring.

## Overview

Magic Assistant Library provides a framework for creating AI assistants using LangChain with support for multiple LLM providers including Google's Gemini and DeepSeek. The library handles conversation management, tool integration, token counting, and session monitoring.

## Features

- Support for multiple LLM providers (Gemini, DeepSeek)
- Dynamic tool integration and management
- Token counting and usage tracking
- Conversation history management
- Idle time monitoring
- Session management with customizable duration
- Async support for modern applications

## Requirements

- Python >=3.10
- Dependencies:
  - langchain>=0.3.23
  - langchain-community>=0.3.21
  - langchain-google-genai>=2.0.1
  - langchain-deepseek>=0.1.2
  - loguru>=0.7.0

## Installation

```bash
pip install magicai
```

## Quick Start

```python
from MagicAI import AIAgent

# Configure the assistant
config = {
    "agent_name": "MyAssistant",
    "avatar": "default",
    "do_not_talk_about": ["restricted topics"],
    "agent_task_prompt": "Your task description here",
    "initial_prompt": "Initial conversation prompt",
    "session_id": "unique_session_id",
    "task_variables": {},
    "llm": "gemini-2.0-flash",  # or "deepseek-*"
    "llm_api": "your_api_key"
}

# Create assistant instance
assistant = AIAgent(config)

# Start conversation
await assistant.start()
```

## Tool Integration

The library supports custom tool integration through the ToolManager class:

```python
tools_dict = [{
    "name": "tool_name",
    "api_url": "https://api.example.com/endpoint",
    "schema": {"type": "object", "properties": {}},
    "description": "Tool description"
}]

assistant = AIAgent(config, tools_dict=tools_dict)
```

## Callbacks

The library supports various callbacks for monitoring and control:

- Tool call notifications
- Idle time monitoring
- Session end handling
- Agent response tracking

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

- Sreedev Melethil
- Email: sreedev.melethil@magic-hire.com

## Version

Current version: 0.1.0 (Alpha)
