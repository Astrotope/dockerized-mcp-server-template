# Dockerized MCP Server Template

This repository provides a reusable template for a Python server implementing the **Model Context Protocol (MCP)**, running in a Docker container and utilizing Streamable HTTP for real-time communication. Built on the Python implementation of the Model Context Protocol (MCP), this template enables easy integration with Large Language Models (LLMs).

## What is MCP?

The **[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction)** lets you build servers that expose data and functionality to LLM applications in a secure, standardized way. 

This template demonstrates a production-ready MCP server running in a Docker container, utilizing stateless Streamable HTTP for real-time communication.

## Project Structure

```
dockerized-mcp-server-template/
├── src/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server.py
├── docker-compose.yml
└── README.md
```

## Getting Started

### Build and Run with Docker Compose

```bash
docker-compose up --build
```

The server will be accessible at:

```
http://localhost:8080/mcp
```

### Running Directly (without Docker)

Alternatively, you can run the server directly using Python. First, install dependencies:

```bash
pip install -r src/requirements.txt
```

Then run the server:

```bash
python src/server.py
```

The server will be accessible at:

```
http://localhost:8080/mcp
```

## Example Usage

The example includes a simple MCP tool function `add`:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
```

You can invoke this tool via MCP client requests.

## Technical Notes

This template uses Streamable HTTP transport, which is available in the Model Context Protocol starting with the Python SDK v1.8.0 (https://github.com/modelcontextprotocol/python-sdk). 

## Why Streamable HTTP?

Streamable HTTP significantly improves upon the previous SSE transport by enabling stateless operation, making MCP compatible with serverless architectures and standard web infrastructure. This approach eliminates the need for persistent connections, resulting in better resource efficiency and cost effectiveness, while offering a more straightforward implementation for developers. The result is an MCP server that's easier to deploy, more scalable, and more resource-efficient without sacrificing functionality.

## Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)