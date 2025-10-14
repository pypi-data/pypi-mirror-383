"""Interruptible nodes for `pydantic_graph`.

The thinking behind an InterruptNode is that the graph run gets interrupted
when the graph reaches the node. The node itself hasn't run yet. Normally,
graph can't be paused until it reaches the End. But here, when interrupted,
the graph returns the partial result along with the node that interrupted
its run.

Naming.

Several options were considered for the name of the class:

- InterruptNode
- PauseNode
- HaltNode
- StopNode
- HandoffNode

Handoff was rejected because it's to obscure and limits the implied use case
to handing off the graph to another process. Pause was eventually rejected
because it's not an on-demand pause, but rather an internal interruption
caused by the graph reaching an InterruptNode. Plus, `interrupt` is a term
most of the computer science literature uses to describe a similar concept.

Halt and Stop were too strict, implying that a node like that is equivalent
to the End node.

Use cases.

There are two use cases I envision for this library. Most of the time, the
graph must be interrupted to obtain some new data, required for the further
processing. But it's completely unknown, when the data will be available.
Could be seconds, could be months, could be never. It is impractical to
keep the graph running and have it wait. The second use case is to simply
interrupt the run for no reason at all. Maybe as a mechanism akin to async
to allow other processes to do some work in the meantime and then resume
this graph from where it left off. No external data is needed here and we
simply transition to the next node after the interruption.

Implementation ideas.

- InterruptNode with return type hint.

  I began with a concept of 2 node types, where one is used to interrupt
  the graph and the other is what the graph resumes from. In that
  implementation, the InterruptNode was not allowed to have anything inside
  its `run` method, but had to declare a return type hint so that we could
  determine the next node to run. It was ugly and seemed redundant.

- InterruptNode with Unset fields.

  This implementation was a huge improvement in terms of code readability,
  clarity of intentions, and ease of use. The idea is that graph stops when
  it reaches an InterruptNode, but the node that returns the InterruptNode
  has a chance to partially populate it.

  Now, the question is, how can we add the missing external data that has
  become available after the interruption and add back to the node to resume
  the graph? The InterruptNode in this implementation is a perfectly normal
  BaseNode that can have many edges. So, when the graph resumes, we
  manually re-populate the InterruptNode with the missing data and tell the
  graph to resume its run from it. The graph executes the `run` method of the
  InterruptNode, where the next node is returned as in normal operation.

  In this implementaion, the InterruptNode is an envelope that gets returned
  partially populated when the graph is interrupted, and then enriched with
  the missing data when the graph resumes.

  The challenge here is that we can't leave the fields of the InterruptNode
  that are required to resume the graph empty. They need to have a default
  value. Otherwise, the previous node can't return the InterruptNode half
  populated.

  The solution I came up with is to assign a special constant called `UNSET`
  to any field that needs to be set from outside before resuming the graph.
  However, this turned out to be a bad idea, because the persistence layer
  wouldn't know how to serialize the `UNSET` value, since it has no encoder
  for it.

- InterruptNode does nothing. resume() accepts missing data.

  In this implementation, resume() has either a `data: dict[str, Any]`
  parameter or a `**kwargs: Any` parameter. When the graph encounters an
  InterruptNode, it finishes its run and returns. When we call `resume()`,
  the graph reads the type hints of the InterruptNode, identifies the one
  and only edge leading to the next node (in this scenario, InterruptNode
  can only have one edge), and then populates the next node with the data
  we pass to `resume()` and runs it to resume the graph run.

  This is ugly for multiple reasons:

  - No typing for the missing data that we use to initialize the next node.
    In fact, this alone is enough to reject this implementation completely.
  - Only one edge is allowed. This limits the use cases for interruptions.
  - The run() method of the InterruptNode is not allowed to run but must
    be defined correctly with an edge even though it doesn't return anything.

- Finally, annotate fields that are required on resume with typing.Annotated.

  This is the best implementation I came up with. The missing values are
  serialized to None. But when the graph resumes we can check the annotation
  metadata and raise an exception if the field is not set.

  Upsides:

  - InterruptNode behaves like a normal node. No need for developers to
    keep in mind that it's `run` method cannot run.
  - InterruptNode can have many edges and can contain real business logic.
  - Familiar to developers thanks to the widespread use of Annotated in
    FastAPI and Typer.
  - Strong typing.
  - Supported by out of the box serialization and default persistence layers.

  Downsides:

  - It's a bit verbose, forcing developers to annotate every required
    field as `name: Annotated[T | None, Required] = None`.
  - Having `None` as an actual value for the required field is not allowed.
    A required field with None value will be treated as unset.
"""

from __future__ import annotations as _annotations

from dataclasses import fields, is_dataclass
from typing import Annotated, Any, get_type_hints, get_origin, get_args

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = None

from pydantic_graph.nodes import (
    BaseNode,
    StateT,
    DepsT,
    NodeRunEndT,
)


__all__ = 'InterruptNode', 'Required'


class Required:
    """Annotate an optional field with default value of None as required.

    This will signal to `proceed()` that this field must be set outside
    of the graph before proceeding.
    """


class InterruptNode(BaseNode[StateT, DepsT, NodeRunEndT]):
    """Base class for interruption nodes.

    When the `proceed()` function runs the graph and reaches an
    `InterruptNode`, it returns `InterruptibleGraphRunResult` with the
    `next_node` that was supposed to run next.

    Resuming the graph after the interruption will execute the interrupt
    node's `run` method to determine the next node to run.

    Any fields that cannot be populated from the previous node and must be
    set manually before resuming the graph run must be annotated with
    `Required`:

    ```python
    class InterruptForData(InterruptNode[State]) -> ProcessData:
        name: str  # Will be populated by the previous node.
        age: Annotated[int | None, Required] = None  # Must be set manually.

        def run(self, ctx: GraphRunContext[State]) -> ProcessData:
            return ProcessData(name=self.name, age=self.age)
    ```

    The annotated fields will work with both dataclasses and Pydantic models.
    """

    def _missing_fields(self) -> list[str]:
        missing: list[str] = []

        if is_dataclass(self):
            type_hints = get_type_hints(self.__class__, include_extras=True)
            for f in fields(self):
                if (
                    _is_required(type_hints[f.name])
                    and getattr(self, f.name) is None
                ):
                    missing.append(f.name)

        elif BaseModel is not None and isinstance(self, BaseModel):
            type_hints = get_type_hints(self.__class__, include_extras=True)
            for name, _ in (
                self.__class__.model_fields.items()
                if hasattr(self.__class__, 'model_fields')
                else self.__fields__.items()
            ):
                if (
                    _is_required(type_hints[name])
                    and getattr(self, name) is None
                ):
                    missing.append(name)

        return missing


def _is_required(annotation: Any) -> bool:
    """Return True if the annotation is `Annotated[..., Required, ...]`."""
    if get_origin(annotation) is Annotated:
        return Required in get_args(annotation)[1:]
    return False
