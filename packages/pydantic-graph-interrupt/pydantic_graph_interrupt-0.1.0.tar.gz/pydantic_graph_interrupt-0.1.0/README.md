# pedantic-graph-interrupt

Run interruptible Pydantic Graphs that can be interrupted and resumed.

## Table of Contents

- [pedantic-graph-interrupt](#pedantic-graph-interrupt)
  - [Table of Contents](#table-of-contents)
  - [Use cases](#use-cases)
  - [Installation](#installation)
  - [Concepts](#concepts)
  - [Usage](#usage)
    - [Define graph with interrupt nodes](#define-graph-with-interrupt-nodes)
    - [Initialize persistence](#initialize-persistence)
    - [Start the graph](#start-the-graph)

## Use cases

* LLM AI chatbots implemented using [pydantic-ai] that need to obtain user
  input outside of the graph.
* Document processing workflows where an external approval or human
  involvement is required.
* Graphs that can run for a very long time, so their execution must be
  broken into smaller continuous chunks. Most often each chunk is executed
  in a background worker, when the graph is ready to resume its run.
* And more...

## Installation

```bash
pip install pydantic-graph-interrupt
```

## Concepts

* `InterruptNode` is a special node type that interrupts the graph execution.
* `proceed()` is an alternative to `graph.run()`. It can be used to both start
  the graph run from scratch or resume it after an interruption.

## Usage

### Define graph with interrupt nodes

```python
"""graph.py"""
from dataclasses import dataclass, field
from pydantic_graph import BaseNode, End, GraphRunContext
from pydantic_graph_interrupt import InterruptibleGraph, InterruptNode, Required

@dataclass
class MyState:
    user_name: str | None = None
    messages: list[str] = field(default_factory=list)

@dataclass
class Greet(BaseNode[MyState]):
    async def run(self, ctx: GraphRunContext[MyState]) -> "WaitForName":
        ctx.state.messages.append("Hello, what is your name?")
        return WaitForName()

@dataclass  # ↓ This is an interrupt node
class WaitForName(InterruptNode[MyState]):
    # ↓ This is a required field that must be provided to resume the graph
    user_name: Annotated[str | None, Required] = None

    async def run(self, ctx: GraphRunContext[MyState]) -> "Goodbye":
        ctx.state.user_name = self.user_name
        return Goodbye(user_name=self.user_name)

@dataclass
class Goodbye(BaseNode[MyState]):
    user_name: str

    async def run(self, ctx: GraphRunContext[MyState]) -> End:
        ctx.state.messages.append(f"Goodbye, {self.user_name}!")
        return End(ctx.state)

my_graph = InterruptibleGraph(nodes=[Greet, WaitForName, Goodbye])
```

### Initialize persistence

When you just start, you have to initialize the persistence. This defines
the starting node of the graph and sets correct types inside the persistence.

```python
"""steps.py"""
from pathlib import Path
from pydantic_graph.persistence.file import FileStatePersistence
from .graph import MyState, my_graph, Greet

async def start():
    persistence = FileStatePersistence(Path("offline_state.json"))
    state = MyState()
    await my_graph.initialize(Greet(), persistence=persistence, state=state)
```

### Start the graph

```python
"""main.py"""
from .steps import start
await start()
```

[State Persistence]: https://ai.pydantic.dev/graph/#state-persistence
[pydantic-ai]: https://ai.pydantic.dev/
