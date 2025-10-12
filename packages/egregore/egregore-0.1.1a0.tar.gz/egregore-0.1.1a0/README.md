# Egregore

**AI Task Management and Workflow Orchestration Framework**

Egregore is a powerful Python framework that provides developers with **two complementary programming interfaces** for building AI-powered applications: a simple **Agent Interface** for conversational AI and a sophisticated **Workflow Interface** for process orchestration.
Its a reimagining of what context is supposed to be? I mean do you really need to have the same format every time? Does that reminder really need to stay in the context?
Egregore treats context like virtual DOM in order to manipulate certain elements and manage their lifecycle
Egregore core llm model is an Agents as actors, giving them an operating system to actually full fill their task with minimal deviation


## 🚀 Quick Start

```python
# Simple Agent Interface - Conversational AI
from egregore.core.agent import Agent

# Create agent with provider:model syntax
agent = Agent(provider="openai:gpt-4o")

# Or use default model
agent = Agent(provider="openai")

response = agent("Analyze this sales data and provide insights")

# Workflow Interface - Process Orchestration  
from egregore.core.workflow import Sequence
from egregore.core.workflow.base_node import node

@node
def data_extraction_node(data):
    return extract_data(data)

workflow = Sequence(
    data_extraction_node >>
    validation_node >> 
    analysis_node >>
    report_generation_node
)

result = await workflow.execute(input_data)
```

## 🏗️ Dual Interface Architecture

### 1. **Agent Interface** - Simple Conversational AI
Perfect for chat applications, AI assistants, and quick AI integrations:

```python
from egregore.core.agent import Agent

# Direct agent interaction
agent = Agent(provider="openai")
response = agent("Generate a summary report")

# Async for better performance
response = await agent.acall("Analyze data")
```

### 2. **Workflow Interface** - Granular Process Orchestration  
Ideal for production pipelines, ETL processes, and complex business logic:

```python
from egregore.core.workflow import Sequence
from egregore.core.workflow.base_node import node

@node
def data_extraction_node(data):
    return extract_data(data)

workflow = Sequence(
    data_extraction_node >>
    validation_node >> 
    analysis_node >>
    report_generation_node
)

result = await workflow.execute(input_data)
```

### 3. **Composed Interface** - Agents within Workflows
Combine both for hybrid approaches - structured processes with AI intelligence:

```python
from egregore.core.agent import Agent
from egregore.core.workflow import Sequence
from egregore.core.workflow.base_node import node

# Create agents
analyst_agent = Agent(provider="anthropic")
reviewer_agent = Agent(provider="openai")

@node
def data_extraction_node(data):
    return extract_data(data)

@node
def validation_node(data):
    return validate(data)

# Use agent() method to create AgentNodes
workflow = Sequence(
    data_extraction_node >>
    analyst_agent("analyst") >>  # Creates AgentNode
    validation_node >>
    reviewer_agent("reviewer") >>  # Creates AgentNode
    report_generation_node
)
```

## ✨ Key Features

- **🔄 Dual Interface Design**: Choose the right abstraction level for your use case
- **⚡ Native Async Support**: Improved performance for concurrent operations
- **🔌 Pluggable LLM Providers**: OpenAI, Anthropic, Google, with easy extensibility
- **🛠️ Advanced Tool Calling**: Function calling with concurrent execution
- **🧠 Smart Memory Management**: Context compression and persistence
- **📊 Built-in Scaffolds**: Development environment, task management, and more
- **🔗 Composable Architecture**: Agents work as workflow nodes for hybrid approaches

## 📦 Installation

```bash
pip install egregore
```

Or install from source:

```bash
git clone https://github.com/your-repo/egregore.git
cd egregore
pip install -e .
```

## 🎯 Use Cases

### Agent Interface
- **Chat Applications**: Build conversational AI interfaces
- **AI Assistants**: Create intelligent assistants for various domains
- **Quick AI Integration**: Add AI capabilities to existing applications
- **Exploratory Analysis**: Interactive data analysis and insights

### Workflow Interface
- **Production Pipelines**: Orchestrate complex data processing workflows
- **ETL Processes**: Extract, transform, and load data with AI enhancement
- **Business Logic**: Implement deterministic business processes
- **Multi-step Automation**: Chain together multiple processing steps

### Composed Interface
- **Hybrid Systems**: Combine structured processes with AI intelligence
- **Smart Pipelines**: Add AI decision-making to deterministic workflows
- **Quality Assurance**: Use AI agents for validation and review steps
- **Dynamic Routing**: Let AI agents determine workflow paths

## 🏃‍♂️ Getting Started

1. **[Installation & Setup](documentation/getting-started.md)** - Get up and running quickly
2. **[Core Concepts](documentation/core-concepts.md)** - Understand the architecture
3. **[Agent Interface Guide](documentation/agent-interface.md)** - Learn conversational AI
4. **[Workflow Interface Guide](documentation/workflow-interface.md)** - Master process orchestration

## 📚 Documentation

Comprehensive documentation is available in the [`documentation/`](documentation/) directory:

- [Getting Started](documentation/getting-started.md) - Installation, setup, and quick start
- [Core Concepts & Architecture](documentation/core-concepts.md) - Understanding Egregore's design
- [Agent Interface](documentation/agent-interface.md) - Conversational AI interface
- [Workflow Interface](documentation/workflow-interface.md) - Process orchestration interface  
- [Provider System](documentation/provider-system.md) - LLM provider integration
- [Model Configuration](documentation/model-configuration.md) - Model validation and auto-selection
- [Message System](documentation/message-system.md) - Message handling and threading
- [Tool System](documentation/tool-system.md) - Function calling and custom tools
- [Memory & Context](documentation/memory-context.md) - Context management and persistence
- [Built-in Tools](documentation/builtin-tools.md) - DSS tools and scaffolds
- [API Reference](documentation/api-reference.md) - Complete API documentation
- [Development Guide](documentation/development-guide.md) - Contributing and extending
- [Examples & Tutorials](documentation/examples-tutorials.md) - Practical examples

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](documentation/development-guide.md) for details on:

- Setting up the development environment
- Running tests
- Adding new LLM providers
- Contributing to documentation
- Submitting pull requests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with love for the AI development community
- Inspired by the need for flexible AI orchestration tools
- Thanks to all contributors and users who make this project possible