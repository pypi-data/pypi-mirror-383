from __future__ import annotations
import _wlplan.data
import _wlplan.planning
import typing
__all__: list[str] = ['AOAGGenerator', 'Graph', 'GraphGenerator', 'ILGGenerator', 'NILGGenerator', 'PLOIGGenerator']
class AOAGGenerator(GraphGenerator):
    def __init__(self, domain: _wlplan.planning.Domain, differentiate_constant_objects: bool) -> None:
        ...
class Graph:
    """
    WLPlan graph object.
    
    Graphs have integer node colours and edge labels.
    
    Parameters
    ----------
        node_colours : list[int]
            List of node colours, where `node[i]` is the colour of node `i` indexed from 0.
    
        node_values : list[float], optional
            List of node values. Empty if not provided.
    
        node_names : list[str], optional
            List of node names, where `node_names[i]` is the name of node `i` indexed from 0.
    
        edges : list[list[tuple[int, int]]]
            List of labelled edges, where `edges[u] = [(r_1, v_1), ..., (r_k, v_k)]` represents edges from node `u` to nodes `v_1, ..., v_k` with labels `r_1, ..., r_k`, respectively. WLPlan graphs are directed so users must ensure that edges are undirected.
    
    Attributes
    ----------
        node_colours : list[int]
            List of node colours.
    
        node_values : list[float]
            List of node values. Empty if not provided.
    
        edges : list[list[tuple[int, int]]]
            List of labelled edges.
    
    Methods
    -------
        get_node_name(u: int) -> str
            Get the name of node `u`.
    
        dump() -> None
            Print the graph representation.
    """
    @typing.overload
    def __init__(self, node_colours: list[int], node_values: list[float], node_names: list[str], edges: list[list[tuple[int, int]]]) -> None:
        ...
    @typing.overload
    def __init__(self, node_colours: list[int], node_values: list[float], edges: list[list[tuple[int, int]]]) -> None:
        ...
    @typing.overload
    def __init__(self, node_colours: list[int], node_names: list[str], edges: list[list[tuple[int, int]]]) -> None:
        ...
    @typing.overload
    def __init__(self, node_colours: list[int], edges: list[list[tuple[int, int]]]) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def dump(self) -> None:
        ...
    def get_node_name(self, u: int) -> str:
        ...
    @property
    def edges(self) -> list[list[tuple[int, int]]]:
        ...
    @property
    def node_colours(self) -> list[int]:
        ...
    @property
    def node_values(self) -> list[float]:
        ...
class GraphGenerator:
    def get_n_features(self) -> int:
        ...
    def get_n_relations(self) -> int:
        ...
    def set_problem(self, problem: _wlplan.planning.Problem) -> None:
        ...
    @typing.overload
    def to_graph(self, state: _wlplan.planning.State) -> Graph:
        ...
    @typing.overload
    def to_graph(self, state: _wlplan.planning.State, actions: list[_wlplan.planning.Action]) -> Graph:
        ...
    def to_graphs(self, dataset: _wlplan.data.DomainDataset) -> list[Graph]:
        ...
class ILGGenerator(GraphGenerator):
    def __init__(self, domain: _wlplan.planning.Domain, differentiate_constant_objects: bool) -> None:
        ...
class NILGGenerator(ILGGenerator):
    def __init__(self, domain: _wlplan.planning.Domain, differentiate_constant_objects: bool) -> None:
        ...
class PLOIGGenerator(GraphGenerator):
    def __init__(self, domain: _wlplan.planning.Domain, differentiate_constant_objects: bool) -> None:
        ...
