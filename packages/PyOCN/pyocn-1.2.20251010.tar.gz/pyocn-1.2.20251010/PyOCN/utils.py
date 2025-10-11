"""
Utility functions for working with OCNs.
"""

from __future__ import annotations
from itertools import product
from typing import Any, Literal, Callable, TYPE_CHECKING
from numbers import Number
import networkx as nx
import numpy as np
from tqdm import tqdm

if TYPE_CHECKING:
    from .ocn import OCN

_allowed_net_types = {"I", "H", "V", "T", "E"}

#TODO: add ability to move root?
def net_type_to_dag(net_type:Literal["I", "H", "V", "T", "E"], dims:tuple, pbar: bool = False) -> nx.DiGraph:
    """Create a predefined OCN initialization network as a NetworkX DiGraph.

    Parameters
    ----------
    net_type : {"I", "H", "V", "T", "E"}
        The type of network to create.
        Descriptions of allowed types:

        - "I":

          ::

              O--O--O--O--O
                    |
              O--O--O--O--O
                    |
              O--O--O--O--O
                    |
              O--O--X--O--O

        - "V":

          ::

              O  O  O  O  O
               \  \ | /  /
              O  O  O  O  O
               \  \ | /  /
              O  O  O  O  O
               \  \ | /  /
              O--O--X--O--O

        - "H":

          ::

              O  O  O  O
              |  |  | /
              O  O  O--O
              |  | /
              O  O--O--O
              | /
              X--O--O--O

        - "E": A network where every node on the edge of the grid is a root.

          ::

              X  X  X  X  X  X
                \  \    /  /
              X  O  O  O  O  X
                \  \    /  /
              X  O  O  O  O  X
  
              X  O  O  O  O  X
                /  /     \  \
              X  O  O  O  O  X
                /  /     \  \  
              X  X  X  X  X  X


        - "T": Not implemented yet.

    dims : tuple
        The network dimensions as ``(rows, cols)``. Both must be positive even integers.
    pbar : bool, default False
        If True, display a progress bar while constructing the graph.
    wrap : bool, default False
        If True, create the graph with periodic boundary conditions (toroidal).

    Returns
    -------
    networkx.DiGraph
        A directed acyclic graph representing a valid initial OCN configuration.

    Raises
    ------
    ValueError
        If ``net_type`` is invalid or ``dims`` are not two positive even integers.

    Notes
    -----
    The returned graph assigns each grid cell exactly one node with a ``pos``
    attribute equal to ``(row, col)``.
    """
    rows, cols = dims
    G = nx.DiGraph()
    pbar = tqdm(product(range(rows), range(cols)), total=rows*cols, disable=not pbar, desc="Creating DAG")
    match net_type:
        case "I":
            jroot = cols // 2
            for i, j in pbar:
                n = i*cols + j
                G.add_node(n, pos=(i, j))
                if j < jroot:
                    G.add_edge(n, n+1)
                elif j > jroot:
                    G.add_edge(n, n-1)
                elif i > 0:
                    G.add_edge(n, n - cols)

        case "V":
            jroot = cols // 2
            for i, j in pbar:
                n = i*cols + j
                G.add_node(n, pos=(i, j))
                if i > 0:
                    if j < jroot:
                        G.add_edge(n, n - cols + 1)
                    elif j > jroot:
                        G.add_edge(n, n - cols - 1)
                    else:
                        G.add_edge(n, n - cols)
                else:
                    if j < jroot:
                        G.add_edge(n, n + 1)
                    elif j > jroot:
                        G.add_edge(n, n - 1)
        case "H": # hip roof is like V, but flowing towards a corner.
            for i, j in pbar:
                n = i*cols + j
                G.add_node(n, pos=(i, j))
                if i == j and i > 0:  # main diagonal
                    G.add_edge(n, n - cols - 1)
                elif i > j:
                    G.add_edge(n, n - cols)
                elif j > i:
                    G.add_edge(n, n - 1)
        case "E":  #TODO: implement a better radial pattern
            half_rows = rows / 2
            half_cols = cols / 2
            for i, j in pbar:
                n = i*cols + j
                G.add_node(n, pos=(i, j))
                # ul quadrant: flow up and left
                if i < half_rows and j < half_cols and i > 0 and j > 0:
                    G.add_edge(n, n - cols - 1)
                # ur quadrant: flow up and right
                elif i < half_rows and j >= half_cols and i > 0 and j < cols - 1:
                    G.add_edge(n, n - cols + 1)
                # ll quadrant: flow down and left
                elif i >= half_rows and j < half_cols and j > 0 and i < rows - 1:
                    G.add_edge(n, n + cols - 1)
                # lr quadrant: flow down and right
                elif i >= half_rows and j >= half_cols and i < rows - 1 and j < cols - 1:
                    G.add_edge(n, n + cols + 1)
        case _:
            raise ValueError(f"Invalid net_type {net_type}. Must be one of {_allowed_net_types}.")
        
    return G

def simulated_annealing_schedule(
    dims: tuple[int, int],
    E0: float,
    constant_phase: float,
    n_iterations: int,
    cooling_rate: float,
) -> Callable[[int], float | np.ndarray]:
    """Create a simulated-annealing cooling schedule for OCN optimization.

    This returns a callable ``schedule(i)`` that returns the temperature at
    iteration ``i``. The schedule consists of a constant-temperature phase
    followed by an exponentially decaying phase.

    Parameters
    ----------
    dims : tuple[int, int]
        The dimensions of the grid as (rows, cols).
    E0 : float
        Initial energy value.
    constant_phase : float
        Fraction of iterations (``0 <= fraction <= 1``) during which the
        temperature remains constant at ``Energy[0]``.
    n_iterations : int
        Total number of optimization iterations.
    cooling_rate : float
        Positive decay rate controlling the exponential temperature decrease
        after the constant phase.

    Returns
    -------
    Callable[[int], float] | numpy.ndarray
        A function mapping an iteration index ``i`` to a temperature value. If
        vectorized evaluation is used, may return a NumPy array of temperatures.

    Notes
    -----
    The exponential phase follows the form

    .. math::

        T_i = E_0 \exp\left(-\frac{\text{cooling\_rate}\,(i - n_0)}{N}\right),

    where ``E0`` is the initial energy, ``n0`` is the number of iterations in
    the constant phase, and ``N = rows * cols``.
    """
    if (not isinstance(constant_phase, Number) or constant_phase < 0 or constant_phase > 1):
        raise ValueError(f"constant_phase must be a number between 0 and 1. Got {constant_phase}")
    if (not isinstance(n_iterations, int) or n_iterations <= 0):
        raise ValueError(f"n_iterations must be a positive integer. Got {n_iterations}")
    if not isinstance(cooling_rate, Number):
        raise ValueError(f"cooling_rate must be a number. Got {cooling_rate}")
    if not isinstance(E0, Number) or E0 <= 0:
        raise ValueError(f"E0 must be a positive number. Got {E0}")
    if not (isinstance(dims, tuple) and len(dims) == 2 and all(isinstance(d, int) and d > 0 for d in dims)):
        raise ValueError(f"dims must be a tuple of two positive integers. Got {dims}")
    
    n_constant = int(constant_phase * n_iterations)
    nnodes = dims[0] * dims[1]

    term1 = -cooling_rate / nnodes
    term2 = cooling_rate * n_constant / nnodes

    def schedule(i):
        i = np.asarray(i)
        return np.where(i < n_constant, E0, E0 * np.exp(term1*i + term2))

    return schedule

def unwrap_digraph(dag: nx.DiGraph, dims: tuple[int, int]) -> nx.DiGraph:
    """"unwrap" gridcell coordinate attributes in a directed acyclic graph to place connected
    nodes adjacent to each other, removing periodic boundary conditions.

    Parameters
    ----------
    dag : nx.DiGraph
        The input directed acyclic graph with periodic boundary conditions.
        Each node must have a 'pos' attribute indicating its (row, col) position.
    dims : tuple[int, int]
        The dimensions of the grid as (rows, cols). Both must be positive integers.

    Returns
    -------
    nx.DiGraph
        A new directed acyclic graph with unwrapped grid coordinates. May not be
        consistent with a grid structure.

    Raises
    ------
    ValueError
        If any node in the input graph lacks a 'pos' attribute or if the
        dimensions are not positive integers.

    Notes
    -----
    The function assumes that the input graph is a valid DAG and that the
    'pos' attributes are correctly assigned. The output graph will no longer
    span a toroidal topology and will no longer cover a dense grid of nodes.
    """
    new_dag = dag.copy()
    
    for _ in range(2):
        for n in nx.topological_sort(new_dag):

            pos = new_dag.nodes[n]['pos']
            r, c = pos
            succs = list(new_dag.successors(n))
            
            # check for row wrapping
            for s in succs:
                sr, _ = new_dag.nodes[s]['pos']
                dr = sr - r
                # if we detect wrapping, move all ancestors and self
                if dr > 1:  # wrapped downward
                    for anc in nx.ancestors(new_dag, n):
                        anc_r, anc_c = new_dag.nodes[anc]['pos']
                        new_dag.nodes[anc]['pos'] = (anc_r + dims[0], anc_c)
                    new_dag.nodes[n]['pos'] = (r + dims[0], c)
                    break
                elif dr < -1:  # wrapped upward
                    for anc in nx.ancestors(new_dag, n):
                        anc_r, anc_c = new_dag.nodes[anc]['pos']
                        new_dag.nodes[anc]['pos'] = (anc_r - dims[0], anc_c)
                    new_dag.nodes[n]['pos'] = (r - dims[0], c)
                    break
            # check for column wrapping
            for s in succs:
                _, sc = new_dag.nodes[s]['pos']
                dc = sc - c
                if dc > 1:  # wrapped rightward
                    for anc in nx.ancestors(new_dag, n):
                        anc_r, anc_c = new_dag.nodes[anc]['pos']
                        new_dag.nodes[anc]['pos'] = (anc_r, anc_c + dims[1])
                    new_dag.nodes[n]['pos'] = (r, c + dims[1])
                    break
                elif dc < -1:  # wrapped leftward
                    for anc in nx.ancestors(new_dag, n):
                        anc_r, anc_c = new_dag.nodes[anc]['pos']
                        new_dag.nodes[anc]['pos'] = (anc_r, anc_c - dims[1])
                    new_dag.nodes[n]['pos'] = (r, c - dims[1])
                    break
    # Adjust positions to be non-negative
    positions = np.array(list(nx.get_node_attributes(new_dag, 'pos').values()))
    row_off, col_off = positions.min(axis=0)
    for n in new_dag.nodes:
        r, c = new_dag.nodes[n]['pos']
        new_dag.nodes[n]['pos'] = (r - row_off, c - col_off)
    return new_dag

def assign_subwatersheds(dag: nx.DiGraph) -> None:
    """Assign a 'watershed_id' attribute to each node in the DAG. 
    The resulting watershed_ids will be of the highest order possible,
    meaning that ids are assigned based on watersheds that drain directly into the 
    root nodes of the graph. To assign ids to lower order watersheds, consider first
    partitioning the graph into smaller subgraphs using the `get_subwatersheds` function.

    Parameters
    ----------
    dag : nx.DiGraph
        The input directed acyclic graph. Each node must have a 'pos' attribute
        indicating its (row, col) position.

    Returns
    -------
    None
        The function modifies the input graph in place by adding a 'watershed_id'
        attribute to each node.

    Raises
    ------
    ValueError
        If any node in the input graph lacks a 'pos' attribute.

    Notes
    -----
    A subwatershed is defined as the set of nodes that drain to a common outlet,
    where an outlet is a node with out-degree zero. Each subwatershed is assigned
    a unique integer ID, starting from 0. Nodes that are outlets themselves are
    assigned a watershed ID of -1.
    """
    roots = [n for n, d in dag.out_degree() if d==0]
    subwatershed_outlets = [n for root in roots for n in dag.predecessors(root)]
    subwatersheds = list(set(nx.ancestors(dag, outlet)) | {outlet} for outlet in subwatershed_outlets)
    subwatersheds = [dag.subgraph(wshd) for wshd in subwatersheds]
    for i, wshd in enumerate(subwatersheds):
        nx.set_node_attributes(wshd, i + 1, 'watershed_id')
    for r in roots:
        nx.set_node_attributes(dag, {r: -1}, 'watershed_id')

def get_subwatersheds(dag : nx.DiGraph, node : Any) -> set[nx.DiGraph]:
    """Extract subwatershed subgraphs from the main DAG. Each subwatershed drains to a common outlet node `node`.
    Node `node` is not included in the returned subwatershed graphs.

    Parameters
    ----------
    dag : nx.DiGraph
        The input directed acyclic graph. Each node must have a 'pos' attribute
        indicating its (row, col) position.
    node : Any
        A node in the graph representing the outlet of a subwatershed.

    Returns
    -------
    set of nx.DiGraph
        A set of directed acyclic graphs, each representing a subwatershed.

    Note
    ----
    The returned subwatersheds are subgraph views of the input graph and share node
    and edge data with the original graph. Unless copied, any changes to node or edge attributes
    in the subwatersheds will affect the original graph.
    """
    subwatershed_outlets = [n for n in dag.predecessors(node)]
    subwatersheds = set(set(nx.ancestors(dag, outlet)) | {outlet} for outlet in subwatershed_outlets)
    subwatersheds = set(dag.subgraph(wshd) for wshd in subwatersheds)
    return subwatersheds
    