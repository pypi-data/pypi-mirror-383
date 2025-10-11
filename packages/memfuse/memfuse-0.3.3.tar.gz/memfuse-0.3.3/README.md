<a id="readme-top"></a>

[![GitHub license](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/Percena/MemFuse/blob/readme/LICENSE)

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://memfuse.vercel.app/">
    <img src="https://raw.githubusercontent.com/memfuse/memfuse-python/refs/heads/main/assets/logo.png" alt="MemFuse Logo"
         style="max-width: 90%; height: auto; display: block; margin: 0 auto; padding-left: 16px; padding-right: 16px;">
  </a>
  <br />

  <p align="center">
    <strong>MemFuse Python SDK</strong>
    <br />
    The official Python client for MemFuse, the open-source memory layer for LLMs.
    <br />
    <a href="https://memfuse.vercel.app/"><strong>Explore the Docs »</strong></a>
    <br />
    <br />
    <a href="https://memfuse.vercel.app/">View Demo</a>
    &middot;
    <a href="https://github.com/memfuse/memfuse-python/issues">Report Bug</a>
    &middot;
    <a href="https://github.com/memfuse/memfuse-python/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-memfuse">About MemFuse</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#quick-start">Quick Start</a></li>
    <li><a href="#examples">Examples</a></li>
    <li><a href="#documentation">Documentation</a></li>
    <li><a href="#community--support">Community & Support</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

## About MemFuse

Large language model applications are inherently stateless by design.
When the context window reaches its limit, previous conversations, user preferences, and critical information simply disappear.

**MemFuse** bridges this gap by providing a persistent, queryable memory layer between your LLM and storage backend, enabling AI agents to:

- **Remember** user preferences and context across sessions
- **Recall** facts and events from thousands of interactions later
- **Optimize** token usage by avoiding redundant chat history resending
- **Learn** continuously and improve performance over time

This repository contains the official Python SDK for seamless integration with MemFuse servers. For comprehensive information about the MemFuse server architecture and advanced features, please visit the [MemFuse Server repository](https://github.com/memfuse/memfuse).

## Recent Updates

- **Enhanced Testing:** Comprehensive E2E testing with semantic memory validation
- **Better Error Handling:** Improved error messages and logging for easier debugging  
- **Prompt Templates:** Structured prompt management system for consistent LLM interactions
- **Performance Benchmarks:** MSC dataset accuracy testing with 95% validation threshold

## Installation

> **Note:** This is the standalone Client SDK repository. If you need to install and run the MemFuse server, which is essential to use the SDK, please visit the [MemFuse Server repository](https://github.com/memfuse/memfuse).

You can install the MemFuse Python SDK using one of the following methods:

**Option 1: Install from PyPI (Recommended)**

```bash
pip install memfuse
```

**Option 2: Install from Source**

```bash
git clone https://github.com/memfuse/memfuse-python.git
cd memfuse-python
pip install -e .
```

### Optional extras

Some features are optional and shipped as extras:

- UI (Gradio demo UIs)
  - pip: `pip install "memfuse[ui]"`
  - poetry: add the `ui` extra

- Full (includes UI)
  - pip: `pip install "memfuse[full]"`
  - poetry: add the `full` extra

The Gradio-based examples in `examples/` require the `ui` extra. If you run those scripts without the extra installed, they will raise: `RuntimeError('Install memfuse[ui] to use the demo UI.')`.

## Quick Start

Here's a comprehensive example demonstrating how to use the MemFuse Python SDK with OpenAI:

```python
from memfuse.llm import OpenAI
from memfuse import MemFuse
import os


memfuse_client = MemFuse(
  # api_key=os.getenv("MEMFUSE_API_KEY")
  # base_url=os.getenv("MEMFUSE_BASE_URL"),
)

memory = memfuse_client.init(
  user="alice",
  # agent="agent_default",
  # session=<randomly-generated-uuid>
)

# Initialize your LLM client with the memory scope
llm_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # Your OpenAI API key
    memory=memory
)

# Make a chat completion request
response = llm_client.chat.completions.create(
    model="gpt-4o", # Or any model supported by your LLM provider
    messages=[{"role": "user", "content": "I'm planning a trip to Mars. What is the gravity there?"}]
)

print(f"Response: {response.choices[0].message.content}")
# Example Output: Response: Mars has a gravity of about 3.721 m/s², which is about 38% of Earth's gravity.
```

### Contextual Follow-up

Now, ask a follow-up question. MemFuse will automatically recall relevant context from the previous conversation:

```python
# Ask a follow-up question. MemFuse automatically recalls relevant context.
followup_response = llm_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What are some challenges of living on that planet?"}]
)

print(f"Follow-up: {followup_response.choices[0].message.content}")
# Example Output: Follow-up: Some challenges of living on Mars include its thin atmosphere, extreme temperatures, high radiation levels, and the lack of liquid water on the surface.
```

MemFuse automatically manages the retrieval of relevant information and storage of new memories from conversations within the specified `memory` scope.

## Advanced Features

### Memory Validation & Testing
The SDK includes comprehensive testing capabilities to validate memory accuracy:

- **E2E Memory Tests:** Automated tests that verify conversational context retention
- **Semantic Similarity Validation:** Uses RAGAS framework for intelligent response verification
- **Performance Benchmarks:** MSC (Multi-Session Chat) dataset testing with accuracy metrics

### Error Handling & Debugging
Enhanced error messages provide clear guidance:

- **Connection Issues:** Helpful instructions for starting the MemFuse server
- **API Errors:** Detailed error responses with actionable information
- **Logging:** Comprehensive logging for troubleshooting and monitoring

## Examples

Explore comprehensive examples in the [examples/](examples/) directory of this repository, featuring:

- **Basic Operations:** Fundamental usage patterns and asynchronous operations
- **Conversation Continuity:** Maintaining context across multiple interactions
- **UI Integrations:** Gradio-based chatbot implementations with streaming support

## Documentation

- **Server Documentation:** For detailed information about the MemFuse server architecture and advanced configuration, visit the [MemFuse online documentation](https://memfuse.vercel.app/)
- **SDK Documentation:** Comprehensive API references and guides will be available soon

## Community & Support

Join our growing community:

- **GitHub Discussions:** Participate in roadmap discussions, RFCs, and Q&A in the [MemFuse Server repository](https://github.com/memfuse/memfuse)
- **Issues & Features:** Report bugs or request features in this repository's [Python SDK Issues section](https://github.com/memfuse/memfuse-python/issues)

If MemFuse enhances your projects, please ⭐ star both the [server repository](https://github.com/memfuse/memfuse) and this SDK repository!

## License

This MemFuse Python SDK is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for complete details.
