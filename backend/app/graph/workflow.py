from langgraph.graph import StateGraph

from .nodes import economist_node, historian_node, philosopher_node
from .state import CommentaryState

NODE_FUNCTIONS = {
    "historian": historian_node,
    "economist": economist_node,
    "philosopher": philosopher_node,
}


def build_commentary_graph(order: list[str]):
    builder = StateGraph(CommentaryState)

    for name in order:
        builder.add_node(name, NODE_FUNCTIONS[name])

    builder.add_edge("__start__", order[0])
    for i in range(len(order) - 1):
        builder.add_edge(order[i], order[i + 1])
    builder.add_edge(order[-1], "__end__")

    return builder.compile()
