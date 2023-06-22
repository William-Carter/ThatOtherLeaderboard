from typing import Dict, List, Set
# Yoinked straight from chatgpt
def dfs(graph: Dict[str, List[str]], currentNode: str, targetNode: str, visited: Set[str]) -> bool:
    """
    Runs a depth first search on a given graph to see if a path between the starting node and target node exists
    Arguments:
        graph - the graph to search, given in the format {"vertex": ["adjacent vertex 1", "adjacent vertex 2"]}
        currentNode - the node from which to start
        targetNode - the target node
        visited - a set to store the visited nodes in
    """
    
    if currentNode == targetNode:
        return True

    visited.add(currentNode)
    
    for neighbor in graph[currentNode]:
        if neighbor not in visited:
            if dfs(graph, neighbor, targetNode, visited):
                return True
    return False



def search(graph: Dict[str, List[str]], startNode: str, targetNode: str) -> bool:
    """
    Runs a depth first search on a given graph to see if a path between the starting node and target node exists
    Arguments:
        graph - the graph to search, given in the format {"vertex": ["adjacent vertex 1", "adjacent vertex 2"]}
        startNode - the node from which to start
        targetNode - the target node
    """
    visited = set()
    return dfs(graph, startNode, targetNode, visited)