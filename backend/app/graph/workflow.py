from langgraph.graph import StateGraph

from .nodes import economist_node, historian_node, philosopher_node
from .state import CommentaryState

builder = StateGraph(CommentaryState)

builder.add_node("historian", historian_node)
builder.add_node("economist", economist_node)
builder.add_node("philosopher", philosopher_node)

builder.add_edge("__start__", "historian")
builder.add_edge("historian", "economist")
builder.add_edge("economist", "philosopher")
builder.add_edge("philosopher", "__end__")

commentary_graph = builder.compile()
