# PicoAgents

A minimal multi-agent framework for educational purposes, accompanying the book "Designing Multi-Agent Systems: Principles, Patterns, and Implementation for AI Agents" by Victor Dibia.

> Note: While the principles in this library are "production-ready" and mirror many of the decisions made in real-world multi-agent frameworks, careful consideration should be given before using it in production environments.

**🎯 From Theory to Implementation**: Every concept in the book has a complete, tested implementation you can learn from and extend.

## Why PicoAgents?

Most multi-agent tutorials show you toy examples. This book—and PicoAgents—shows you how to build production systems from first principles:

| What You Learn              | What You Build                                       | Real Impact                              |
| --------------------------- | ---------------------------------------------------- | ---------------------------------------- |
| **Agent Architecture**      | Complete `Agent` class with reasoning, tools, memory | Deploy agents that solve actual tasks    |
| **Workflow Orchestration**  | Type-safe, streaming workflow engine                 | Build reliable multi-step AI systems     |
| **Autonomous Coordination** | AI-driven agent orchestration patterns               | Create adaptive, self-organizing teams   |
| **Production Deployment**   | Evaluation, monitoring, error handling               | Ship multi-agent systems with confidence |

- **Battle-tested patterns**: Implements proven architectures from production multi-agent systems
- **Complete implementations**: No black boxes—see exactly how agents, workflows, and orchestration work
- **Type-safe**: Full typing support for robust production code
- **Extensible**: Designed for experimentation and customization

## Installation

```bash
# Install from PyPI (when published)
pip install picoagents

# Or install from source
git clone <repository-url>
cd picoagents
pip install -e .
```

### API Key Setup

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Quick Start

### Building Your First Agent (Chapter 4)

```python
from picoagents import Agent, OpenAIChatCompletionClient

def get_weather(location: str) -> str:
    """Get current weather for a given location."""
    return f"The weather in {location} is sunny, 75°F"

# Create an agent - that's it!
agent = Agent(
    name="assistant",
    instructions="You are helpful. Use tools when appropriate.",
    model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"),
    tools=[get_weather]  # Functions become tools automatically!
)

# Use the agent
response = await agent.run("What's the weather in Paris?")
print(response.messages[-1].content)
# Output: "The weather in Paris is sunny, 75°F"
```

### Multi-Agent Workflows (Chapter 5)

```python
from picoagents.orchestration.workflow import Workflow, WorkflowRunner, FunctionStep

# Define workflow steps
def research_step(topic: str) -> str:
    return f"Research findings on {topic}"

def write_step(research: str) -> str:
    return f"Article based on: {research}"

# Create type-safe workflow
workflow = Workflow("content_pipeline")
workflow.add_step(FunctionStep("research", research_step))
workflow.add_step(FunctionStep("write", write_step))
workflow.add_edge("research", "write")

# Run with streaming observability
runner = WorkflowRunner(workflow)
result = await runner.run({"topic": "renewable energy"})
```

### Autonomous Orchestration (Chapter 6)

```python
from picoagents import Agent, OpenAIChatCompletionClient
from picoagents.orchestration import RoundRobinOrchestrator

# Create specialized agents
researcher = Agent(
    name="researcher",
    instructions="Research topics and provide factual insights.",
    model_client=OpenAIChatCompletionClient(model="gpt-4o-mini")
)

writer = Agent(
    name="writer",
    instructions="Write engaging content based on research.",
    model_client=OpenAIChatCompletionClient(model="gpt-4o-mini")
)

# Create orchestrator with termination conditions
orchestrator = RoundRobinOrchestrator(
    "content_team",
    agents=[researcher, writer],
    max_messages=10  # Prevent runaway execution
)

# Agents coordinate autonomously
result = await orchestrator.orchestrate("Write about renewable energy trends")
```

## What You'll Learn & Build

| Chapter   | Concept                 | Implementation                             | Example                                                                          |
| --------- | ----------------------- | ------------------------------------------ | -------------------------------------------------------------------------------- |
| **Ch 4**  | Agent Architecture      | `Agent` with reasoning, tools, memory      | [`agents/`](examples/agents/) - Basic agents, tools, memory                      |
| **Ch 5**  | Workflow Orchestration  | Type-safe `Workflow` + `WorkflowRunner`    | [`workflows/`](examples/workflows/) - Sequential, conditional, parallel          |
| **Ch 6**  | Autonomous Coordination | `RoundRobinOrchestrator`, `AIOrchestrator` | [`orchestration/`](examples/orchestration/) - Round-robin, AI-driven, plan-based |
| **Ch 8**  | Evaluation Systems      | Testing framework + metrics                | [`evaluation/`](examples/evaluation/) - Agent evaluation patterns                |
| **Ch 12** | Real-World Apps         | Complete case study                        | Multi-perspective information processing                                         |

### Core Architecture

**Agent Foundation**: Every agent implements the universal pattern: `reason → act → communicate → adapt`

**Workflow Control**: Deterministic execution with type safety and streaming observability

**Autonomous Orchestration**: AI-driven coordination with robust termination conditions

## Architecture

```
src/picoagents/
├── agents.py          # Core Agent implementation
├── multiagent.py      # High-level system coordination
├── workflow/          # Explicit control patterns
│   ├── base.py        # Base classes and abstractions
│   ├── sequential.py  # Sequential workflow pattern
│   ├── conditional.py # Conditional/branching workflows
│   └── parallel.py    # Parallel execution patterns
└── orchestration/     # Autonomous control patterns
    ├── base.py        # Base orchestration classes
    ├── roundrobin.py  # Round-robin coordination
    ├── llm.py         # LLM-based coordination
    └── planner.py     # Plan-based orchestration
```

## Examples

Complete implementations organized by concept:

- **Agents** ([`agents/`](examples/agents/)) - Basic agents, tools, memory, structured output (Chapter 4)
- **Orchestration** ([`orchestration/`](examples/orchestration/)) - Round-robin, AI-driven, plan-based coordination (Chapter 6)
- **Workflows** ([`workflows/`](examples/workflows/)) - Sequential, conditional, parallel execution patterns (Chapter 5)
- **Evaluation** ([`evaluation/`](examples/evaluation/)) - Agent evaluation and metrics (Chapter 8)

**📖 Get the Book**: Each example directory corresponds to book chapters with detailed explanations, trade-offs, and production considerations.

## Development

Install with development dependencies:

```bash
pip install -e ".[dev]"
```

### Code Quality Commands

```bash
# Type checking
python -m mypy --show-error-codes --ignore-missing-imports src/
python -m pyright src/ examples/ tests/

# Code formatting
python -m black src/ examples/ tests/
python -m isort src/ examples/ tests/

# Testing
python -m pytest tests/
```

## Requirements

- Python 3.9+
- OpenAI API key (set `OPENAI_API_KEY` environment variable)
- Optional: Other LLM providers (configure in agent initialization)

## Contributing

This is an educational framework designed to accompany the book. Contributions should:

1. Maintain clarity and simplicity
2. Include comprehensive documentation
3. Follow the established patterns
4. Include tests and type hints

## License

MIT License - see LICENSE file for details.

## Get the Book

**"Designing Multi-Agent Systems: Principles, Patterns, and Implementation for AI Agents"** by Victor Dibia

This framework implements every concept from the book with production-ready code. The book provides:

- **Deep explanations** of when and why to use each pattern
- **Trade-off analysis** for production decision-making
- **Real-world case studies** with complete implementations
- **Evaluation frameworks** for measuring system performance

## Citation

```bibtex
@book{dibia2025multiagent,
  title={Designing Multi-Agent Systems: Principles, Patterns, and Implementation for AI Agents},
  author={Dibia, Victor},
  year={2025}
}
```
