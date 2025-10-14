import inspect
from contextlib import ExitStack
from dataclasses import dataclass
from typing import overload, Sequence

import logfire_api
from pydantic_graph import (
    Graph,
    End,
    BaseNode,
    GraphRun,
    GraphRunResult,
    exceptions,
    _utils,
)
from pydantic_graph.nodes import StateT, DepsT, RunEndT
from pydantic_graph.persistence import BaseStatePersistence
from pydantic_graph.persistence.in_mem import SimpleStatePersistence

from .nodes import InterruptNode


__all__ = 'InterruptibleGraph', 'InterruptibleGraphRunResult'


@dataclass(init=False)
class InterruptibleGraphRunResult(GraphRunResult[StateT, RunEndT]):
    """The result of resuming an interruptible graph.

    This is a subclass of `GraphRunResult` that adds the `next_node`
    attribute. When the graph finishes its run and reaches an `End` node,
    the outcome is the same as a normal `GraphRunResult` and the `next_node`
    is empty.

    When the graph is interrupted by a `InterruptNode`, the `output` is empty
    and the `next_node` contains the node that has interrupted the run
    and will be executed next when the graph is resumed.

    The `next_node` and the `state` can be modified and passed back to
    the `proceed` method and will overwrite the values in the persistence
    in that case. The `proceed` method will then call the `run` method of the
    `next_node`.

    Attributes:
        state: The state of the graph at the end of the proceed attempt.
        next_node: The last node that was executed during the proceed attempt.
        persistence: The persistence implementation that was used for
        this graph run.
        output: The data returned by the :pyclass:`End` node if the graph
        has finished its run.
        is_interrupt: Whether the graph has been interrupted by an
        :class:`InterruptNode`.
        is_end: Whether the graph has reached an end node.
    """
    next_node: BaseNode[StateT, DepsT, RunEndT] | None

    def __init__(
        self,
        *,
        state: StateT,
        persistence: BaseStatePersistence[StateT, RunEndT],
        output: RunEndT | None = None,
        next_node: BaseNode[StateT, DepsT, RunEndT] | None = None,
        traceparent: str | None = None,
    ) -> None:
        super().__init__(
            output=output,
            state=state,
            persistence=persistence,
            traceparent=traceparent,
        )
        self.next_node = next_node

    @property
    def is_interrupt(self) -> bool:  # noqa: D401
        """Return ``True`` if the graph has been interrupted by an
        :class:`InterruptNode`."""

        return isinstance(self.next_node, InterruptNode)

    @property
    def is_end(self) -> bool:  # noqa: D401
        """Return ``True`` if the graph has reached an end node."""

        return self.next_node is None


class InterruptibleGraph(Graph[StateT, DepsT, RunEndT]):
    """Graph that interrupts its run when a `InterruptNode` is encountered
    and can be resumed from the same point.

    This is a subclass of `Graph` and can be used in the same way. It adds
    the `proceed` method which can be used to both start and continue the
    interruptible graph run.

    In `pydantic-graph`, a graph is a collection of nodes that can be run
    in sequence. The nodes define their outgoing edges — e.g. which nodes
    may be run next, and thereby the structure of the graph.
    """
    def __init__(
        self,
        *,
        nodes: Sequence[type[BaseNode[StateT, DepsT, RunEndT]]],
        name: str | None = None,
        state_type: type[StateT] | _utils.Unset = _utils.UNSET,
        run_end_type: type[RunEndT] | _utils.Unset = _utils.UNSET,
        auto_instrument: bool = True,
    ):
        """Create an interruptible graph from a sequence of nodes.

        Interruptible graph is a subclass of `Graph` that will interrupt its
        execution when an `InterruptNode` is encountered and can then
        be resumed from the same point.

        Args:
            nodes: The nodes which make up the graph, nodes need to be
                unique and all be generic in the same state type.
            name: Optional name for the graph, if not provided the name
                will be inferred from the calling frame on the first call
                to a graph method.
            state_type: The type of the state for the graph, this can
                generally be inferred from `nodes`.
            run_end_type: The type of the result of running the graph, this
                can generally be inferred from `nodes`.
            auto_instrument: Whether to create a span for the graph run and
                the execution of each node's run method.
        """
        super().__init__(
            nodes=nodes,
            name=name,
            state_type=state_type,
            run_end_type=run_end_type,
            auto_instrument=auto_instrument,
        )

    @overload
    async def proceed(
        self,
        *,
        persistence: BaseStatePersistence[StateT, RunEndT],
        from_node: BaseNode[StateT, DepsT, RunEndT] | InterruptNode[StateT, DepsT, RunEndT] | None = ...,  # noqa: D401
        state: StateT | None = ...,  # noqa: D401
        deps: DepsT | None = ...,  # noqa: D401
        infer_name: bool = ...,  # noqa: D401
    ) -> InterruptibleGraphRunResult[StateT, RunEndT]:
        ...

    @overload
    async def proceed(
        self,
        *,
        persistence: BaseStatePersistence[StateT, RunEndT] | None = ...,  # noqa: D401
        from_node: BaseNode[StateT, DepsT, RunEndT] | InterruptNode[StateT, DepsT, RunEndT] = ...,  # noqa: D401
        state: StateT | None = ...,  # noqa: D401
        deps: DepsT | None = ...,  # noqa: D401
        infer_name: bool = ...,  # noqa: D401
    ) -> InterruptibleGraphRunResult[StateT, RunEndT]:
        ...

    async def proceed(
        self,
        persistence: BaseStatePersistence[StateT, RunEndT] | None = None,
        from_node: BaseNode[StateT, DepsT, RunEndT] | InterruptNode[StateT, DepsT, RunEndT] | None = None,
        state: StateT | None = None,
        deps: DepsT | None = None,
        infer_name: bool = True,
    ) -> InterruptibleGraphRunResult[StateT, RunEndT]:
        """Run the graph from the start, from the last known state, or from a
        given node until it ends or reaches an `InterruptNode`.

        The `proceed` method can be used to both start and continue the
        interruptible graph run.

        Args:
            persistence: The state persistence interface to use.
            from_node: Node to proceed from. Overrides the node
                from the persistence snapshot.
            state: The state of the graph to proceed from. Overrides the
                state from the persistence snapshot.
            deps: The dependencies of the graph.
            infer_name: Whether to infer the graph name from the calling
                frame.

        If `persistence` is not provided, an in-memory persistence will be
        created. If provided persistence is not initialized, the `proceed` 
        method will automatically set graph types and create the first
        snapshot.

        If you are passing a `persistence` instance, there is no need to
        initialize it beforehand, the `proceed` method will do it for you.
        However, when the graph run is just starting, the `from_node` must
        be provided.

        When resuming the graph run from a persistence, the `from_node` and
        `state` arguments are optional, but will override the values from the
        persistence snapshot, if provided, and will be persisted.

        Returns:
            `InterruptibleGraphRunResult` with the result of the proceed attempt.
        """
        if infer_name and self.name is None:
            self._infer_name(inspect.currentframe())

        if persistence is None and from_node is None:
            raise exceptions.GraphRuntimeError('Either `persistence` or `from_node` must be provided.')

        # An iter() call does the same by creating an in-memory persistence
        # if persistence is not provided.
        if persistence is None:
            persistence = SimpleStatePersistence()

        # The Graph.initialiazie() method always sets the graph type and then
        # snapshots the state and the next node to run. We optimize this to
        # remove redundant snapshot calls. First, set types if they are not
        # already set.
        if persistence.should_set_types():
            persistence.set_graph_types(self)

        # Persistence now has correct types set. Two things can happen here:
        # 1. Persistence already has data, in which case load_next() will
        #    return a valid snapshot.
        # 2. Persistence has just been created, in which case load_next()
        #    will throw an exception (most likely, a ValidationError from
        #    TypeAdapter, for non-trivial persistence types) or will return
        #    None (for in-memory persistence).
        snapshot = None
        try:
            snapshot = await persistence.load_next()
        except Exception:
            pass

        if snapshot:
            start_node = from_node or snapshot.node
            state = state or snapshot.state
            start_node.set_snapshot_id(snapshot.id)
        else:
            # If persistence was uninitialized, the user must provide a
            # a node to start from.
            if from_node is None:
                raise exceptions.GraphRuntimeError('Cannot initialize persistence without `from_node`.')
            # If persistence has no data, that's ok, because the first call
            # to GraphRun.next() inside the iter() will snapshot it anyway.
            start_node = from_node

        # Validate that interruption node has been fully populated.
        if isinstance(start_node, InterruptNode):
            missing = start_node._missing_fields()
            if missing:
                raise exceptions.GraphRuntimeError(
                    "Cannot proceed from InterruptNode "
                    f"{start_node.__class__.__name__} because it has "
                    f"unpopulated required fields: {', '.join(missing)}"
                )

        async with self.iter(
            start_node=start_node,
            persistence=persistence,
            state=state,
            deps=deps,
        ) as graph_run:
            done = False
            while not done:
                # GraphRun.next() will automatically snapshot the next_node
                # into persistence if it isn't already there.
                next_node = await graph_run.next(graph_run.next_node)
                if isinstance(next_node, InterruptNode):
                    return InterruptibleGraphRunResult(
                        state=graph_run.state,
                        persistence=persistence,
                        next_node=next_node,
                        traceparent=graph_run._traceparent(required=False),
                    )
                elif isinstance(next_node, End):
                    done = True

        # Graph has reached an end node.
        result = graph_run.result
        assert result is not None, 'Complete graph run should have a result'
        return InterruptibleGraphRunResult(
            state=result.state,
            persistence=persistence,
            output=result.output,
            traceparent=graph_run._traceparent(required=False),
        )
