from __future__ import annotations
import _wlplan.planning
import typing
__all__: list[str] = ['DomainDataset', 'ProblemDataset']
class DomainDataset:
    """
    WLPlan dataset object.
    
    Datasets contain a domain and a list of problem states.
    
    Parameters
    ----------
        domain : Domain
            Domain object.
    
        data : list[ProblemDataset]
            List of problem states.
    """
    def __getstate__(self) -> tuple:
        ...
    def __init__(self, domain: _wlplan.planning.Domain, data: list[...]) -> None:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @property
    def data(self) -> list[...]:
        ...
    @property
    def domain(self) -> _wlplan.planning.Domain:
        ...
class ProblemDataset:
    """
    Stores a problem and training states for the problem.
    
    Upon initialisation, the problem and states are checked for consistency.
    
    Parameters
    ----------
        problem : Problem
            Problem object.
    
        states : list[State]
            List of training states.
    
        actions : list[list[Action]], optional
            List of actions for each state.
    """
    def __getstate__(self) -> tuple:
        ...
    @typing.overload
    def __init__(self, problem: _wlplan.planning.Problem, states: list[_wlplan.planning.State]) -> None:
        ...
    @typing.overload
    def __init__(self, problem: _wlplan.planning.Problem, states: list[_wlplan.planning.State], actions: list[list[_wlplan.planning.Action]]) -> None:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @property
    def actions(self) -> list[list[_wlplan.planning.Action]]:
        ...
    @property
    def problem(self) -> _wlplan.planning.Problem:
        ...
    @property
    def states(self) -> list[_wlplan.planning.State]:
        ...
