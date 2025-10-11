"""
EngiX Algorithms Module
Provides basic algorithms for CSE engineers.
"""

def binary_search(arr, target):
    """
    Binary search on a sorted array.

    Parameters
    ----------
    arr : list
        Sorted list.
    target : int/float
        Element to search.

    Returns
    -------
    int
        Index if found, else -1.

    Example
    -------
    >>> binary_search([1,3,5,7], 5)
    2
    """
    low, high = 0, len(arr)-1
    while low <= high:
        mid = (low + high)//2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid+1
        else:
            high = mid-1
    return -1

def dijkstra(graph, start):
    """
    Dijkstra's shortest path algorithm.

    Parameters
    ----------
    graph : dict
        {node: [(neighbor, weight), ...]}
    start : node
        Starting node.

    Returns
    -------
    dict
        Shortest distance to each node.

    Example
    -------
    >>> graph = {'A':[('B',1),('C',4)], 'B':[('C',2),('D',5)], 'C':[('D',1)], 'D':[]}
    >>> dijkstra(graph,'A')
    {'A': 0, 'B': 1, 'C': 3, 'D': 4}
    """
    import heapq
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    queue = [(0,start)]
    while queue:
        d, node = heapq.heappop(queue)
        if d > dist[node]:
            continue
        for neighbor, weight in graph[node]:
            if dist[node] + weight < dist[neighbor]:
                dist[neighbor] = dist[node] + weight
                heapq.heappush(queue, (dist[neighbor], neighbor))
    return dist
