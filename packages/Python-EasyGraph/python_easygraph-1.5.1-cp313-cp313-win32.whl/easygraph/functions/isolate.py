"""
Functions for identifying isolate (degree zero) nodes.
"""

__all__ = ["is_isolate", "isolates", "number_of_isolates"]


def is_isolate(G, n):
    """Determines whether a node is an isolate.

    An *isolate* is a node with no neighbors (that is, with degree
    zero). For directed graphs, this means no in-neighbors and no
    out-neighbors.

    Parameters
    ----------
    G : EasyGraph graph

    n : node
        A node in `G`.

    Returns
    -------
    is_isolate : bool
       True if and only if `n` has no neighbors.

    Examples
    --------
    >>> G = eg.Graph()
    >>> G.add_edge(1, 2)
    >>> G.add_node(3)
    >>> eg.is_isolate(G, 2)
    False
    >>> eg.is_isolate(G, 3)
    True
    """
    return G.degree()[n] == 0


def isolates(G):
    """Iterator over isolates in the graph.

    An *isolate* is a node with no neighbors (that is, with degree
    zero). For directed graphs, this means no in-neighbors and no
    out-neighbors.

    Parameters
    ----------
    G : EasyGraph graph

    Returns
    -------
    iterator
        An iterator over the isolates of `G`.

    Examples
    --------
    To get a list of all isolates of a graph, use the :class:`list`
    constructor::

        >>> G = eg.Graph()
        >>> G.add_edge(1, 2)
        >>> G.add_node(3)
        >>> list(eg.isolates(G))
        [3]

    To remove all isolates in the graph, first create a list of the
    isolates, then use :meth:`Graph.remove_nodes_from`::

        >>> G.remove_nodes_from(list(eg.isolates(G)))
        >>> list(G)
        [1, 2]

    For digraphs, isolates have zero in-degree and zero out_degre::

        >>> G = eg.DiGraph([(0, 1), (1, 2)])
        >>> G.add_node(3)
        >>> list(eg.isolates(G))
        [3]

    """
    return (n for n, d in G.degree().items() if d == 0)


def number_of_isolates(G):
    """Returns the number of isolates in the graph.

    An *isolate* is a node with no neighbors (that is, with degree
    zero). For directed graphs, this means no in-neighbors and no
    out-neighbors.

    Parameters
    ----------
    G : EasyGraph graph

    Returns
    -------
    int
        The number of degree zero nodes in the graph `G`.

    """
    # TODO This can be parallelized.
    return sum(1 for v in isolates(G))
