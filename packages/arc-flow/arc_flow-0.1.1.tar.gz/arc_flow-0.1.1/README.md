﻿
## Arc Flow (arc_flow)

Arc Flow is a professional hierarchical multi-agent framework for building, composing,
and orchestrating agent-based workflows. It provides primitives for defining coordinators,
planners, supervisors, teams and nodes, plus ready-to-use workflow patterns such as
sequential pipelines and graph-based orchestrations.

This repository contains the `arc_flow` package — a modular, extensible toolkit for
research and production systems that require structured multi-agent reasoning.

Key goals:

- Make it easy to build hierarchical agent graphs (coordinator -> planner -> teams -> generator).
- Provide opinionated workflow patterns (sequential, swarm, hierarchical) out of the box.
- Include safe defaults for validation, cycle-detection, and persistence.
- Keep the API small and testable so teams can extend and replace components.

## Features

- GraphOrchestrator: build and compile directed workflows with cycle detection and checkpointing.
- Supervisor and Team abstractions: manage groups of agents and their lifecycle.
- Pre-built workflows: SequentialWorkflow, swarm and hierarchical templates for common patterns.
- Utilities: logging, state management, caching and retry helpers.
- Config-driven: `config.yml` and the `arc_flow.config` helpers to centralize settings.

## Quick links

- Package entry: `arc_flow.__init__` exports the main classes (GraphOrchestrator, Supervisor, TeamBuilder, etc.).
- Orchestration: `arc_flow.core.orchestrator.GraphOrchestrator`
- Workflows: `arc_flow.workflows.SequentialWorkflow` and other workflow primitives.

## Installation

The project uses Python. Install dependencies from `requirements.txt` and install the package
in editable mode for development:

```bash
# create a virtualenv (recommended)
python -m venv .venv
source .venv/bin/activate

# install runtime dependencies
pip install -r requirements.txt

# install package in editable mode
pip install -e .
```

Alternatively, to install directly from sources for use in other projects:

```bash
pip install .
```

Note: the repository may rely on external LLM integrations (langchain/langgraph) — check `requirements.txt`
and your environment for any provider-specific setup (API keys, environment variables, etc.).

## Quickstart examples

1) Simple sequential workflow

```python
from arc_flow.workflows.sequential_workflow import SequentialWorkflow
from arc_flow.agents.react_agent import ReactAgent

# (Assume `llm` is a configured LLM client conforming to the project's expectations)
writer = ReactAgent(name="Writer", llm=llm)
workflow = SequentialWorkflow(name="simple", agents=[writer])
result = workflow.run("Write a short summary of multi-agent systems")
print(result['output'])
```

2) Build and compile a hierarchical graph

```python
from arc_flow.core.orchestrator import GraphOrchestrator
from arc_flow.core.supervisor import Supervisor
from arc_flow.agents.team_builder import TeamBuilder
from arc_flow.nodes.planner import PlannerNode
from arc_flow.nodes.generator import ResponseGeneratorNode

# create orchestrator
orch = GraphOrchestrator()

# create simple nodes / team objects (these are illustrative — adapt to your agent classes)
planner = PlannerNode()
generator = ResponseGeneratorNode()
supervisor = Supervisor()
team = TeamBuilder(name="researchers")

compiled = orch.build_hierarchical_graph(
		coordinator=None,
		planner=planner,
		supervisor=supervisor,
		teams=[team.build()],
		generator=generator
)

# `compiled` is a runnable graph object (see GraphOrchestrator.compile() for details)
```

## API overview (high level)

- GraphOrchestrator
	- add_node(name, node)
	- add_team(team)
	- set_supervisor(supervisor, name='supervisor')
	- add_edge(from_node, to_node)
	- build_hierarchical_graph(...)
	- compile()

- SequentialWorkflow
	- run(initial_input)
	- arun(initial_input)
	- add_agent(agent), insert_agent(agent, position), remove_agent(index)

See the docstrings in `arc_flow/core/orchestrator.py` and
`arc_flow/workflows/sequential_workflow.py` for runtime details and examples.

## Directory layout

- `arc_flow/` — main package
	- `agents/` — agent implementations and factories (TeamBuilder, AgentFactory, reactors)
	- `core/` — core abstractions (BaseAgent, BaseNode, Orchestrator, Supervisor, State)
	- `nodes/` — coordinator/planner/generator node implementations
	- `workflows/` — higher-level workflow patterns (sequential, swarm, hierarchical)
	- `config/` — configuration helpers and validation
	- `utils/` — logging, caching, retry helpers and common utilities

Other files:

- `config.yml` — example configuration for the framework
- `requirements.txt` — Python dependencies
- `setup.py` — package metadata and install hooks

## Configuration

Configuration is provided via `config.yml` and the `arc_flow.config` helpers. The
framework validates configuration at startup. Typical options include LLM provider
settings, checkpoint/persistence settings, logging levels, and orchestrator defaults
(max iterations, cycle detection, etc.).

## Development

To develop locally:

1. Create and activate a virtualenv (see Installation).
2. Install editable package and dev dependencies.
3. Run linters and tests (if present):

```bash
pip install -e .
# run tests if tests are added to the repo
pytest -q
```

If you add new agents or nodes, add unit tests that cover the public behavior
and include small integration tests for workflows or orchestrations.

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Open an issue describing the feature or bug.
2. Create focused pull requests with descriptive titles.
3. Add tests for new features and run the test suite locally.
4. Keep API changes minimal and document them in the README or docstrings.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

## Where to go next

- Read the docstrings in `arc_flow/core` and `arc_flow/workflows` for implementation details.
- Inspect `requirements.txt` to ensure you have required LLM integrations configured.
- Try the quickstart examples above and adapt them to your LLM client and agent classes.

If you'd like, I can also generate a minimal example script that demonstrates a full
end-to-end run (setup, simple mock agent, and a workflow invocation). Just tell me
which example you'd prefer (sequential or graph-based) and whether to mock or use a
real LLM client.
